from app.schemas import LifestyleCreate, LifestyleResponse
from app.models import User, Lifestyle
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.api.deps import get_db
from app.core import get_current_user
from app.utils import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=LifestyleResponse,
    summary="Create Lifestyle Profile",
    description="Store lifestyle habits for the user. Only one record per user is allowed."
)
def create_lifestyle(
    data: LifestyleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LifestyleResponse:
    """
    Submit lifestyle data. 
    
    If all fields are null (skipped), no database entry is generated.
    If data already exists, this will return a **409 Conflict**. 
    """
    logger.info(f"Lifestyle creation attempt for user: {current_user.email}")

    # Check for existing record (One-to-One enforcement)
    existing_lifestyle = db.query(Lifestyle).filter(
        Lifestyle.user_id == current_user.id
    ).first()

    if existing_lifestyle:
        logger.warning(f"Conflict: Lifestyle record already exists for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lifestyle data already exists. Use the UPDATE endpoint instead."
        )

    # 3. Create new record
    new_lifestyle = Lifestyle(
        user_id = current_user.id,
        **data.model_dump()
    )

    try:
        db.add(new_lifestyle)
        db.commit()
        db.refresh(new_lifestyle)
        logger.info(f"Lifestyle profile created successfully for {current_user.email}")
        return new_lifestyle

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while saving lifestyle data."
        )

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=LifestyleResponse,
    summary="Get Lifestyle Profile",
    description="Retrieve the lifestyle habits for the current authenticated user."
)
def get_lifestyle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LifestyleResponse:
    """
    Fetch the user's lifestyle record.
    
    **Frontend Note**: If this returns **404 Not Found**, it means the user has not 
    yet completed their lifestyle profile (likely skipped during signup). 
    In this case, you should display the 'Log Lifestyle' button on the dashboard.
    """
    logger.info(f"Fetching lifestyle record for {current_user.email}")
    
    lifestyle = db.query(Lifestyle).filter(
        Lifestyle.user_id == current_user.id
    ).first()

    if not lifestyle:
        logger.debug(f"No lifestyle record found for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lifestyle data not found."
        )

    return lifestyle

@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=LifestyleResponse,
    summary="Update Lifestyle Profile",
    description="Update specific habits or clear them entirely by sending `null`."
)
def update_lifestyle(
    data: LifestyleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LifestyleResponse:
    """
    Perform a partial update on the user's lifestyle habits.
    
    - **Partial Update**: Only include the fields you wish to change.
    - **Clear Field**: To clear a habit, send its value as `null`.
    """
    logger.info(f"Lifestyle update attempt for user: {current_user.email}")

    lifestyle = db.query(Lifestyle).filter(
        Lifestyle.user_id == current_user.id
    ).first()

    if not lifestyle:
        logger.warning(f"Update failed: No lifestyle record for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lifestyle data not found."
        )

    # exclude_unset=True allows detecting when the user explicitly sends 'null'
    update_data = data.model_dump(exclude_unset=True)
    updated_fields = []

    for key, value in update_data.items():
        setattr(lifestyle, key, value)
        updated_fields.append(key)

    try:
        db.commit()
        db.refresh(lifestyle)
        logger.info(f"Lifestyle record updated for {current_user.email}. Fields: {', '.join(updated_fields)}")
        return lifestyle
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while updating lifestyle habits."
        )

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Lifestyle Profile",
    description="Permantently remove the user's lifestyle habits record."
)
def delete_lifestyle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete the lifestyle profile. 
    
    This action cannot be undone. Once deleted, the dashboard will lose lifestyle-based 
    insights until a new profile is created.
    """
    logger.info(f"Lifestyle deletion request for user: {current_user.email}")
    
    lifestyle = db.query(Lifestyle).filter(
        Lifestyle.user_id == current_user.id
    ).first()

    if not lifestyle:
        logger.warning(f"Delete failed: No lifestyle record found for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lifestyle data not found."
        )

    try:
        db.delete(lifestyle)
        db.commit()
        logger.info(f"Lifestyle profile deleted successfully for {current_user.email}")
        return None
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Persistence error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System error occurred while deleting lifestyle habits."
        )
