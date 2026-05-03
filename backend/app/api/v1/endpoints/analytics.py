from fastapi import APIRouter, status, Depends, Query
from app.api.deps import get_db
from app.core import get_current_user, HEALTH_TARGETS
from app.utils import (
    get_metric_aggregates, parse_metric_result, get_logger,
    calculate_lifestyle_score, calculate_physical_score, calculate_medical_score,
    determine_risk_level, generate_health_insights,
    calculate_daily_health_score, generate_recommendations
)
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, HealthMetric, Profile, Lifestyle, MedicalHistory
from app.schemas import (
    OverallSummaryResponse, InsightsResponse, CategoricalMetricSummary,
    TrendsResponse, TrendDataPoint, RecommendationsResponse,
    HealthStatusResponse
)
from typing import Optional
from datetime import date, timedelta

# Initialize logger for this module
logger = get_logger(__name__)
router = APIRouter()

@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=OverallSummaryResponse,
    summary="Fetch Aggregated Health Summary",
    description="Calculates statistical aggregates (avg, min, max, achievement) for all core health metrics over a specified date range."
)
def get_health_summary(
    start_date: Optional[date] = Query(None, description="Start date for filtering logs (inclusive)."),
    end_date: Optional[date] = Query(None, description="End date for filtering logs (inclusive)."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OverallSummaryResponse:
    """
    Analytics Root: Provides a quantitative breakdown of recorded health data.
    
    1. Filters logs based on the provided date range.
    2. Performs SQL-level aggregation for efficiency.
    3. Calculates categorical modes (e.g., most frequent sleep quality).
    """
    logger.info(f"Analytics: Summary requested for user {current_user.id} ({current_user.email})")
    
    # 1. Base Query with Date Filtering
    query = db.query(HealthMetric).filter(HealthMetric.user_id == current_user.id)
    if start_date: 
        query = query.filter(HealthMetric.log_date >= start_date)
    if end_date: 
        query = query.filter(HealthMetric.log_date <= end_date)

    # 2. Batch Aggregate Numerical Metrics
    # This uses SQLAlchemy func.avg/func.sum to avoid loading all logs into Python memory.
    result = query.with_entities(
        *get_metric_aggregates(HealthMetric.steps, "steps", HEALTH_TARGETS["steps"]),
        *get_metric_aggregates(HealthMetric.sleep_hours, "sleep", HEALTH_TARGETS["sleep"]),
        *get_metric_aggregates(HealthMetric.water_intake, "water", HEALTH_TARGETS["water"]),
        *get_metric_aggregates(HealthMetric.activity_minutes, "activity", HEALTH_TARGETS["activity"]),
        *get_metric_aggregates(HealthMetric.sedentary_minutes, "sedentary", HEALTH_TARGETS["sedentary"], False),
        *get_metric_aggregates(HealthMetric.nutrition_sugar, "sugar", HEALTH_TARGETS["sugar"], False),
        *get_metric_aggregates(HealthMetric.nutrition_fruits, "fruits", HEALTH_TARGETS["fruits"]),
    ).first()

    # 3. Categorical Analysis (Sleep Quality Mode)
    # Counts occurrences of each quality rating (Poor, Average, Good, Excellent).
    quality_counts = query.with_entities(HealthMetric.sleep_quality, func.count(HealthMetric.sleep_quality))\
                          .group_by(HealthMetric.sleep_quality).all()
    
    most_freq = None
    total_logs = 0
    if quality_counts:
        # Sort results to find the most frequent rating
        sorted_qualities = sorted(quality_counts, key=lambda x: x[1], reverse=True)
        most_freq = sorted_qualities[0][0]
        total_logs = sum(count for _, count in quality_counts)

    logger.debug(f"Analytics: Aggregated {total_logs} logs for user {current_user.id}")

    return OverallSummaryResponse(
        message="Overall health summary fetched successfully",
        steps=parse_metric_result(result, "steps", HEALTH_TARGETS["steps"]),
        sleep=parse_metric_result(result, "sleep", HEALTH_TARGETS["sleep"]),
        water=parse_metric_result(result, "water", HEALTH_TARGETS["water"]),
        activity=parse_metric_result(result, "activity", HEALTH_TARGETS["activity"]),
        sedentary=parse_metric_result(result, "sedentary", HEALTH_TARGETS["sedentary"]),
        sugar=parse_metric_result(result, "sugar", HEALTH_TARGETS["sugar"]),
        fruits=parse_metric_result(result, "fruits", HEALTH_TARGETS["fruits"]),
        sleep_quality=CategoricalMetricSummary(most_frequent=most_freq, recorded_days=total_logs)
    )

@router.get(
    "/insights",
    status_code=status.HTTP_200_OK,
    response_model=InsightsResponse,
    summary="Generate Context-Aware Insights",
    description="Performs a behavioral audit by correlating the last 7 days of logs with the user's medical and physical profile."
)
def get_health_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InsightsResponse:
    """
    Intelligence Module: Identifies behavioral patterns and risks.
    
    - Analyzes 7-day trailing data.
    - Factors in chronic conditions (Diabetes, BP) from MedicalHistory.
    - Evaluates physical profile goals (e.g., Weight Loss).
    """
    logger.info(f"Analytics: Generating severe insights for user {current_user.id}")
    
    # 1. Fetch 7-day Metric Aggregates
    seven_days_ago = date.today() - timedelta(days=7)
    metrics_result = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= seven_days_ago
    ).with_entities(
        *get_metric_aggregates(HealthMetric.steps, "steps", HEALTH_TARGETS["steps"]),
        *get_metric_aggregates(HealthMetric.sleep_hours, "sleep", HEALTH_TARGETS["sleep"]),
        *get_metric_aggregates(HealthMetric.water_intake, "water", HEALTH_TARGETS["water"]),
        *get_metric_aggregates(HealthMetric.activity_minutes, "activity", HEALTH_TARGETS["activity"]),
        *get_metric_aggregates(HealthMetric.sedentary_minutes, "sedentary", HEALTH_TARGETS["sedentary"], False),
        *get_metric_aggregates(HealthMetric.nutrition_sugar, "sugar", HEALTH_TARGETS["sugar"], False),
        *get_metric_aggregates(HealthMetric.nutrition_fruits, "fruits", HEALTH_TARGETS["fruits"]),
    ).first()
    
    # 2. Fetch Full User Context (Lifestyle, Profile, Medical)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    lifestyle = db.query(Lifestyle).filter(Lifestyle.user_id == current_user.id).first()
    history = db.query(MedicalHistory).filter(MedicalHistory.user_id == current_user.id).first()
    
    # 3. Process Behavioral Summaries
    summaries = {
        "steps": parse_metric_result(metrics_result, "steps", HEALTH_TARGETS["steps"]),
        "sleep": parse_metric_result(metrics_result, "sleep", HEALTH_TARGETS["sleep"]),
        "water": parse_metric_result(metrics_result, "water", HEALTH_TARGETS["water"]),
        "activity": parse_metric_result(metrics_result, "activity", HEALTH_TARGETS["activity"]),
        "sedentary": parse_metric_result(metrics_result, "sedentary", HEALTH_TARGETS["sedentary"]),
        "sugar": parse_metric_result(metrics_result, "sugar", HEALTH_TARGETS["sugar"]),
        "fruits": parse_metric_result(metrics_result, "fruits", HEALTH_TARGETS["fruits"])
    }
    
    # 4. Hybrid Scoring Logic (Averages daily scores over the week)
    logs = db.query(HealthMetric).filter(HealthMetric.user_id == current_user.id, HealthMetric.log_date >= seven_days_ago).all()
    l_score = calculate_lifestyle_score(lifestyle)
    p_score = calculate_physical_score(profile)
    m_score = calculate_medical_score(history)
    
    daily_scores = [calculate_daily_health_score(log, l_score, p_score, m_score, history) for log in logs]
    overall_score = sum(daily_scores) / len(daily_scores) if daily_scores else calculate_daily_health_score(None, l_score, p_score, m_score, history)
    
    # 5. Generate Qualitative Insights and Risk Category
    insights = generate_health_insights(summaries, lifestyle, profile, history)
    risk_level = determine_risk_level(overall_score)
    
    logger.info(f"Analytics: Insight generation complete for user {current_user.id}. Score: {overall_score:.2f}, Risk: {risk_level}")
    
    return InsightsResponse(
        health_score=round(overall_score, 2),
        risk_level=risk_level,
        insights=insights,
        summary_message="High-performance health assessment completed." if overall_score > 70 else "Health review complete."
    )

@router.get(
    "/trends",
    response_model=TrendsResponse,
    summary="Fetch Daily Score Trends",
    description="Returns a time-series of daily holistic health scores for charting."
)
def get_health_trends(
    start_date: Optional[date] = Query(None, description="Start date for trend data."),
    end_date: Optional[date] = Query(None, description="End date for trend data."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TrendsResponse:
    """
    Visualization Module: Calculates a unique health score for every day in the range.
    
    Default range: Last 30 days.
    """
    if not end_date: end_date = date.today()
    if not start_date: start_date = end_date - timedelta(days=30)
    
    logger.debug(f"Analytics: Trends requested for user {current_user.id} from {start_date} to {end_date}")
        
    # Fetch user context for baseline scores
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    lifestyle = db.query(Lifestyle).filter(Lifestyle.user_id == current_user.id).first()
    history = db.query(MedicalHistory).filter(MedicalHistory.user_id == current_user.id).first()
    
    l_score = calculate_lifestyle_score(lifestyle)
    p_score = calculate_physical_score(profile)
    m_score = calculate_medical_score(history)

    # Fetch daily logs
    logs = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ).order_by(HealthMetric.log_date.asc()).all()
    
    # Perform daily score calculations
    trend_data = [
        TrendDataPoint(log_date=log.log_date, health_score=calculate_daily_health_score(log, l_score, p_score, m_score, history))
        for log in logs
    ]

    return TrendsResponse(message="Trend analysis complete", data=trend_data)

@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get Personalized Coach Tasks",
    description="Digital Coach: Analyzes performance gaps to provide prioritized health recommendations."
)
def get_health_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RecommendationsResponse:
    """
    Coaching Module: Actionable next steps based on recent data.
    
    - Prioritizes medical risks (e.g., managing sugar for diabetics).
    - Addresses the lowest achievement rates across all health metrics.
    """
    logger.info(f"Analytics: Generating recommendations for user {current_user.id}")
    
    seven_days_ago = date.today() - timedelta(days=7)
    
    # Aggregate recent performance
    metrics_result = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= seven_days_ago
    ).with_entities(
        *get_metric_aggregates(HealthMetric.steps, "steps", HEALTH_TARGETS["steps"]),
        *get_metric_aggregates(HealthMetric.sleep_hours, "sleep", HEALTH_TARGETS["sleep"]),
        *get_metric_aggregates(HealthMetric.water_intake, "water", HEALTH_TARGETS["water"]),
        *get_metric_aggregates(HealthMetric.activity_minutes, "activity", HEALTH_TARGETS["activity"]),
        *get_metric_aggregates(HealthMetric.sedentary_minutes, "sedentary", HEALTH_TARGETS["sedentary"], False),
        *get_metric_aggregates(HealthMetric.nutrition_sugar, "sugar", HEALTH_TARGETS["sugar"], False),
        *get_metric_aggregates(HealthMetric.nutrition_fruits, "fruits", HEALTH_TARGETS["fruits"]),
    ).first()
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    lifestyle = db.query(Lifestyle).filter(Lifestyle.user_id == current_user.id).first()
    history = db.query(MedicalHistory).filter(MedicalHistory.user_id == current_user.id).first()
    
    summaries = {
        "steps": parse_metric_result(metrics_result, "steps", HEALTH_TARGETS["steps"]),
        "sleep": parse_metric_result(metrics_result, "sleep", HEALTH_TARGETS["sleep"]),
        "water": parse_metric_result(metrics_result, "water", HEALTH_TARGETS["water"]),
        "activity": parse_metric_result(metrics_result, "activity", HEALTH_TARGETS["activity"]),
        "sedentary": parse_metric_result(metrics_result, "sedentary", HEALTH_TARGETS["sedentary"]),
        "sugar": parse_metric_result(metrics_result, "sugar", HEALTH_TARGETS["sugar"]),
        "fruits": parse_metric_result(metrics_result, "fruits", HEALTH_TARGETS["fruits"])
    }
    
    recommendations = generate_recommendations(summaries, profile, lifestyle, history)
    
    logger.debug(f"Analytics: Generated {len(recommendations)} tasks for user {current_user.id}")
    
    return RecommendationsResponse(message="Coach tasks generated", recommendations=recommendations)

