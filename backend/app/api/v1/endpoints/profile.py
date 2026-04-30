from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from app.schemas import ProfileCreate, ProfileResponse, ProfileGetResponse, ProfileUpdate, ProfilePhotoResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.deps import get_db
from app.models import User, Profile
from app.core import get_current_user, IMAGE_EXT_MAP
from typing import Optional
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


from app.utils import get_logger

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=ProfileResponse, 
    summary="Create user profile"
)
def create_profile(
    profile: ProfileCreate = Depends(ProfileCreate.as_form), 
    file: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileResponse:
    """
    Create a new profile for the authenticated user.
    
    - **full_name**: First and last name 
    - **age**: Valid age between 0-120 years
    - **gender**: M (Male) or F (Female)
    - **weight**: Weight in kg (30-300 kg)
    - **height**: Height in cm (50-250 cm)
    - **goal**: Health/fitness objective
    - **file**: Optional profile image (JPG/PNG)
    """
    
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        logger.warning(f"Profile creation failed - Already exists for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this user"
        )
        
    image_url = None
    if file:
        if file.content_type not in IMAGE_EXT_MAP.keys():
            logger.warning(f"Invalid file type attempted: {file.content_type} by user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {', '.join(IMAGE_EXT_MAP.keys())} images are allowed"
            )

        ext = IMAGE_EXT_MAP[file.content_type]
        filename = f"profile_{current_user.id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        try:
            with file.file as src, open(file_path, "wb") as buffer:
                shutil.copyfileobj(src, buffer)
            image_url = f"{BASE_URL}/{UPLOAD_DIR}/{filename}"
            logger.debug(f"Profile image saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save profile image for {current_user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save profile image"
            )
        
    new_profile = Profile(
        user_id=current_user.id,
        **profile.model_dump(),
        profile_image=image_url
    )

    try:
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        logger.info(f"Profile created successfully for user: {current_user.email} (ID: {new_profile.id})")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during profile creation for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error occurred"
        )
        
    return new_profile


