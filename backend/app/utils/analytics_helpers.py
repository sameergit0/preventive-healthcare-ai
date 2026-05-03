from sqlalchemy import func, case
from app.schemas import MetricSummary, HealthInsight, Recommendation
from app.core import HEALTH_SCORE_WEIGHTS, BASELINE_SCORE_WEIGHTS, RISK_LEVELS, HEALTH_TARGETS
from typing import List, Any, Dict, Optional

def get_metric_aggregates(column: Any, prefix: str, target: float, is_positive: bool = True) -> List:
    """
    Generates a list of SQLAlchemy aggregation expressions for a given metric column.
    
    This helper centralizes the logic for calculating averages, mins, maxes, totals, 
    and achievement counts for any numerical health metric.
    
    Args:
        column (Any): The SQLAlchemy model column to aggregate (e.g., HealthMetric.steps).
        prefix (str): The label prefix for the aggregated fields (e.g., "steps").
        target (float): The daily goal/threshold used to determine if a day was "achieved".
        is_positive (bool): If True, 'achieved' means column >= target. If False, column <= target (e.g., for sugar).
        
    Returns:
        List: A list of SQLAlchemy 'label' expressions ready to be used in .with_entities().
    """
    # Define the achievement condition based on metric polarity
    condition = column >= target if is_positive else column <= target
    
    return [
        func.avg(column).label(f"{prefix}_avg"),
        func.min(column).label(f"{prefix}_min"),
        func.max(column).label(f"{prefix}_max"),
        func.sum(column).label(f"{prefix}_total"),
        func.count(column).label(f"{prefix}_days"),
        # Count days where the condition was met using a CASE statement
        func.sum(case((condition, 1), else_=0)).label(f"{prefix}_achieved"),
    ]

def parse_metric_result(result: Any, prefix: str, target: float) -> MetricSummary:
    """
    Maps raw database aggregation results (from get_metric_aggregates) into a structured MetricSummary.
    
    Handles null values safely and calculates the achievement rate as a percentage.
    
    Args:
        result (Any): The result object returned by a SQLAlchemy query.
        prefix (str): The prefix used when generating the labels.
        target (float): The daily goal/target for this metric.
        
    Returns:
        MetricSummary: A Pydantic model containing the processed statistics.
    """
    def to_float(val: Any) -> float:
        """Safely converts a value to a rounded float."""
        return round(float(val), 2) if val is not None else 0.0
    
    def calculate_rate(achieved: Any, total: Any) -> float:
        """Calculates the percentage of days where the target was met."""
        if not total or total == 0: return 0.0
        return round((float(achieved or 0) / total) * 100, 2)

    return MetricSummary(
        avg=to_float(getattr(result, f"{prefix}_avg")),
        min=to_float(getattr(result, f"{prefix}_min")),
        max=to_float(getattr(result, f"{prefix}_max")),
        total=to_float(getattr(result, f"{prefix}_total")),
        days_recorded=getattr(result, f"{prefix}_days") or 0,
        target=target,
        achievement_rate=calculate_rate(getattr(result, f"{prefix}_achieved"), getattr(result, f"{prefix}_days"))
    )

def calculate_lifestyle_score(lifestyle: Any) -> float:
    """
    Computes a 0-100 lifestyle score based on qualitative habits.
    
    Factors considered:
    - Stress Level (Inverted: lower stress = higher score)
    - Work-Life Balance (Direct: higher balance = higher score)
    - Tobacco Usage (Categorical: 'never' > 'occasionally/former' > 'daily')
    - Alcohol Frequency (Categorical: 'never' > 'rarely/sometimes' > 'frequently')
    
    Args:
        lifestyle (Lifestyle): The user's lifestyle profile record.
        
    Returns:
        float: A rounded score from 0 to 100. Defaults to 50 if no profile exists.
    """
    if not lifestyle: return 50.0
    
    score = 0.0
    factors = 0
    
    # 1. Stress Level (Value is 1-5, where 1 is best)
    if lifestyle.stress_level:
        score += (6 - lifestyle.stress_level) * 20 # 1=100, 5=20
        factors += 1
        
    # 2. Work-Life Balance (Value is 1-5, where 5 is best)
    if lifestyle.work_life_balance:
        score += lifestyle.work_life_balance * 20 # 5=100, 1=20
        factors += 1
        
    # 3. Tobacco Usage
    if lifestyle.tobacco_type == "never": score += 100
    elif lifestyle.tobacco_type in ["occasionally", "former"]: score += 70
    else: score += 30 # 'daily' or other
    factors += 1
    
    # 4. Alcohol Frequency
    if lifestyle.alcohol_freq == "never": score += 100
    elif lifestyle.alcohol_freq in ["rarely", "sometimes"]: score += 70
    else: score += 30 # 'frequently' or other
    factors += 1
    
    return round(score / factors, 2) if factors > 0 else 50.0