@router.get(
    "/status",
    response_model=HealthStatusResponse,
    summary="Fetch Dashboard Hero Data",
    description="Returns the all-time overall health score and risk level for the dashboard's main display."
)
def get_health_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthStatusResponse:
    """
    Dashboard Hub: Lightweight endpoint for the main score display.
    
    Calculates the average holistic score across every log entry ever recorded by the user.
    """
    logger.info(f"Analytics: Fetching dashboard hero status for user {current_user.id}")
    
    # 1. Load Full History Context
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    lifestyle = db.query(Lifestyle).filter(Lifestyle.user_id == current_user.id).first()
    history = db.query(MedicalHistory).filter(MedicalHistory.user_id == current_user.id).first()
    
    # 2. Compute Baseline Scores
    l_score = calculate_lifestyle_score(lifestyle)
    p_score = calculate_physical_score(profile)
    m_score = calculate_medical_score(history)
    
    # 3. Calculate All-Time Holistic Average
    logs = db.query(HealthMetric).filter(HealthMetric.user_id == current_user.id).all()
    
    daily_scores = [calculate_daily_health_score(log, l_score, p_score, m_score, history) for log in logs]
    overall_score = sum(daily_scores) / len(daily_scores) if daily_scores else calculate_daily_health_score(None, l_score, p_score, m_score, history)
    
    risk_level = determine_risk_level(overall_score)
    
    logger.info(f"Analytics: Status fetch complete. Current score: {overall_score:.2f}")
    
    return HealthStatusResponse(
        health_score=round(overall_score, 2),
        risk_level=risk_level,
        summary_message="Holistic health baseline established."
    )