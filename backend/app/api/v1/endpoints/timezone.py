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
    summary="Fetch Grouped Timezones",
    description="Returns a dictionary of all supported IANA timezones, grouped by their geographical regions (e.g., Asia, Europe, America)."
)
def get_grouped_timezones() -> TimezonesResponse:
    """
    Retrieve all valid timezones grouped by their top-level region.
    
    This is useful for frontend onboarding/signup flows where users 
    need to select their local timezone from a nested or grouped dropdown.
    
    Returns:
        TimezonesResponse: A dictionary where keys are regions and values are lists of timezone strings.
    """
    
    logger.debug("Starting timezone grouping process")
    
    # Fallback to a set of common timezones if VALID_TIMEZONES is empty
    source_tzs = VALID_TIMEZONES if VALID_TIMEZONES else {"UTC", "GMT", "Asia/Kolkata", "America/New_York", "Europe/London"}
    
    grouped = defaultdict(list)

    for tz in source_tzs:
        if "/" in tz:
            parts = tz.split("/")
            region = parts[0]
            grouped[region].append(tz)
        else:
            grouped["Other"].append(tz)

    # Sort regions alphabetically and sort timezones within each region
    sorted_grouped = {
        region: sorted(timezones)
        for region, timezones in sorted(grouped.items())
    }
        
    logger.info(f"Successfully grouped {len(source_tzs)} timezones into {len(sorted_grouped)} regions")
    
    return TimezonesResponse(grouped=sorted_grouped)

