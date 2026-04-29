from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import DailyHealthLogCreate, DailyHealthLogResponse, AllLogsResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.api.deps import get_db
from app.models import User, HealthMetric
from app.core import get_current_user
from datetime import date
from app.utils import get_user_today
from typing import Optional, Literal
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/daily-logs", 
    status_code=status.HTTP_201_CREATED, 
    response_model=DailyHealthLogResponse, 
    summary="Create or update today's health log (upsert)"
)
def create_or_update_daily_log(
    data: DailyHealthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DailyHealthLogResponse:
    """
    Create a new health log for today or update existing one.
    
    - Provide at least one metric (steps, sleep_hours, water_intake, or food_log)
    - Food log supports breakfast, lunch, dinner with multiple items
    """
    
    today = get_user_today(current_user.timezone)
    logger.debug(f"Upsert health log for user {current_user.email} on {today}")

    existing_log = db.query(HealthMetric).filter(HealthMetric.user_id == current_user.id, HealthMetric.log_date == today).first()

    try:
        if existing_log:
            update_data = data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key == "food_log":
                    existing_log.food_log = [
                        item.model_dump() if hasattr(item, "model_dump") else item 
                        for item in value
                    ] if value is not None else []
                else:
                    setattr(existing_log, key, value)

            db.commit()
            db.refresh(existing_log)
            
            logger.info(f"Health log updated for user {current_user.email} on {today}")
            
            return existing_log
        
        else:
            new_log = HealthMetric(
                user_id=current_user.id,
                log_date=today,
                steps=data.steps,
                sleep_hours=data.sleep_hours,
                water_intake=data.water_intake,
                food_log=(
                    [item.model_dump() for item in data.food_log]
                    if data.food_log is not None else []
                )
            )

            db.add(new_log)
            db.commit()
            db.refresh(new_log)
            
            logger.info(f"New health log created for user {current_user.email} on {today}")

            return new_log
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during health log upsert for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error. Please try again later."
        )
    
@router.get(
    "/daily-logs", 
    status_code=status.HTTP_200_OK, 
    response_model=AllLogsResponse, 
    summary="Get health logs with flexible filtering"
)
def get_health_logs(
    request_type: Literal["today", "all", "range"] = Query(
        "all", 
        description="Type of logs to fetch: 'today' for today's log, 'all' for paginated all logs, 'range' for date range"
    ),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD) - required for 'range' type"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD) - required for 'range' type"),
    
    page: int = Query(1, ge=1, description="Page number - used for 'all' and 'range' types"),
    limit: int = Query(20, ge=1, le=100, description="Number of logs per page - used for 'all' and 'range' types"),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AllLogsResponse:
    """
    Get health logs with flexible filtering options.
    
    - **today**: Get today's log only
    - **all**: Get all logs with pagination
    - **range**: Get logs within date range with pagination
    """
    
    # Handle "today" request type
    if request_type == "today":
        today = get_user_today(current_user.timezone)
        
        log = db.query(HealthMetric).filter(
            HealthMetric.user_id == current_user.id, 
            HealthMetric.log_date == today
        ).first()
        
        logger.debug(f"Today's log fetched for user: {current_user.email}")
                
        return AllLogsResponse(
            message="Today's log fetched successfully" if log else "No log created yet",
            logs=[log] if log else [],
            total=1 if log else 0
        )
    
    # Handle "range" request type
    elif request_type == "range":
        if start_date is None or end_date is None:
            logger.warning(f"Missing dates for range request: user={current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="start_date and end_date are required when request_type='range'"
            )
        
        if start_date > end_date:
            logger.warning(f"Invalid date range for user: {current_user.email}. start_date > end_date")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Start date cannot be after end date"
            )
            
        if (end_date - start_date).days > 366:
            logger.warning(f"Date range exceeded 1 year for user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Range exceeds 1 year. Please refine your search."
            )
        
        base_filter = [
            HealthMetric.user_id == current_user.id,
            HealthMetric.log_date >= start_date,
            HealthMetric.log_date <= end_date
        ]
        
        total_count = db.query(func.count(HealthMetric.id)).filter(*base_filter).scalar() or 0
        
        offset = (page - 1) * limit
        
        logs = db.query(HealthMetric).filter(*base_filter).order_by(
            HealthMetric.log_date.desc()
        ).offset(offset).limit(limit).all()
        
        logger.debug(f"Fetched {len(logs)} logs for range {start_date} to {end_date} for user: {current_user.email}")
        
        return AllLogsResponse(
            message=f"Fetched {len(logs)} logs from page {page} for range {start_date} to {end_date}" if logs 
                    else f"No health logs found between {start_date} and {end_date}",
            logs=logs,
            total=total_count
        )
    
    # Handle "all" request type (default)
    else:
        base_filter = [HealthMetric.user_id == current_user.id]
        
        total_count = db.query(func.count(HealthMetric.id)).filter(*base_filter).scalar() or 0
        
        offset = (page - 1) * limit
        
        logs = db.query(HealthMetric).filter(*base_filter).order_by(
            HealthMetric.log_date.desc()
        ).offset(offset).limit(limit).all()
        
        logger.debug(f"Fetched {len(logs)} of {total_count} total logs for user: {current_user.email} (page {page})")
        
        return AllLogsResponse(
            message=f"Successfully fetched {len(logs)} logs" if logs else "No health logs found for this user",
            logs=logs,
            total=total_count
        )
    
