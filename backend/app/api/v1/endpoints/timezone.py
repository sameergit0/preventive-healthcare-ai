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
    
    Returns:
        TimezonesResponse: Dictionary with region as key and list of timezones as value
    """
    
    logger.debug("Fetching grouped timezones")
    
    grouped = defaultdict(list)

    for tz in VALID_TIMEZONES:
        if "/" in tz:
            region = tz.split("/")[0]
            if region == "Etc":
                grouped["Other"].append(tz)
            else:
                grouped[region].append(tz)
        else:
            grouped["Other"].append(tz)

    sorted_grouped = {
        region: sorted(timezones)
        for region, timezones in sorted(grouped.items())
    }
        
    logger.info(f"Returning {len(sorted_grouped)} timezone regions")
    
    return TimezonesResponse(grouped=sorted_grouped)

