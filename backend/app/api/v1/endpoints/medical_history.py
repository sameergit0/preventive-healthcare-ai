from fastapi import APIRouter, status, Depends, HTTPException
from app.utils import get_logger
from app.api.deps import get_db
from app.core import get_current_user
from app.schemas import MedicalHistoryCreate, MedicalHistoryResponse
from app.models import User, MedicalHistory
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MedicalHistoryResponse,
    summary="Create Medical History Profile",
    description="Store medical history for the user. Only one record per user is allowed."
)
def create_medical_history(
    data: MedicalHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MedicalHistoryResponse:
    """
    Creates a medical history record for the user.
    """
    logger.info(f"Medical history creation attempt for user: {current_user.email}")
    
    # 1. Prevent duplicate entries
    existing_history = db.query(MedicalHistory).filter(
        MedicalHistory.user_id == current_user.id
    ).first()

    if existing_history:
        logger.warning(f"Duplicate medical history attempt for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medical history data already exists for this user."
        )

    # 2. Create and persist the record
    new_history = MedicalHistory(
        user_id = current_user.id,
        **data.model_dump()
    )

    try:
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        logger.info(f"Medical history record created successfully for user {current_user.id}")
        return new_history

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to save medical history for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while saving medical history data."
        )

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=MedicalHistoryResponse,
    summary="Get Medical History Profile",
    description="Retrieve the medical history for the current authenticated user."
)
def get_medical_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MedicalHistoryResponse:
    """
    Fetch the user's medical history record.
    
    **Frontend Note**: If this returns **404 Not Found**, it means the user has 
    skipped the medical history setup. In this case, you should display 
    the 'Complete Medical History' button on the dashboard.
    """
    logger.info(f"Fetching medical history for {current_user.email}")
    
    history = db.query(MedicalHistory).filter(
        MedicalHistory.user_id == current_user.id
    ).first()

    if not history:
        logger.debug(f"No medical history record found for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history data not found."
        )

    return history

@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=MedicalHistoryResponse,
    summary="Update Medical History Profile",
    description="Update specific medical conditions for the user."
)
def update_medical_history(
    data: MedicalHistoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MedicalHistoryResponse:
    """
    Perform a partial update on the user's medical history.
    """
    logger.info(f"Medical history update attempt for user: {current_user.email}")

    history = db.query(MedicalHistory).filter(
        MedicalHistory.user_id == current_user.id
    ).first()

    if not history:
        logger.warning(f"Update failed: No medical history record for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history data not found."
        )

    # exclude_unset=True allows for partial updates
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(history, key, value)

    try:
        db.commit()
        db.refresh(history)
        logger.info(f"Medical history record updated for {current_user.email}")
        return history
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while updating medical history."
        )

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Medical History Profile",
    description="Permanently remove the user's medical history record."
)
def delete_medical_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete the medical history profile.
    """
    logger.info(f"Medical history deletion request for user: {current_user.email}")
    
    history = db.query(MedicalHistory).filter(
        MedicalHistory.user_id == current_user.id
    ).first()

    if not history:
        logger.warning(f"Delete failed: No medical history record for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history data not found."
        )

    try:
        db.delete(history)
        db.commit()
        logger.info(f"Medical history profile deleted successfully for {current_user.email}")
        return None
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while deleting medical history."
        )