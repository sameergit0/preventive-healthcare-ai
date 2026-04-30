import zoneinfo

VALID_TIMEZONES = zoneinfo.available_timezones()

# Health Thresholds
STEPS_GOAL_HIGH = 10000
STEPS_GOAL_LOW = 6000

SLEEP_GOAL_HIGH = 7.5
SLEEP_GOAL_LOW = 6.0

WATER_GOAL_HIGH = 2.7
WATER_GOAL_LOW = 2.0

ACTIVITY_GOAL_HIGH = 45
ACTIVITY_GOAL_LOW = 20

# Lower is better for sedentary time
SEDENTARY_LIMIT_LOW = 480  # 8 hours
SEDENTARY_LIMIT_HIGH = 600  # 10 hours

# Lower is better for sugar
SUGAR_LIMIT_LOW = 25
SUGAR_LIMIT_HIGH = 50

FRUITS_GOAL_HIGH = 3
FRUITS_GOAL_LOW = 1

IMAGE_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png"
}