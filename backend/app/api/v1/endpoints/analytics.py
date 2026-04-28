from fastapi import APIRouter, Query, Depends, status, HTTPException
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.api.deps import get_db
from app.models import User, HealthMetric
from app.core import get_current_user
from app.schemas import MetricSummary, HealthSummaryResponse, Insight, HealthInsightsResponse, MetricTrend, HealthTrendsResponse, Recommendation, HealthRecommendationsResponse, HealthScorePoint, HealthScoreHistoryResponse

router = APIRouter()
logger = logging.getLogger(__name__)

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

    logger.debug(f"Fetching steps metrics for user_id={current_user.id}")
    
    steps_avg, steps_total, steps_max, steps_min, steps_days = db.query(
        func.avg(HealthMetric.steps),
        func.sum(HealthMetric.steps),
        func.max(HealthMetric.steps),
        func.min(HealthMetric.steps),
        func.count(HealthMetric.steps)
    ).filter(*base_filter).first()

    steps_achieved = db.query(func.count(HealthMetric.id)).filter(
        *base_filter,
        HealthMetric.steps >= 10000
    ).scalar() or 0

    logger.debug(
        f"Steps data: {steps_days or 0} days recorded, "
        f"{steps_achieved} days achieved target of 10,000 steps"
    )

    logger.debug(f"Fetching sleep metrics for user_id={current_user.id}")
    
    sleep_avg, sleep_total, sleep_max, sleep_min, sleep_days = db.query(
        func.avg(HealthMetric.sleep_hours),
        func.sum(HealthMetric.sleep_hours),
        func.max(HealthMetric.sleep_hours),
        func.min(HealthMetric.sleep_hours),
        func.count(HealthMetric.sleep_hours)
    ).filter(*base_filter).first()

    sleep_achieved = db.query(func.count(HealthMetric.id)).filter(
        *base_filter,
        HealthMetric.sleep_hours >= 7.5
    ).scalar() or 0

    logger.debug(
        f"Sleep data: {sleep_days or 0} days recorded, "
        f"{sleep_achieved} days achieved target of 7.5 hours"
    )

    logger.debug(f"Fetching water intake metrics for user_id={current_user.id}")
    
    water_avg, water_total, water_max, water_min, water_days = db.query(
        func.avg(HealthMetric.water_intake),
        func.sum(HealthMetric.water_intake),
        func.max(HealthMetric.water_intake),
        func.min(HealthMetric.water_intake),
        func.count(HealthMetric.water_intake)
    ).filter(*base_filter).first()

    water_achieved = db.query(func.count(HealthMetric.id)).filter(
        *base_filter,
        HealthMetric.water_intake >= 2.7
    ).scalar() or 0

    logger.debug(
        f"Water data: {water_days or 0} days recorded, "
        f"{water_achieved} days achieved target of 2.7L"
    )

    active_days = db.query(
        func.count(func.distinct(HealthMetric.log_date))
    ).filter(
        *base_filter,
        or_(
            HealthMetric.steps.isnot(None),
            HealthMetric.sleep_hours.isnot(None),
            HealthMetric.water_intake.isnot(None)
        )
    ).scalar() or 0

    total_days = days_range + 1
    
    logger.info(
        f"Health summary generated for user_id={current_user.id}: "
        f"{active_days}/{total_days} active days "
        f"(Steps: {steps_days or 0}, Sleep: {sleep_days or 0}, Water: {water_days or 0})"
    )
    
    steps_summary = MetricSummary(
        average=round(steps_avg, 2) if steps_avg is not None else None,
        total=steps_total,
        max=steps_max,
        min=steps_min,
        days_recorded=steps_days or 0,
        target=10000,
        achievement_rate=round((steps_achieved / steps_days) * 100, 1) if steps_days and steps_days > 0 else None
    )

    sleep_summary = MetricSummary(
        average=round(sleep_avg, 1) if sleep_avg is not None else None,
        total=round(sleep_total, 1) if sleep_total is not None else None,
        max=sleep_max,
        min=sleep_min,
        days_recorded=sleep_days or 0,
        target=7.5,
        achievement_rate=round((sleep_achieved / sleep_days) * 100, 1) if sleep_days and sleep_days > 0 else None
    )

    water_summary = MetricSummary(
        average=round(water_avg, 1) if water_avg is not None else None,
        total=round(water_total, 1) if water_total is not None else None,
        max=water_max,
        min=water_min,
        days_recorded=water_days or 0,
        target=2.7,
        achievement_rate=round((water_achieved / water_days) * 100, 1) if water_days and water_days > 0 else None
    )

    return HealthSummaryResponse(
        period_start=start_date,
        period_end=end_date,
        total_days=total_days,
        active_days=active_days,
        steps=steps_summary,
        sleep=sleep_summary,
        water=water_summary
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
    
    steps_avg, sleep_avg, water_avg = db.query(
        func.avg(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake)
    ).filter(*base_filter).first()
    
    logger.debug(
        f"Averages for user_id={current_user.id}: "
        f"Steps={steps_avg}, Sleep={sleep_avg}, Water={water_avg}"
    )
    
    insights = []
    
    # steps
    if steps_avg is None:
        insights.append(Insight(
            type="steps",
            message="No step data available. Start tracking your steps.",
            severity="warning"
        ))
        steps_score = 50
        
    elif steps_avg < 5000:
        insights.append(Insight(
            type="steps",
            message="Your activity level is low. Try to walk more daily.",
            severity="critical"
        ))
        steps_score = 40
        
    elif steps_avg < 10000:
        insights.append(Insight(
            type="steps",
            message="You're close to your step goal. Keep pushing!",
            severity="warning"
        ))
        steps_score = 70
        
    else:
        insights.append(Insight(
            type="steps",
            message="Excellent! You're consistently active.",
            severity="good"
        ))
        steps_score = 100
      
        
    # sleep
    if sleep_avg is None:
        insights.append(Insight(
            type="sleep",
            message="No sleep data available. Start tracking your sleep.",
            severity="warning"
        ))
        sleep_score = 50
        
    elif sleep_avg < 6:
        insights.append(Insight(
            type="sleep",
            message="You are not getting enough sleep.",
            severity="critical"
        ))
        sleep_score = 40
        
    elif sleep_avg < 7.5:
        insights.append(Insight(
            type="sleep",
            message="Your sleep is okay but can be improved.",
            severity="warning"
        ))
        sleep_score = 70
        
    else:
        insights.append(Insight(
            type="sleep",
            message="Great! You have a healthy sleep pattern.",
            severity="good"
        ))
        sleep_score = 100
        
        
    # water
    if water_avg is None:
        insights.append(Insight(
            type="water",
            message="No water intake data available.",
            severity="warning"
        ))
        water_score = 50
        
    elif water_avg < 2:
        insights.append(Insight(
            type="water",
            message="You should drink more water daily.",
            severity="critical"
        ))
        water_score = 40
        
    elif water_avg < 2.7:
        insights.append(Insight(
            type="water",
            message="Increase your water intake slightly.",
            severity="warning"
        ))
        water_score = 70
        
    else:
        insights.append(Insight(
            type="water",
            message="Good hydration level maintained.",
            severity="good"
        ))
        water_score = 100
   
        
    overall_score = int(
        (steps_score * 0.4) +
        (sleep_score * 0.3) +
        (water_score * 0.3)
    )
    
    overall_score = max(0, min(100, overall_score))
    
    logger.info(
        f"Insights generated for user_id={current_user.id}: "
        f"Score={overall_score}, Steps={steps_score}, Sleep={sleep_score}, Water={water_score}"
    )
    
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
    
    logger.debug(f"Generating trends for user_id={current_user.id} from {start_date} to {end_date}")
    
    if start_date > end_date:
        logger.warning(f"Invalid date range for user_id={current_user.id}: {start_date} > {end_date}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )
        
    days = (end_date - start_date).days + 1
    if days > 90:
        logger.warning(f"Date range exceeds 90 days for user_id={current_user.id}: {days} days")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Range cannot exceed 90 days"
        )
        
    logger.debug(f"Period length: {days} days")
        
    current_filter = [
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ]
    
    current_steps, current_sleep, current_water = db.query(
        func.avg(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake)
    ).filter(*current_filter).first()
    
    logger.debug(
        f"Current period averages for user_id={current_user.id}: "
        f"Steps={current_steps}, Sleep={current_sleep}, Water={current_water}"
    )
    
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    
    logger.debug(f"Previous period range: {prev_start} to {prev_end} ({days} days)")
    
    prev_filter = [
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= prev_start,
        HealthMetric.log_date <= prev_end
    ]
    
    prev_steps, prev_sleep, prev_water = db.query(
        func.avg(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake)
    ).filter(*prev_filter).first()
    
    logger.debug(
        f"Previous period averages for user_id={current_user.id}: "
        f"Steps={prev_steps}, Sleep={prev_sleep}, Water={prev_water}"
    )
    
    # utility function
    def calc_change(curr, prev):
        if curr is None or prev is None or prev == 0:
            return None
        change = round(((curr - prev) / prev) * 100, 1)
        logger.debug(f"Calculated change: {change}% (curr={curr}, prev={prev})")
        return change

    steps_trend = MetricTrend(
        current_avg=round(current_steps, 1) if current_steps else None,
        previous_avg=round(prev_steps, 1) if prev_steps else None,
        change_percent=calc_change(current_steps, prev_steps)
    )

    sleep_trend = MetricTrend(
        current_avg=round(current_sleep, 1) if current_sleep else None,
        previous_avg=round(prev_sleep, 1) if prev_sleep else None,
        change_percent=calc_change(current_sleep, prev_sleep)
    )

    water_trend = MetricTrend(
        current_avg=round(current_water, 1) if current_water else None,
        previous_avg=round(prev_water, 1) if prev_water else None,
        change_percent=calc_change(current_water, prev_water)
    )
    
    logger.info(
        f"Trends for user_id={current_user.id}: "
        f"Steps={steps_trend.change_percent}%, "
        f"Sleep={sleep_trend.change_percent}%, "
        f"Water={water_trend.change_percent}%"
    )
    
    return HealthTrendsResponse(
        steps=steps_trend,
        sleep=sleep_trend,
        water=water_trend
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
    """
    Generate recommendations for authenticated user within date range.
    """
    
    logger.debug(f"Request received: user_id={current_user.id}, start={start_date}, end={end_date}")
    
    if start_date > end_date:
        logger.warning(f"Invalid date range: user_id={current_user.id}, start={start_date}, end={end_date}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )
    
    days_range = (end_date - start_date).days
    if days_range > 90:
        logger.warning(f"Date range too large: user_id={current_user.id}, days={days_range}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Range cannot exceed 90 days"
        )
        
    base_filter = [
        HealthMetric.user_id == current_user.id,
        HealthMetric.log_date >= start_date,
        HealthMetric.log_date <= end_date
    ]
    
    steps_avg, sleep_avg, water_avg = db.query(
        func.avg(HealthMetric.steps),
        func.avg(HealthMetric.sleep_hours),
        func.avg(HealthMetric.water_intake)
    ).filter(*base_filter).first()
    
    logger.debug(
        f"Averages fetched: user_id={current_user.id}, "
        f"steps_avg={steps_avg}, sleep_avg={sleep_avg}, water_avg={water_avg}"
    )
    
    recommendations = []
    
    # steps
    if steps_avg is None:
        recommendations.append(Recommendation(
            type="steps",
            message="Start tracking your daily steps to get personalized recommendations.",
            priority="medium"
        ))
        
    elif steps_avg < 6000:
        recommendations.append(Recommendation(
            type="steps",
            message="Increase your daily steps by at least 3,000 to improve activity level.",
            priority="high"
        ))
        
    elif steps_avg < 10000:
        recommendations.append(Recommendation(
            type="steps",
            message="You're close to your goal. Try adding 1,000–2,000 more steps daily.",
            priority="medium"
        ))
        
    else:
        recommendations.append(Recommendation(
            type="steps",
            message="Great job! Maintain your current activity level.",
            priority="low"
        ))
        
    # sleep
    if sleep_avg is None:
        recommendations.append(Recommendation(
            type="sleep",
            message="Start tracking your sleep to improve your health insights.",
            priority="medium"
        ))
        
    elif sleep_avg < 6:
        recommendations.append(Recommendation(
            type="sleep",
            message="Try to increase your sleep duration by at least 1–1.5 hours.",
            priority="high"
        ))
        
    elif sleep_avg < 7.5:
        recommendations.append(Recommendation(
            type="sleep",
            message="Improve your sleep routine to reach 7–8 hours.",
            priority="medium"
        ))
        
    else:
        recommendations.append(Recommendation(
            type="sleep",
            message="Your sleep pattern is good. Keep it consistent.",
            priority="low"
        ))
        
    # water
    if water_avg is None:
        recommendations.append(Recommendation(
            type="water",
            message="Start tracking your water intake daily.",
            priority="medium"
        ))
    elif water_avg < 2:
        recommendations.append(Recommendation(
            type="water",
            message="Increase your daily water intake by at least 1 liter.",
            priority="high"
        ))
    elif water_avg < 2.7:
        recommendations.append(Recommendation(
            type="water",
            message="Try to drink a bit more water to reach optimal hydration.",
            priority="medium"
        ))
    else:
        recommendations.append(Recommendation(
            type="water",
            message="You are well hydrated. Maintain this habit.",
            priority="low"
        ))
        
    logger.info(
        f"Recommendations generated: user_id={current_user.id}, "
        f"count={len(recommendations)}"
    )
        
    return HealthRecommendationsResponse(
        recommendations=recommendations
    )
    
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
    """
    Generate daily health score history for authenticated user within date range.
    """

    logger.debug(
        f"Score history request: user_id={current_user.id}, "
        f"start={start_date}, end={end_date}, include_empty={include_empty}"
    )

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
            if log.steps is not None:
                if log.steps >= 10000:
                    steps_score = 100
                elif log.steps >= 6000:
                    steps_score = 70
                else:
                    steps_score = 40
            else:
                steps_score = 0

            if log.sleep_hours is not None:
                if log.sleep_hours >= 7.5:
                    sleep_score = 100
                elif log.sleep_hours >= 6:
                    sleep_score = 70
                else:
                    sleep_score = 40
            else:
                sleep_score = 0

            if log.water_intake is not None:
                if log.water_intake >= 2.7:
                    water_score = 100
                elif log.water_intake >= 2:
                    water_score = 70
                else:
                    water_score = 40
            else:
                water_score = 0

            score = int(
                (steps_score * 0.4) +
                (sleep_score * 0.3) +
                (water_score * 0.3)
            )

        scores.append(HealthScorePoint(
            date=current_date,
            score=score
        ))

        current_date += timedelta(days=1)

    if not include_empty:
        scores = [s for s in scores if s.score is not None]

    logger.info(
        f"Score history generated: user_id={current_user.id}, "
        f"points={len(scores)}"
    )

    return HealthScoreHistoryResponse(scores=scores)