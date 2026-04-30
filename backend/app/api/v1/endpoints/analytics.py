from fastapi import APIRouter, Query, Depends, status, HTTPException
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.api.deps import get_db
from app.models import User, HealthMetric
from app.core import (
    get_current_user, STEPS_GOAL_HIGH, 
    SLEEP_GOAL_HIGH, WATER_GOAL_HIGH,
    ACTIVITY_GOAL_HIGH, SEDENTARY_LIMIT_LOW,
    SUGAR_LIMIT_LOW, FRUITS_GOAL_HIGH
)
from app.schemas import MetricSummary, HealthSummaryResponse, Insight, HealthInsightsResponse, MetricTrend, HealthTrendsResponse, Recommendation, HealthRecommendationsResponse, HealthScorePoint, HealthScoreHistoryResponse
from app.utils import get_metric_scores, calculate_daily_health_score, get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=HealthSummaryResponse,
    summary="Get health summary for a date range",
)
def get_health_summary(
    start_date: date = Query(..., description="Start date for the summary period (YYYY-MM-DD format)"),
    end_date: date = Query(..., description="End date for the summary period (YYYY-MM-DD format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthSummaryResponse:
    """
    Generate health summary for authenticated user within date range.
    """
    
    if start_date > end_date:
        logger.warning(
            f"Invalid date range requested by user_id={current_user.id}: "
            f"start_date={start_date} > end_date={end_date}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    days_range = (end_date - start_date).days
    if days_range > 90:
        logger.warning(
            f"Date range exceeds limit for user_id={current_user.id}: "
            f"{days_range} days (max 90 days)"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary range cannot exceed 90 days. Please request a shorter period."
        )

    logger.debug(
        f"Generating health summary for user_id={current_user.id} "
        f"from {start_date} to {end_date} ({days_range + 1} days)"
    )

    base_filter = [
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ]

    # Metrics mapping for cleaner code
    metrics_query = db.query(
        func.avg(HealthMetric.steps), func.sum(HealthMetric.steps), func.max(HealthMetric.steps), func.min(HealthMetric.steps), func.count(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours), func.sum(HealthMetric.sleep_hours), func.max(HealthMetric.sleep_hours), func.min(HealthMetric.sleep_hours), func.count(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake), func.sum(HealthMetric.water_intake), func.max(HealthMetric.water_intake), func.min(HealthMetric.water_intake), func.count(HealthMetric.water_intake),
        func.avg(HealthMetric.activity_minutes), func.sum(HealthMetric.activity_minutes), func.max(HealthMetric.activity_minutes), func.min(HealthMetric.activity_minutes), func.count(HealthMetric.activity_minutes),
        func.avg(HealthMetric.sedentary_minutes), func.sum(HealthMetric.sedentary_minutes), func.max(HealthMetric.sedentary_minutes), func.min(HealthMetric.sedentary_minutes), func.count(HealthMetric.sedentary_minutes),
        func.avg(HealthMetric.nutrition_sugar), func.sum(HealthMetric.nutrition_sugar), func.max(HealthMetric.nutrition_sugar), func.min(HealthMetric.nutrition_sugar), func.count(HealthMetric.nutrition_sugar),
        func.avg(HealthMetric.nutrition_fruits), func.sum(HealthMetric.nutrition_fruits), func.max(HealthMetric.nutrition_fruits), func.min(HealthMetric.nutrition_fruits), func.count(HealthMetric.nutrition_fruits),
    ).filter(*base_filter).first()

    # Unpack the results (5 values per metric)
    s_avg, s_sum, s_max, s_min, s_days = metrics_query[0:5]
    sl_avg, sl_sum, sl_max, sl_min, sl_days = metrics_query[5:10]
    w_avg, w_sum, w_max, w_min, w_days = metrics_query[10:15]
    a_avg, a_sum, a_max, a_min, a_days = metrics_query[15:20]
    sed_avg, sed_sum, sed_max, sed_min, sed_days = metrics_query[20:25]
    sug_avg, sug_sum, sug_max, sug_min, sug_days = metrics_query[25:30]
    f_avg, f_sum, f_max, f_min, f_days = metrics_query[30:35]

    # Targets achieved (re-calculate or just use averages for simplicity in summary)
    def calc_achievement(metric_col, target, is_inverse=False):
        if is_inverse:
            achieved = db.query(func.count(HealthMetric.id)).filter(*base_filter, metric_col <= target).scalar() or 0
        else:
            achieved = db.query(func.count(HealthMetric.id)).filter(*base_filter, metric_col >= target).scalar() or 0
        return achieved

    steps_achieved = calc_achievement(HealthMetric.steps, STEPS_GOAL_HIGH)
    sleep_achieved = calc_achievement(HealthMetric.sleep_hours, SLEEP_GOAL_HIGH)
    water_achieved = calc_achievement(HealthMetric.water_intake, WATER_GOAL_HIGH)
    activity_achieved = calc_achievement(HealthMetric.activity_minutes, ACTIVITY_GOAL_HIGH)
    sedentary_achieved = calc_achievement(HealthMetric.sedentary_minutes, SEDENTARY_LIMIT_LOW, is_inverse=True)
    sugar_achieved = calc_achievement(HealthMetric.nutrition_sugar, SUGAR_LIMIT_LOW, is_inverse=True)
    fruits_achieved = calc_achievement(HealthMetric.nutrition_fruits, FRUITS_GOAL_HIGH)

    active_days = db.query(func.count(func.distinct(HealthMetric.log_date))).filter(*base_filter).scalar() or 0
    total_days = days_range + 1

    def make_summary(avg, total, mx, mn, days, target, achieved, round_to=1):
        return MetricSummary(
            average=round(avg, round_to) if avg is not None else None,
            total=round(total, round_to) if total is not None else None,
            max=mx,
            min=mn,
            days_recorded=days or 0,
            target=target,
            achievement_rate=round((achieved / days) * 100, 1) if days and days > 0 else None
        )

    return HealthSummaryResponse(
        period_start=start_date,
        period_end=end_date,
        total_days=total_days,
        active_days=active_days,
        steps=make_summary(s_avg, s_sum, s_max, s_min, s_days, STEPS_GOAL_HIGH, steps_achieved, 0),
        sleep=make_summary(sl_avg, sl_sum, sl_max, sl_min, sl_days, SLEEP_GOAL_HIGH, sleep_achieved, 1),
        water=make_summary(w_avg, w_sum, w_max, w_min, w_days, WATER_GOAL_HIGH, water_achieved, 1),
        activity=make_summary(a_avg, a_sum, a_max, a_min, a_days, ACTIVITY_GOAL_HIGH, activity_achieved, 0),
        sedentary=make_summary(sed_avg, sed_sum, sed_max, sed_min, sed_days, SEDENTARY_LIMIT_LOW, sedentary_achieved, 0),
        sugar=make_summary(sug_avg, sug_sum, sug_max, sug_min, sug_days, SUGAR_LIMIT_LOW, sugar_achieved, 1),
        fruits=make_summary(f_avg, f_sum, f_max, f_min, f_days, FRUITS_GOAL_HIGH, fruits_achieved, 0)
    )

@router.get(
    "/insights",
    status_code=status.HTTP_200_OK,
    response_model=HealthInsightsResponse,
    summary="Get health insights for a date range",
)
def get_health_insights(
    start_date: date = Query(..., description="Start date for the insights period (YYYY-MM-DD format)"),
    end_date: date = Query(..., description="End date for the insights period (YYYY-MM-DD format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthInsightsResponse:
    """
    Generate health insights for authenticated user within date range.
    """
    
    logger.debug(f"Generating insights for user_id={current_user.id} from {start_date} to {end_date}")
    
    if start_date > end_date:
        logger.warning(f"Invalid date range for user_id={current_user.id}: {start_date} > {end_date}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )
        
    days_range = (end_date - start_date).days
    if days_range > 90:
        logger.warning(f"Date range exceeds 90 days for user_id={current_user.id}: {days_range} days")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Range cannot exceed 90 days"
        )
        
    base_filter = [
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ]
    
    averages = db.query(
        func.avg(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake),
        func.avg(HealthMetric.activity_minutes),
        func.avg(HealthMetric.sedentary_minutes),
        func.avg(HealthMetric.nutrition_sugar),
        func.avg(HealthMetric.nutrition_fruits)
    ).filter(*base_filter).first()
    
    # We need a sample for sleep quality since it's a string (get most frequent or just latest)
    sleep_quality = db.query(HealthMetric.sleep_quality).filter(
        *base_filter, 
        HealthMetric.sleep_quality.isnot(None)
    ).order_by(HealthMetric.log_date.desc()).first()
    sleep_quality = sleep_quality[0] if sleep_quality else None

    s_avg, sl_avg, w_avg, a_avg, sed_avg, sug_avg, f_avg = averages
    
    logger.debug(f"Averages for insights: {averages}")
    
    metric_scores = get_metric_scores(
        steps=s_avg, sleep=sl_avg, water=w_avg, 
        activity=a_avg, sedentary=sed_avg, 
        sugar=sug_avg, fruits=f_avg
    )
    
    insights = []
    
    def add_insight(m_type, score, low_msg, warn_msg, good_msg):
        if score == 40:
            insights.append(Insight(type=m_type, message=low_msg, severity="critical"))
        elif score == 70:
            insights.append(Insight(type=m_type, message=warn_msg, severity="warning"))
        elif score == 100:
            insights.append(Insight(type=m_type, message=good_msg, severity="good"))

    add_insight("steps", metric_scores["steps"], 
                "Your activity level is low. Try to walk more daily.", 
                "You're close to your step goal. Keep pushing!", 
                "Excellent! You're consistently active.")

    add_insight("sleep", metric_scores["sleep"], 
                "You are not getting enough sleep.", 
                "Your sleep duration is okay but can be improved.", 
                "Great! You have a healthy sleep pattern.")

    add_insight("water", metric_scores["water"], 
                "You should drink more water daily.", 
                "Increase your water intake slightly.", 
                "Good hydration level maintained.")

    add_insight("activity", metric_scores["activity"], 
                "Very low physical activity detected.", 
                "Try to add more active minutes to your day.", 
                "Excellent daily activity levels!")

    add_insight("sedentary", metric_scores["sedentary"], 
                "You are sitting for too long. Move more!", 
                "Try to reduce your sedentary time.", 
                "Good balance between sitting and moving.")

    add_insight("sugar", metric_scores["sugar"], 
                "Your sugar intake is too high.", 
                "Try to reduce sweet snacks and drinks.", 
                "Great job keeping sugar intake low!")

    add_insight("fruits", metric_scores["fruits"], 
                "You should eat more fruits daily.", 
                "Almost there with your fruit intake goal.", 
                "Excellent variety of fruits in your diet!")

    overall_score = calculate_daily_health_score(
        steps=s_avg, sleep_hours=sl_avg, water_intake=w_avg,
        sleep_quality=sleep_quality, activity_minutes=a_avg,
        sedentary_minutes=sed_avg, nutrition_sugar=sug_avg,
        nutrition_fruits=f_avg
    ) or 0
    
    return HealthInsightsResponse(
        overall_score=overall_score,
        insights=insights
    )

@router.get(
    "/trends",
    status_code=status.HTTP_200_OK,
    response_model=HealthTrendsResponse,
    summary="Get health trends for a date range"
)
def get_health_trends(
    start_date: date = Query(..., description="Start date for the trend period (YYYY-MM-DD format)"),
    end_date: date = Query(..., description="End date for the trend period (YYYY-MM-DD format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthTrendsResponse:
    """
    Generate health trends for authenticated user within date range.
    """
    
    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")
        
    days = (end_date - start_date).days + 1
    if days > 90:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Range cannot exceed 90 days")
        
    current_filter = [HealthMetric.user_id == current_user.id, HealthMetric.log_date >= start_date, HealthMetric.log_date <= end_date]
    
    current_metrics = db.query(
        func.avg(HealthMetric.steps), func.avg(HealthMetric.sleep_hours), func.avg(HealthMetric.water_intake),
        func.avg(HealthMetric.activity_minutes), func.avg(HealthMetric.sedentary_minutes),
        func.avg(HealthMetric.nutrition_sugar), func.avg(HealthMetric.nutrition_fruits)
    ).filter(*current_filter).first()
    
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    prev_filter = [HealthMetric.user_id == current_user.id, HealthMetric.log_date >= prev_start, HealthMetric.log_date <= prev_end]
    
    prev_metrics = db.query(
        func.avg(HealthMetric.steps), func.avg(HealthMetric.sleep_hours), func.avg(HealthMetric.water_intake),
        func.avg(HealthMetric.activity_minutes), func.avg(HealthMetric.sedentary_minutes),
        func.avg(HealthMetric.nutrition_sugar), func.avg(HealthMetric.nutrition_fruits)
    ).filter(*prev_filter).first()
    
    def calc_change(curr, prev):
        if curr is None or prev is None or prev == 0: return None
        return round(((curr - prev) / prev) * 100, 1)

    def make_trend(curr, prev, round_to=1):
        return MetricTrend(
            current_avg=round(curr, round_to) if curr is not None else None,
            previous_avg=round(prev, round_to) if prev is not None else None,
            change_percent=calc_change(curr, prev)
        )

    return HealthTrendsResponse(
        steps=make_trend(current_metrics[0], prev_metrics[0], 0),
        sleep=make_trend(current_metrics[1], prev_metrics[1], 1),
        water=make_trend(current_metrics[2], prev_metrics[2], 1),
        activity=make_trend(current_metrics[3], prev_metrics[3], 0),
        sedentary=make_trend(current_metrics[4], prev_metrics[4], 0),
        sugar=make_trend(current_metrics[5], prev_metrics[5], 1),
        fruits=make_trend(current_metrics[6], prev_metrics[6], 0)
    )
    
@router.get(
    "/recommendations",
    status_code=status.HTTP_200_OK,
    response_model=HealthRecommendationsResponse,
    summary="Get health recommendations for a date range"
)
def get_health_recommendations(
    start_date: date = Query(..., description="Start date for the recommendation period (YYYY-MM-DD format)"),
    end_date: date = Query(..., description="End date for the recommendation period (YYYY-MM-DD format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthRecommendationsResponse:
    """Generate recommendations for authenticated user within date range."""
    
    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")
        
    base_filter = [HealthMetric.user_id == current_user.id, HealthMetric.log_date >= start_date, HealthMetric.log_date <= end_date]
    
    averages = db.query(
        func.avg(HealthMetric.steps), func.avg(HealthMetric.sleep_hours), func.avg(HealthMetric.water_intake),
        func.avg(HealthMetric.activity_minutes), func.avg(HealthMetric.sedentary_minutes),
        func.avg(HealthMetric.nutrition_sugar), func.avg(HealthMetric.nutrition_fruits)
    ).filter(*base_filter).first()
    
    s_avg, sl_avg, w_avg, a_avg, sed_avg, sug_avg, f_avg = averages
    recommendations = []
    
    # 1. Activity (Steps & Active Minutes)
    if s_avg is not None and s_avg < 6000:
        recommendations.append(Recommendation(type="steps", message="Try to increase your daily steps to at least 6,000.", priority="high"))
    if a_avg is not None and a_avg < 20:
        recommendations.append(Recommendation(type="activity", message="Aim for at least 20-30 minutes of physical activity daily.", priority="high"))
        
    # 2. Sleep
    if sl_avg is not None and sl_avg < 7:
        recommendations.append(Recommendation(type="sleep", message="Try to get at least 7-8 hours of sleep for better recovery.", priority="medium"))
        
    # 3. Hydration
    if w_avg is not None and w_avg < 2:
        recommendations.append(Recommendation(type="water", message="Your water intake is low. Aim for 2.5L+ daily.", priority="medium"))
        
    # 4. Sedentary Time
    if sed_avg is not None and sed_avg > 480:
        recommendations.append(Recommendation(type="sedentary", message="You spend a lot of time sitting. Try taking short walks every hour.", priority="medium"))
        
    # 5. Nutrition
    if sug_avg is not None and sug_avg > 50:
        recommendations.append(Recommendation(type="sugar", message="Your sugar intake is high. Try to limit processed sweets.", priority="high"))
    if f_avg is not None and f_avg < 2:
        recommendations.append(Recommendation(type="fruits", message="Add more fruits to your diet for essential vitamins.", priority="low"))
        
    return HealthRecommendationsResponse(recommendations=recommendations)
    
@router.get(
    "/score-history",
    response_model=HealthScoreHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get health score history"
)
def get_health_score_history(
    start_date: date = Query(..., description="Start date for the score history (YYYY-MM-DD format)"),
    end_date: date = Query(..., description="End date for the score history (YYYY-MM-DD format). Maximum 90 days range."),
    include_empty: bool = Query(False, description="Include days with no data (score=None)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthScoreHistoryResponse:
    """Generate daily health score history for authenticated user within date range."""
    
    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")
        
    logs = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ).all()

    log_dict = {log.log_date: log for log in logs}
    scores = []
    current_date = start_date

    while current_date <= end_date:
        log = log_dict.get(current_date)
        if not log:
            score = None  
        else:
            score = calculate_daily_health_score(
                steps=log.steps,
                sleep_hours=log.sleep_hours,
                water_intake=log.water_intake,
                sleep_quality=log.sleep_quality,
                activity_minutes=log.activity_minutes,
                sedentary_minutes=log.sedentary_minutes,
                nutrition_sugar=log.nutrition_sugar,
                nutrition_fruits=log.nutrition_fruits
            )

        scores.append(HealthScorePoint(date=current_date, score=score))
        current_date += timedelta(days=1)

    if not include_empty:
        scores = [s for s in scores if s.score is not None]

    return HealthScoreHistoryResponse(scores=scores)