@router.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfileGetResponse, 
    summary="Get current user profile"
)
def get_profile(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileGetResponse:
    """
    Get the profile of the currently authenticated user.
    
    Returns profile information including personal details and health metrics.
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        logger.debug(f"No profile found for user: {current_user.email}")
 
        return ProfileGetResponse(
            message="Profile not found",
            profile=None
        )
        
    logger.debug(f"Profile fetched successfully for user: {current_user.email}")

    return ProfileGetResponse(
        message="Profile fetched successfully",
        profile=profile
    )

@router.patch(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfileResponse, 
    summary="Update user profile"
)
def update_profile(
    profile: ProfileUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileResponse:
    """
    Update profile fields for the authenticated user.
    
    All fields are optional. Only provided fields will be updated.
    
    Examples:
    - Update only weight: {"weight": 75.5}
    - Update multiple fields: {"full_name": "New Name", "age": 30, "goal": "Weight Loss"}
    """
    
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if not existing_profile:
        logger.warning(f"Update failed - No profile found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first"
        )

    update_data = profile.model_dump(exclude_unset=True)

    if not update_data:
        logger.warning(f"Update failed - No data provided by user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update. Please provide at least one field to update"
        )
            
    updated_fields = []

    for key, value in update_data.items():
        setattr(existing_profile, key, value)
        updated_fields.append(key)
        logger.debug(f"Updated {key} for user {current_user.email}")

    try:
        db.commit()
        db.refresh(existing_profile)
        
        logger.info(f"Profile updated successfully for user: {current_user.email} (ID: {existing_profile.id}) - Fields: {', '.join(updated_fields)}")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during profile update for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error occurred"
        )

    return existing_profile

@router.delete(
    "/", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete user profile"
)
def delete_my_profile(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete the profile of the currently authenticated user.
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        logger.warning(f"Delete failed - No profile found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No profile found to delete"
        )

    try:
        if profile.profile_image:
            filename = profile.profile_image.split("/")[-1]
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Profile image deleted: {filename}")
            except Exception as e:
                logger.error(f"Failed to delete image: {str(e)}")

        db.delete(profile)
        db.commit()
        
        logger.info(f"Profile deleted successfully for user: {current_user.email}")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during profile deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error during deletion"
        )
    
    return None 
    
@router.put(
    "/photo", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfilePhotoResponse, 
    summary="Upload or update profile photo"
)
def upload_profile_photo(
    file: UploadFile = File(..., description="Profile image (JPG or PNG only)"), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfilePhotoResponse:
    """
    Upload or update profile photo for the authenticated user.
    
    - **file**: Image file (JPG or PNG format only)
    - **Max size**: Recommended under 5MB
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if not profile:
        logger.warning(f"Photo upload failed - No profile found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first"
        )

    if file.content_type not in IMAGE_EXT_MAP.keys():
        logger.warning(f"Invalid file type attempted by user: {current_user.email} - {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {', '.join(IMAGE_EXT_MAP.keys())} images are allowed"
        )
    
    ext = IMAGE_EXT_MAP[file.content_type]
    filename = f"profile_{current_user.id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if profile.profile_image:
        old_filename = profile.profile_image.split("/")[-1]
        old_path = os.path.join(UPLOAD_DIR, old_filename)

        try:
            if os.path.exists(old_path):
                os.remove(old_path)
                logger.debug(f"Old profile photo deleted: {old_filename}")
        except Exception as e:
            logger.error(f"Failed to delete old profile photo: {str(e)}")

    try:
        with file.file as src, open(file_path, "wb") as buffer:
            shutil.copyfileobj(src, buffer)
            
        logger.debug(f"New profile photo saved: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save profile photo for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not save file to disk. Please try again"
        )

    image_url = f"{BASE_URL}/{UPLOAD_DIR}/{filename}"
    profile.profile_image = image_url
    
    try:
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Profile photo uploaded successfully for user: {current_user.email} (ID: {profile.id})")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during photo upload for {current_user.email}: {str(e)}")
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up uploaded file due to database error: {filename}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file: {str(cleanup_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile with new photo. Please try again"
        )
        
    return ProfilePhotoResponse(
            message="Photo uploaded successfully",
            image_url=image_url
        )
    
@router.get(
    "/photo", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfilePhotoResponse, 
    summary="Get profile photo")
def get_profile_photo(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfilePhotoResponse:
    """
    Get the profile photo URL for the authenticated user.
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        logger.debug(f"No profile found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
        
    if not profile.profile_image:
        logger.debug(f"No profile photo found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile photo found"
        )

    logger.debug(f"Profile photo retrieved for user: {current_user.email}")
    
    return ProfilePhotoResponse(
        message="Profile photo retrieved successfully",
        image_url=profile.profile_image
    )
    
@router.delete(
    "/photo", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete profile photo"
)
def delete_profile_photo(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete the profile photo of the authenticated user.
    
    This removes the image file from storage and clears the image URL from the profile.
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        logger.warning(f"Delete photo failed - No profile found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
        
    if not profile.profile_image:
        logger.warning(f"Delete photo failed - No photo found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile photo found to delete"
        )
        
    filename = profile.profile_image.split("/")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    file_deleted = False
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True
            logger.debug(f"Profile photo file deleted: {filename}")
        else:
            logger.warning(f"Profile photo file not found on disk: {filename}")
    except Exception as e:
        logger.error(f"Failed to delete profile photo file: {str(e)}")

    profile.profile_image = None
    
    try:
        db.commit()
        db.refresh(profile)
        
        if file_deleted:
            logger.info(f"Profile photo deleted successfully for user: {current_user.email} (ID: {profile.id})")
        else:
            logger.info(f"Profile photo reference cleared for user: {current_user.email} (file not found)")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during profile photo deletion for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile. Please try again"
        )    

    return None
