from fastapi import APIRouter, status
from collections import defaultdict
from app.utils import get_logger
from app.core import VALID_TIMEZONES
from app.schemas import TimezonesResponse

router = APIRouter()
logger = get_logger(__name__)

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=TimezonesResponse,  
    summary="Get grouped timezones",
    description="Returns all available timezones grouped by geographic region."
)
def get_grouped_timezones() -> TimezonesResponse:
    """
    Get all available timezones grouped by region.
    """
    
    logger.debug("Fetching grouped timezones")
    
    # Use fallback if system timezones are not available
    source_tzs = VALID_TIMEZONES if VALID_TIMEZONES else {"UTC", "GMT", "Asia/Kolkata", "America/New_York", "Europe/London"}
    
    grouped = defaultdict(list)

    for tz in source_tzs:
        if "/" in tz:
            parts = tz.split("/")
            region = parts[0]
            # Use only the last part for display if desired, or keep full path
            grouped[region].append(tz)
        else:
            grouped["Other"].append(tz)

    # Sort regions and timezones within regions
    sorted_grouped = {
        region: sorted(timezones)
        for region, timezones in sorted(grouped.items())
    }
        
    logger.info(f"Returning {len(sorted_grouped)} timezone regions")
    
    return TimezonesResponse(grouped=sorted_grouped)