def calculate_physical_score(profile: Any) -> float:
    """
    Computes a 0-100 physical health score using BMI and Waist-to-Height Ratio (WtHR).
    
    WtHR is often considered a more accurate predictor of cardiovascular risk than BMI alone.
    
    Args:
        profile (Profile): The user's physical profile record.
        
    Returns:
        float: A rounded score from 0 to 100.
    """
    if not profile or not profile.weight or not profile.height: return 50.0
    
    score = 0.0
    factors = 0
    height_m = profile.height / 100
    bmi = profile.weight / (height_m * height_m)
    
    # 1. BMI Score (WHO Categories)
    if 18.5 <= bmi <= 24.9: score += 100 # Healthy
    elif 25.0 <= bmi <= 29.9: score += 70 # Overweight
    else: score += 40 # Underweight or Obese
    factors += 1
    
    # 2. Waist-to-Height Ratio (WtHR)
    if profile.waist_cm:
        wthr = profile.waist_cm / profile.height
        if wthr <= 0.5: score += 100 # Low risk
        elif wthr <= 0.6: score += 70 # Increased risk
        else: score += 40 # High risk
        factors += 1
        
    return round(score / factors, 2) if factors > 0 else 50.0

def calculate_medical_score(history: Any) -> float:
    """
    Computes a 0-100 medical risk score based on chronic conditions.
    
    Baseline is 100. Each diagnosed condition reduces the score by a fixed weight.
    
    Args:
        history (MedicalHistory): The user's medical history record.
        
    Returns:
        float: A score from 0 to 100 (never negative).
    """
    if not history: return 100.0
    
    score = 100.0
    if history.diabetes: score -= 15
    if history.bp: score -= 15
    if history.heart_disease: score -= 20
    if history.high_cholesterol: score -= 10
    if history.asthma: score -= 5
    
    return max(score, 0.0)

def get_sleep_quality_multiplier(quality: Optional[str]) -> float:
    """
    Maps categorical sleep quality to a numerical multiplier.
    
    Excellent duration with 'Poor' quality should result in a lower effective score.
    """
    multipliers = {"excellent": 1.0, "good": 0.85, "average": 0.7, "poor": 0.5}
    return multipliers.get(quality, 0.7)

def determine_risk_level(score: float) -> str:
    """
    Maps a numerical health score (0-100) to a qualitative risk level.
    """
    if score >= 80: return RISK_LEVELS["LOW"]
    if score >= 60: return RISK_LEVELS["MODERATE"]
    if score >= 40: return RISK_LEVELS["HIGH"]
    return RISK_LEVELS["CRITICAL"]