@router.patch(
    "/daily-logs/{log_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=DailyHealthLogResponse, 
    summary="Update or clear health metrics for a specific log"
)
def update_or_clear_metrics(
    log_id: int,
    data: DailyHealthLogCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DailyHealthLogResponse:
    """
    Update specific fields of a health log by ID.
    
    - Provide at least one metric to update (steps, sleep_hours, water_intake, or food_log)
    - Set a field to None to clear its value
    - Food log can be partially updated
    """
    
    log = db.query(HealthMetric).filter(HealthMetric.id == log_id, HealthMetric.user_id == current_user.id).first()

    if not log:
        logger.warning(f"Update failed - Log {log_id} not found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log entry with id {log_id} not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    
    if not update_data:
        logger.warning(f"Update failed - No data provided for log {log_id} by user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update. Please provide at least one field to update"
        )
        
    updated_fields = []

    for key, value in update_data.items():
        if key == "food_log":
            log.food_log = [
                item.model_dump() if hasattr(item, "model_dump") else item 
                for item in value
            ] if value is not None else []
            updated_fields.append(key)
            logger.debug(f"Updated {key} for log {log_id}")
        else:
            setattr(log, key, value)
            updated_fields.append(key)
            logger.debug(f"Updated {key}={value} for log {log_id}")

    try:
        db.commit()
        db.refresh(log)
        
        logger.info(f"Health log {log_id} updated successfully for user: {current_user.email} - Fields: {', '.join(updated_fields)}")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during update of log {log_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred while updating the log. Please try again."
        )

    return log  

@router.delete(
    "/daily-logs/today", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete today's health log"
)
def delete_today_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete today's health log for the authenticated user.
    
    - Only the log for current date (based on user's timezone) is deleted
    - This action cannot be undone
    """
    
    today = get_user_today(current_user.timezone)
    logger.debug(f"Attempting to delete today's log for user: {current_user.email} on {today}")

    log = db.query(HealthMetric).filter(HealthMetric.user_id == current_user.id, HealthMetric.log_date == today).first()
        
    if not log:
        logger.warning(f"Delete failed - No log found for today ({today}) for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No log found for today ({today})"
        )

    try:
        db.delete(log)
        db.commit()
        
        logger.info(f"Today's health log deleted successfully for user: {current_user.email} on {today}")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during deletion of today's log for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting the log. Please try again."
        )

    return None 

@router.delete(
    "/daily-logs/{log_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete a specific health log"
)
def delete_full_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a specific health log by its ID.
    
    - Only the owner of the log can delete it
    - This action cannot be undone
    - Useful for deleting past entries or incorrect data
    """
    
    logger.debug(f"Attempting to delete health log {log_id} for user: {current_user.email}")
    
    log = db.query(HealthMetric).filter(HealthMetric.id == log_id, HealthMetric.user_id == current_user.id).first()

    if not log:
        logger.warning(f"Delete failed - Health log {log_id} not found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Health log with id {log_id} not found"
        )

    try:
        db.delete(log)
        db.commit()
        
        logger.info(f"Health log {log_id} (date: {log.log_date}) deleted successfully for user: {current_user.email}")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during deletion of health log {log_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred while deleting the log. Please try again."
        )
    
    return None