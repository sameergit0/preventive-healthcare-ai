from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import DailyHealthLogCreate, DailyHealthLogResponse, AllLogsResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.api.deps import get_db
from app.models import User, HealthMetric
from app.core import get_current_user
from datetime import date
from app.utils import get_user_today, get_logger
from typing import Literal, Optional

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/daily-logs", 
    status_code=status.HTTP_201_CREATED, 
    response_model=DailyHealthLogResponse, 
    summary="Daily Health Log (Upsert)",
    description="Creates a new health log for today or updates an existing one. If a log exists, provided fields are overwritten with the new data."
)
def create_or_update_daily_log(
    data: DailyHealthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DailyHealthLogResponse:
    """
    Log health metrics for the current day. 
    
    This endpoint uses **Upsert** logic:
    1. **Insert**: If no log exists for today (user's local time), a new record is created.
    2. **Update**: If a log already exists, any provided fields will **overwrite** the existing database values.
        
    **Frontend Note**: To add or remove a meal, manage the list on the frontend and send the final version of the list here.
    """
    
    today = get_user_today(current_user.timezone)
    logger.info(f"Upserting health log for user {current_user.email} on date {today}")

    # Explicitly check for existing log for this user and date
    existing_log = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id, 
        HealthMetric.log_date == today
    ).first()

    try:
        if existing_log:
            logger.info(f"Existing log found (ID: {existing_log.id}) for user {current_user.email} on {today}. Updating metrics.")
            
            # exclude_unset=True ensures we only iterate over fields the user actually sent
            update_data = data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                # OVERWRITE: The frontend manages the full list (adding/cutting).
                # We save exactly what the frontend sends.
                setattr(existing_log, key, value)

            db.commit()
            db.refresh(existing_log)
            return existing_log
        
        else:
            logger.info(f"No existing log for user {current_user.email} on {today}. Creating new entry.")
            new_log = HealthMetric(
                user_id=current_user.id,
                log_date=today,
                **data.model_dump()
            )

            db.add(new_log)
            db.commit()
            db.refresh(new_log)
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
    summary="Get Health Logs (Filtered)",
    description="Fetch health logs with support for today's data, specific date ranges, or full history with pagination."
)
def get_health_logs(
    request_type: Literal["today", "all", "range"] = Query(
        "all", 
        description="Fetch type: 'today' (just today), 'all' (paginated history), or 'range' (start/end required)."
    ),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD) for 'range' search."),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD) for 'range' search."),
    
    page: int = Query(1, ge=1, description="Pagination: Page number."),
    limit: int = Query(20, ge=1, le=100, description="Pagination: Items per page."),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AllLogsResponse:
    """
    Retrieve historical health logs with flexible filtering.
    
    - **Today**: Fetches only the log matching the user's current local date.
    - **All**: Returns all historical logs for the user, sorted newest to oldest.
    - **Range**: Filters logs between `start_date` and `end_date` (inclusive). Max range is 1 year.
    
    Pagination applies to **All** and **Range** request types.
    """
    
    logger.info(f"Health log retrieval requested: type={request_type}, user={current_user.email}")

    # 1. Today's Log Only
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
    
    # 2. Date Range Request
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
                detail="Search range exceeds 1 year limit. Please refine your search."
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
        
        logger.debug(f"Range search successful: {len(logs)} logs found for user {current_user.email}")
        
        return AllLogsResponse(
            message=f"Found {len(logs)} logs (Page {page})" if logs else "No logs found in this range.",
            logs=logs,
            total=total_count
        )
    
    # 3. All Logs Request (Default)
    else:
        base_filter = [HealthMetric.user_id == current_user.id]
        
        total_count = db.query(func.count(HealthMetric.id)).filter(*base_filter).scalar() or 0
        offset = (page - 1) * limit
        
        logs = db.query(HealthMetric).filter(*base_filter).order_by(
            HealthMetric.log_date.desc()
        ).offset(offset).limit(limit).all()
        
        logger.debug(f"History fetched for user {current_user.email}: {len(logs)} logs (Page {page})")
        
        return AllLogsResponse(
            message=f"Fetched {len(logs)} logs (Page {page})" if logs else "No history found.",
            logs=logs,
            total=total_count
        )
    
@router.patch(
    "/daily-logs/{log_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=DailyHealthLogResponse, 
    summary="Update or Clear Health Metrics",
    description="Update specific fields or clear them entirely. To clear a field, send its value as `null` (JSON) or `None` (Python)."
)
def update_or_clear_metrics(
    log_id: int,
    data: DailyHealthLogCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DailyHealthLogResponse:
    """
    Perform a precision update on a specific health log.
    
    **Behavior**:
    - **Overwrite**: Any field you provide will replace the existing value in the database.
    - **Clear Data**: To set a field to NULL (clear it), send the field with a `null` value.
    - **Meal Deletion**: To remove a meal, send the `food_log` list without that specific meal entry.
    
    Returns the fully updated log object.
    """
    
    # 1. Fetch existing log
    log = db.query(HealthMetric).filter(
        HealthMetric.id == log_id, 
        HealthMetric.user_id == current_user.id
    ).first()

    if not log:
        logger.warning(f"Update failed: Log {log_id} not found for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health log entry not found."
        )

    # 2. Extract update data
    # exclude_unset=True is vital: it allows us to detect when a user explicitly sends 'null'
    update_data = data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update. Please include at least one field."
        )
        
    # 3. Apply changes
    updated_fields = []
    for key, value in update_data.items():
        setattr(log, key, value)
        updated_fields.append(key)

    # 4. Persistence
    try:
        db.commit()
        db.refresh(log)
        logger.info(f"Log {log_id} updated for {current_user.email}. Fields: {', '.join(updated_fields)}")
        return log
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for log {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="System error occurred while saving updates."
        )

@router.delete(
    "/daily-logs/today", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete Today's Log",
    description="Removes the health log for the current local date. Use this for 'Reset Dashboard' functionality."
)
def delete_today_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Finds and deletes the health log for today (based on user's timezone).
    """
    today = get_user_today(current_user.timezone)
    logger.info(f"Requested deletion of today's log for {current_user.email} on {today}")

    log = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id, 
        HealthMetric.log_date == today
    ).first()
        
    if not log:
        logger.warning(f"Delete failed: No log found for {today} (user={current_user.email})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No health log exists for today ({today})."
        )

    try:
        db.delete(log)
        db.commit()
        logger.info(f"Today's log ({today}) deleted successfully for {current_user.email}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error during deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while deleting today's log."
        )

@router.delete(
    "/daily-logs/{log_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete Specific Log",
    description="Deletes a health log by its ID. Only allowed for the owner of the log."
)
def delete_full_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Deletes a historical health log entry. Useful for clearing incorrect data from past dates.
    """
    logger.info(f"Requested deletion of log {log_id} for {current_user.email}")
    
    log = db.query(HealthMetric).filter(
        HealthMetric.id == log_id, 
        HealthMetric.user_id == current_user.id
    ).first()

    if not log:
        logger.warning(f"Delete failed: Log {log_id} not found or access denied for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Health log not found."
        )

    try:
        log_date = log.log_date
        db.delete(log)
        db.commit()
        logger.info(f"Log {log_id} (Date: {log_date}) deleted successfully for {current_user.email}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for log {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="System error occurred while deleting the log."
        )
