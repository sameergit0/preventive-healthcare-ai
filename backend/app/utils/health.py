from typing import Optional, Tuple, Dict
from app.core import (
    STEPS_GOAL_HIGH, STEPS_GOAL_LOW, 
    SLEEP_GOAL_HIGH, SLEEP_GOAL_LOW, 
    WATER_GOAL_HIGH, WATER_GOAL_LOW,
    ACTIVITY_GOAL_HIGH, ACTIVITY_GOAL_LOW,
    SEDENTARY_LIMIT_LOW, SEDENTARY_LIMIT_HIGH,
    SUGAR_LIMIT_LOW, SUGAR_LIMIT_HIGH,
    FRUITS_GOAL_HIGH, FRUITS_GOAL_LOW
)

SLEEP_QUALITY_SCORES = {
    "poor": 40,
    "average": 60,
    "good": 80,
    "excellent": 100
}

def get_metric_score(value: Optional[float], high_goal: float, low_goal: float, inverse: bool = False) -> int:
    """Calculate score for a single metric based on thresholds."""
    if value is None:
        return 0
    
    if not inverse:
        if value >= high_goal:
            return 100
        if value >= low_goal:
            return 70
        return 40
    else:
        # Lower is better (e.g. sedentary, sugar)
        if value <= high_goal: # high_goal is actually the "ideal" low limit
            return 100
        if value <= low_goal: # low_goal is the "limit"
            return 70
        return 40

def calculate_daily_health_score(
    steps: Optional[int] = None, 
    sleep_hours: Optional[float] = None, 
    water_intake: Optional[float] = None,
    sleep_quality: Optional[str] = None,
    activity_minutes: Optional[int] = None,
    sedentary_minutes: Optional[int] = None,
    nutrition_sugar: Optional[float] = None,
    nutrition_fruits: Optional[int] = None
) -> Optional[int]:
    """
    Calculate overall health score for a day based on multiple metrics.
    Returns None if all metrics are missing.
    """
    metrics = [
        steps, sleep_hours, water_intake, sleep_quality, 
        activity_minutes, sedentary_minutes, nutrition_sugar, nutrition_fruits
    ]
    if all(m is None for m in metrics):
        return None
    
    scores = []
    
    # Weights (total 100)
    # Steps: 15, Sleep: 20 (Hours 10, Quality 10), Water: 15, Activity: 20, Sedentary: 10, Nutrition: 20 (Sugar 10, Fruits 10)
    
    # 1. Steps (15)
    s_score = get_metric_score(steps, STEPS_GOAL_HIGH, STEPS_GOAL_LOW)
    scores.append(s_score * 0.15)
    
    # 2. Sleep (20)
    sh_score = get_metric_score(sleep_hours, SLEEP_GOAL_HIGH, SLEEP_GOAL_LOW)
    sq_score = SLEEP_QUALITY_SCORES.get(sleep_quality.lower() if sleep_quality else "", 0) if sleep_quality else 0
    
    if sleep_hours is not None and sleep_quality:
        scores.append(sh_score * 0.10 + sq_score * 0.10)
    elif sleep_hours is not None:
        scores.append(sh_score * 0.20)
    elif sleep_quality:
        scores.append(sq_score * 0.20)
    else:
        scores.append(0)
        
    # 3. Water (15)
    w_score = get_metric_score(water_intake, WATER_GOAL_HIGH, WATER_GOAL_LOW)
    scores.append(w_score * 0.15)
    
    # 4. Activity (20)
    a_score = get_metric_score(activity_minutes, ACTIVITY_GOAL_HIGH, ACTIVITY_GOAL_LOW)
    scores.append(a_score * 0.20)
    
    # 5. Sedentary (10)
    sed_score = get_metric_score(sedentary_minutes, SEDENTARY_LIMIT_LOW, SEDENTARY_LIMIT_HIGH, inverse=True)
    scores.append(sed_score * 0.10)
    
    # 6. Nutrition (20)
    sug_score = get_metric_score(nutrition_sugar, SUGAR_LIMIT_LOW, SUGAR_LIMIT_HIGH, inverse=True)
    f_score = get_metric_score(nutrition_fruits, FRUITS_GOAL_HIGH, FRUITS_GOAL_LOW)
    
    if nutrition_sugar is not None and nutrition_fruits is not None:
        scores.append(sug_score * 0.10 + f_score * 0.10)
    elif nutrition_sugar is not None:
        scores.append(sug_score * 0.20)
    elif nutrition_fruits is not None:
        scores.append(f_score * 0.20)
    else:
        scores.append(0)

    overall_score = int(sum(scores))
    return max(0, min(100, overall_score))

def get_metric_scores(
    steps: Optional[float] = None, 
    sleep: Optional[float] = None, 
    water: Optional[float] = None,
    activity: Optional[float] = None,
    sedentary: Optional[float] = None,
    sugar: Optional[float] = None,
    fruits: Optional[float] = None
) -> Dict[str, int]:
    """Get individual scores for each metric (for insights)."""
    return {
        "steps": get_metric_score(steps, STEPS_GOAL_HIGH, STEPS_GOAL_LOW) if steps is not None else 50,
        "sleep": get_metric_score(sleep, SLEEP_GOAL_HIGH, SLEEP_GOAL_LOW) if sleep is not None else 50,
        "water": get_metric_score(water, WATER_GOAL_HIGH, WATER_GOAL_LOW) if water is not None else 50,
        "activity": get_metric_score(activity, ACTIVITY_GOAL_HIGH, ACTIVITY_GOAL_LOW) if activity is not None else 50,
        "sedentary": get_metric_score(sedentary, SEDENTARY_LIMIT_LOW, SEDENTARY_LIMIT_HIGH, inverse=True) if sedentary is not None else 50,
        "sugar": get_metric_score(sugar, SUGAR_LIMIT_LOW, SUGAR_LIMIT_HIGH, inverse=True) if sugar is not None else 50,
        "fruits": get_metric_score(fruits, FRUITS_GOAL_HIGH, FRUITS_GOAL_LOW) if fruits is not None else 50
    }
