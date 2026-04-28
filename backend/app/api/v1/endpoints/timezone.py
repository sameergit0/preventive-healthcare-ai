from fastapi import APIRouter, status
from collections import defaultdict
import logging
from app.core import VALID_TIMEZONES
from app.schemas import TimezonesResponse

router = APIRouter()
logger = logging.getLogger(__name__)

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
    
    Returns:
        TimezonesResponse: Dictionary with region as key and list of timezones as value
    """
    
    logger.debug("Fetching grouped timezones")
    
    grouped = defaultdict(list)

    for tz in VALID_TIMEZONES:
        if "/" in tz and not tz.startswith("Etc/"):
            region = tz.split("/")[0]
            grouped[region].append(tz)

    sorted_grouped = {
        region: sorted(timezones)
        for region, timezones in sorted(grouped.items())
    }
        
    logger.info(f"Returning {len(sorted_grouped)} timezone regions")
    
    return TimezonesResponse(grouped=sorted_grouped)

