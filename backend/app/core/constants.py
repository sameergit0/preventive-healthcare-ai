# List of valid timezone strings (IANA Time Zone Database)
# Used during signup and profile creation to ensure correct date-time calculations for users.
VALID_TIMEZONES = [
    "UTC", "GMT",
    "Africa/Cairo", "Africa/Johannesburg", "Africa/Lagos", "Africa/Nairobi",
    "America/Anchorage", "America/Argentina/Buenos_Aires", "America/Chicago", 
    "America/Denver", "America/Los_Angeles", "America/Mexico_City", 
    "America/New_York", "America/Phoenix", "America/Sao_Paulo", "America/Toronto",
    "Asia/Bangkok", "Asia/Dubai", "Asia/Hong_Kong", "Asia/Jakarta", 
    "Asia/Jerusalem", "Asia/Kolkata", "Asia/Seoul", "Asia/Shanghai", 
    "Asia/Singapore", "Asia/Tokyo",
    "Australia/Adelaide", "Australia/Brisbane", "Australia/Melbourne", 
    "Australia/Perth", "Australia/Sydney",
    "Europe/Amsterdam", "Europe/Berlin", "Europe/Brussels", "Europe/Istanbul", 
    "Europe/London", "Europe/Madrid", "Europe/Moscow", "Europe/Paris", "Europe/Rome",
    "Pacific/Auckland", "Pacific/Honolulu"
]

# Image file extension mapping for Profile Photo uploads.
# Maps MIME types to file extensions for storage.
IMAGE_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png"
}

# Daily health targets for achievement calculation (Analytics Summary)
HEALTH_TARGETS = {
    "steps": 10000,
    "sleep": 8.0,
    "water": 2.5,
    "activity": 30.0,
    "sedentary": 480.0,
    "sugar": 25.0,
    "fruits": 2.0
}

# Health Scoring Weights (Total = 1.0)
HEALTH_SCORE_WEIGHTS = {
    "metrics": 0.50,      
    "lifestyle": 0.20,    
    "physical": 0.15,     
    "medical": 0.15       
}

# Baseline Weights (when no logs are present)
BASELINE_SCORE_WEIGHTS = {
    "lifestyle": 0.30,
    "physical": 0.20,
    "medical": 0.50
}

# Risk Level Thresholds
RISK_LEVELS = {
    "LOW": "Low",
    "MODERATE": "Moderate",
    "HIGH": "High",
    "CRITICAL": "Critical"
}