def calculate_daily_health_score(log: Any, lifestyle_score: float, physical_score: float, medical_score: float, history: Any = None) -> float:
    """
    The Core Analytics Engine: Computes a comprehensive 0-100 health score for a specific day.
    
    This function implements 'Context-Aware Scoring':
    1.  **Dynamic Weighting**: If a user has a condition (e.g., Diabetes), metrics like Sugar 
        receive higher weights in the daily average.
    2.  **Hybrid Modeling**: Combines point-in-time behavioral data (logs) with 
        long-term health data (Lifestyle, Physical Profile, Medical History).
    
    Calculation Logic:
    - Weighted Metric Score (50%): Average of daily achievement across 7 metrics.
    - Lifestyle Score (20%): Baseline habits.
    - Physical Score (15%): Body composition (BMI/WtHR).
    - Medical Score (15%): Chronic risk reduction.
    
    Args:
        log (HealthMetric): The daily log entry.
        lifestyle_score (float): Pre-calculated lifestyle score.
        physical_score (float): Pre-calculated physical score.
        medical_score (float): Pre-calculated medical score.
        history (MedicalHistory, optional): Used for dynamic weight adjustment.
        
    Returns:
        float: Final holistic health score for the day.
    """
    # Case: User hasn't logged anything for this day. 
    # Return a baseline based solely on their profiles.
    if not log:
        return round(
            (lifestyle_score * BASELINE_SCORE_WEIGHTS["lifestyle"]) + 
            (physical_score * BASELINE_SCORE_WEIGHTS["physical"]) + 
            (medical_score * BASELINE_SCORE_WEIGHTS["medical"]), 2
        )

    # 1. Determine Weights based on Medical Context
    # Default is equal weighting for all metrics.
    weights = {"steps": 1.0, "sleep": 1.0, "water": 1.0, "activity": 1.0, "sedentary": 1.0, "sugar": 1.0, "fruits": 1.0}
    
    if history:
        # Heavily penalize high sugar for diabetic users
        if history.diabetes: weights["sugar"] = 2.5
        # Prioritize activity and low sedentary time for cardiac/hypertensive users
        if history.bp or history.heart_disease:
            weights["activity"] = 1.5
            weights["sedentary"] = 1.5

    # Helper to calculate binary achievement (100 or 30 points)
    def metric_score(val, target, is_positive=True):
        if val is None: return 50 # Neutral if not logged
        achieved = val >= target if is_positive else val <= target
        return 100 if achieved else 30

    # 2. Compute Raw Scores for each Metric
    raw_scores = {
        "steps": metric_score(log.steps, HEALTH_TARGETS["steps"]),
        "sleep": metric_score(log.sleep_hours, HEALTH_TARGETS["sleep"]) * get_sleep_quality_multiplier(log.sleep_quality),
        "water": metric_score(log.water_intake, HEALTH_TARGETS["water"]),
        "activity": metric_score(log.activity_minutes, HEALTH_TARGETS["activity"]),
        "sedentary": metric_score(log.sedentary_minutes, HEALTH_TARGETS["sedentary"], False),
        "sugar": metric_score(log.nutrition_sugar, HEALTH_TARGETS["sugar"], False),
        "fruits": metric_score(log.nutrition_fruits, HEALTH_TARGETS["fruits"])
    }

    # 3. Calculate Weighted Average of Metrics
    total_weight = sum(weights.values())
    weighted_metric_score = sum(raw_scores[k] * weights[k] for k in raw_scores) / total_weight

    # 4. Final Aggregation (Hybrid Model)
    overall = (
        (weighted_metric_score * HEALTH_SCORE_WEIGHTS["metrics"]) + 
        (lifestyle_score * HEALTH_SCORE_WEIGHTS["lifestyle"]) + 
        (physical_score * HEALTH_SCORE_WEIGHTS["physical"]) + 
        (medical_score * HEALTH_SCORE_WEIGHTS["medical"])
    )
    return round(overall, 2)

