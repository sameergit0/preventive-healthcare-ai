from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from app.schemas import ProfileCreate, ProfileResponse, ProfileUpdate
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
    summary="Create User Profile",
    description="Initializes a new health profile for the authenticated user. This includes physiological data and an optional profile image."
)
def create_profile(
    profile: ProfileCreate = Depends(ProfileCreate.as_form), 
    file: Optional[UploadFile] = File(None, description="Optional profile picture (JPEG/PNG)"), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileResponse:
    """
    Establish a comprehensive health profile for the current user.
    
    1. Verifies that the user does not already have a profile.
    2. Processes and saves the optional profile image if provided.
    3. Calculates physiological metadata (handled by the schema during response).
    4. Persists the profile data to the database.
    """
    
    # 1. Integrity Check: Prevent duplicate profiles
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        logger.warning(f"Profile creation conflict: User {current_user.email} already has a profile.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A health profile already exists for your account. Please use the update endpoint for changes."
        )
        
    # 2. Media Handling: Process profile image if uploaded
    image_url = None
    if file:
        if file.content_type not in IMAGE_EXT_MAP.keys():
            logger.warning(f"Unsupported media type: {file.content_type} uploaded by {current_user.email}")
            allowed_types = ", ".join(IMAGE_EXT_MAP.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Please upload one of: {allowed_types}"
            )

        ext = IMAGE_EXT_MAP[file.content_type]
        filename = f"profile_{current_user.id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        try:
            with file.file as src, open(file_path, "wb") as buffer:
                shutil.copyfileobj(src, buffer)
            image_url = f"{BASE_URL}/{UPLOAD_DIR}/{filename}"
            logger.debug(f"Profile image persisted for user {current_user.email}: {filename}")
        except Exception as e:
            logger.error(f"Image persistence failure for {current_user.email}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while saving your profile image. The rest of your profile was not saved."
            )
    
    # 3. Data Persistence: Create and save profile record
    new_profile = Profile(
        user_id=current_user.id,
        **profile.model_dump(),
        profile_image=image_url
    )

    try:
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        logger.info(f"Health profile created successfully: {current_user.email} (Profile ID: {new_profile.id})")
        return new_profile
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database persistence error for {current_user.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred while saving your health profile. Please try again later."
        )


@router.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfileResponse, 
    summary="Get Current Profile",
    description="Retrieves the detailed health profile for the currently authenticated user, including physical metrics and BMI calculations."
)
def get_profile(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileResponse:
    """
    Fetch the complete profile data for the logged-in user.
    
    This endpoint requires a valid JWT token. If no profile exists yet, 
    it will return a 404 error, indicating that the user needs to create one.
    """
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        logger.debug(f"Profile lookup failed: No profile record found for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile data not found. Please complete your initial profile setup first."
        )
        
    logger.debug(f"Profile data retrieved successfully for {current_user.email}")
    return profile


@router.patch(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=ProfileResponse, 
    summary="Update Profile",
    description="Updates one or more profile fields. Supports partial updates. Unprovided or empty fields are ignored."
)
def update_profile(
    profile: ProfileUpdate = Depends(ProfileUpdate.as_form), 
    file: Optional[UploadFile] = File(None, description="Optional new profile photo"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> ProfileResponse:
    """
    Update the health profile for the authenticated user.
    
    - **Partial Update**: Only the fields you provide will be changed. Unprovided fields are ignored.
    - **Photo Management**: Uploading a new photo automatically replaces and deletes the previous one.
    """
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not existing_profile:
        logger.warning(f"Update failed: Profile not found for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found. Please create your profile first."
        )

    # 2. Photo Handling
    if file:
        if file.content_type not in IMAGE_EXT_MAP.keys():
            logger.warning(f"Invalid photo format: {file.content_type} uploaded by {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Please upload: {', '.join(IMAGE_EXT_MAP.keys())}"
            )

        # Cleanup old image
        if existing_profile.profile_image:
            old_filename = existing_profile.profile_image.split("/")[-1]
            old_path = os.path.join(UPLOAD_DIR, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    logger.debug(f"Deprecated photo removed: {old_filename}")
                except Exception as e:
                    logger.error(f"Cleanup failed for {old_filename}: {str(e)}")

        # Save new image
        ext = IMAGE_EXT_MAP[file.content_type]
        filename = f"profile_{current_user.id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            with file.file as src, open(file_path, "wb") as buffer:
                shutil.copyfileobj(src, buffer)
            existing_profile.profile_image = f"{BASE_URL}/{UPLOAD_DIR}/{filename}"
            logger.info(f"Profile photo refreshed for {current_user.email}")
        except Exception as e:
            logger.error(f"Persistence error for profile photo: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System error occurred while updating your profile photo."
            )

    # 3. Field Updates
    update_data = profile.model_dump(exclude_none=True)
    
    # If no text fields AND no photo are provided, we skip the commit
    if not update_data and not file:
        logger.warning(f"No data provided for update by {current_user.email}. No changes made.")
        return existing_profile

    updated_fields = []

    for key, value in update_data.items():
        setattr(existing_profile, key, value)
        updated_fields.append(key)

    try:
        db.commit()
        db.refresh(existing_profile)
        
        if updated_fields or file:
            fields_str = f"Fields: {', '.join(updated_fields)}" if updated_fields else "photo only"
            logger.info(f"Profile updated for {current_user.email} | {fields_str}")
            
        return existing_profile
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database update failure for {current_user.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while updating your profile. Changes reverted."
        )


@router.delete(
    "/photo", 
    status_code=status.HTTP_204_NO_CONTENT, 
    response_model=None, 
    summary="Delete profile photo",
    description="Deletes the authenticated user's profile photo from both physical storage and the database."
)
def delete_profile_photo(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Remove the profile photo for the authenticated user.
    
    This endpoint safely handles a two-step deletion process:
    1. Removes the physical image file from the server's local upload directory.
    2. Nullifies the `profile_image` reference in the database.
    
    Returns:
        - 204 No Content on success.
        
    Raises:
        - 404 Not Found: If the user has no profile, or if their profile currently has no photo.
        - 500 Internal Server Error: If the database transaction fails.
    """
    
    # 1. Existence Check
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile or not profile.profile_image:
        logger.warning(f"Delete photo failed - Not found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile photo not found"
        )
        
    # 2. File Cleanup
    # Extract just the filename from the URL (e.g., 'profile_1.jpg')
    filename = profile.profile_image.split("/")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.debug(f"Photo file deleted: {filename}")
        except Exception as e:
            # We log the error but DO NOT crash the request. 
            # If the file is locked or already gone, we still want to clear the DB reference.
            logger.error(f"Failed to delete photo file: {str(e)}")

    # 3. Database Update
    profile.profile_image = None
    try:
        db.commit()
        logger.info(f"Profile photo deleted for user: {current_user.email}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during photo deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete photo reference"
        )
        
    return None


@router.delete(
    "/", 
    status_code=status.HTTP_204_NO_CONTENT, 
    response_model=None, 
    summary="Delete full profile",
    description="Permanently deletes the authenticated user's health profile and cleans up any associated physical files (like profile photos)."
)
def delete_my_profile(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete the full profile of the authenticated user.
    
    This endpoint performs a comprehensive cleanup:
    1. Validates profile existence.
    2. Gracefully attempts to delete the physical profile image (if one exists).
    3. Deletes the profile record from the database.
    
    Returns:
        - 204 No Content on success.
        
    Raises:
        - 404 Not Found: If the user currently has no profile.
        - 500 Internal Server Error: If the database deletion transaction fails.
    """
    
    # 1. Existence Check
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        logger.warning(f"Delete failed - No profile for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profile not found"
        )

    # 2. Physical File Cleanup
    # We do this BEFORE db.delete, but we wrap it in its own try/except.
    # If file deletion fails (e.g. locked file), we catch the general Exception
    # so it DOES NOT stop the main database profile deletion from happening.
    if profile.profile_image:
        filename = profile.profile_image.split("/")[-1]
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Photo file deleted during profile removal: {filename}")
            except Exception as e:
                logger.error(f"Failed to delete photo file during profile removal: {str(e)}")

    # 3. Database Deletion
    try:
        db.delete(profile)
        db.commit()
        logger.info(f"Full profile deleted for user: {current_user.email}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during profile deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete profile"
        )
        
    return None