def generate_health_insights(summaries: Dict[str, MetricSummary], lifestyle: Any, profile: Any, history: Any = None) -> List[HealthInsight]:
    """
    Generates personalized, medically-aware health insights.
    
    The engine looks for correlations between behavior (summaries) and 
    user context (history, profile).
    
    Args:
        summaries (Dict): Aggregated metric stats for the last 7 days.
        lifestyle (Lifestyle): Lifestyle profile.
        profile (Profile): Physical profile.
        history (MedicalHistory): Medical context.
        
    Returns:
        List[HealthInsight]: A list of prioritized insights.
    """
    insights = []
    
    def get_trend(summary: MetricSummary) -> str:
        """Simple trend detection based on achievement rate."""
        if summary.days_recorded < 2: return "stable"
        return "stable" if summary.achievement_rate >= 70 else "declining"

    # --- 1. Chronic Condition Insights ---
    if history:
        # Diabetes + High Sugar Correlation
        if history.diabetes and summaries.get("sugar"):
            if summaries["sugar"].avg > 25:
                insights.append(HealthInsight(
                    category="Medical Context",
                    message="Your sugar intake is above recommended levels for managing diabetes. Aim for <25g.",
                    priority="high",
                    trend=get_trend(summaries["sugar"])
                ))
        
        # BP/Heart + Sedentary Correlation
        if (history.bp or history.heart_disease) and summaries.get("sedentary"):
            if summaries["sedentary"].avg > 480:
                insights.append(HealthInsight(
                    category="Heart Health",
                    message="High sedentary time increases cardiac risk. Try standing up every 30 minutes.",
                    priority="high",
                    trend=get_trend(summaries["sedentary"])
                ))

    # --- 2. Lifestyle & Behavior Insights ---
    if summaries.get("sleep") and lifestyle:
        # Poor Sleep + High Screen Time Correlation
        if (summaries["sleep"].avg < 7.0) and (lifestyle.screen_time_hours and lifestyle.screen_time_hours > 5):
            insights.append(HealthInsight(
                category="Sleep Hygiene",
                message="Your high screen time may be preventing restful sleep. Try a digital detox before bed.",
                priority="medium",
                trend=get_trend(summaries["sleep"])
            ))

    # --- 3. Physical Goal Alignment ---
    if profile and profile.goal == "Weight Loss" and summaries.get("activity"):
        if summaries["activity"].avg < 30:
            insights.append(HealthInsight(
                category="Goal Alignment",
                message="Increasing your daily activity to 30+ minutes will accelerate your weight loss.",
                priority="medium",
                trend=get_trend(summaries["activity"])
            ))

    # Fallback if no specific insights are triggered
    if not insights:
        insights.append(HealthInsight(category="General", message="Keep logging to unlock deeper health correlations!", priority="low", trend="stable"))
        
    return insights

def generate_recommendations(summaries: Dict[str, MetricSummary], profile: Any, lifestyle: Any, history: Any = None) -> List[Recommendation]:
    """
    Digital Coach: Prioritizes and generates actionable tasks.
    
    This function implements a 'Medical-First' prioritization:
    1.  Critical conditions (Diabetes/BP) tasks always appear first.
    2.  Performance gaps (lowest achievement rates) are addressed next.
    
    Args:
        summaries (Dict): Last 7 days of behavioral data.
        profile: User profile.
        lifestyle: Lifestyle habits.
        history: Medical history.
        
    Returns:
        List[Recommendation]: List of prioritized tasks for the user.
    """
    recommendations = []
    
    # --- 1. Medical-Critical Recommendations ---
    if history:
        if history.diabetes and (summaries.get("sugar") and summaries["sugar"].achievement_rate < 70):
            recommendations.append(Recommendation(
                task="Avoid processed snacks and opt for high-fiber fruits today.",
                benefit="Helps stabilize blood glucose levels and prevents insulin spikes.",
                priority="high", category="Nutrition"
            ))
        if history.bp and (summaries.get("sedentary") and summaries["sedentary"].avg > 480):
            recommendations.append(Recommendation(
                task="Take a 5-minute movement break every hour.",
                benefit="Reduces pressure on your arteries and improves circulation.",
                priority="high", category="Activity"
            ))

    # --- 2. Gap-Based Recommendations ---
    # Sort metrics by lowest achievement rate to identify the biggest weaknesses
    low_performing = [(n, s) for n, s in summaries.items() if s.days_recorded > 0 and s.achievement_rate < 80]
    low_performing.sort(key=lambda x: x[1].achievement_rate)
    
    # Take the top 2 biggest gaps
    for name, s in low_performing[:2]:
        if name == "steps":
            recommendations.append(Recommendation(
                task=f"Walk {int(HEALTH_TARGETS['steps'] - s.avg + 1000)} more steps today.",
                benefit="Strengthens your heart and helps manage weight.",
                priority="medium", category="Activity"
            ))
        elif name == "sleep":
            recommendations.append(Recommendation(
                task="Prioritize 8 hours of sleep by starting your bedtime routine earlier.",
                benefit="Boosts immune function and mental clarity.",
                priority="medium", category="Sleep"
            ))

    # Fallback
    if not recommendations:
        recommendations.append(Recommendation(task="Maintain your healthy streaks!", benefit="Consistency is key.", priority="low", category="General"))
        
    return recommendations
