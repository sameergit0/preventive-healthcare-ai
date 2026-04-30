from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal, List
from datetime import date


class MetricSummary(BaseModel):
    average: Optional[float]
    total: Optional[float]
    max: Optional[float]
    min: Optional[float]
    days_recorded: int
    target: Optional[float] = None
    achievement_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    total_days: int
    active_days: int

    steps: MetricSummary
    sleep: MetricSummary
    water: MetricSummary
    activity: MetricSummary
    sedentary: MetricSummary
    sugar: MetricSummary
    fruits: MetricSummary

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class Insight(BaseModel):
    type: Literal["steps", "sleep", "water", "activity", "sedentary", "sugar", "fruits"]
    message: str
    severity: Literal["good", "warning", "critical"]

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthInsightsResponse(BaseModel):
    overall_score: int
    insights: List[Insight]

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class MetricTrend(BaseModel):
    current_avg: Optional[float]
    previous_avg: Optional[float]
    change_percent: Optional[float]  

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthTrendsResponse(BaseModel):
    steps: MetricTrend
    sleep: MetricTrend
    water: MetricTrend
    activity: MetricTrend
    sedentary: MetricTrend
    sugar: MetricTrend
    fruits: MetricTrend

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class Recommendation(BaseModel):
    type: Literal["steps", "sleep", "water", "activity", "sedentary", "sugar", "fruits"]             
    message: str
    priority: Literal["high", "medium", "low"]      

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthRecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class HealthScorePoint(BaseModel):
    date: date
    score: Optional[int]

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthScoreHistoryResponse(BaseModel):
    scores: List[HealthScorePoint]

    model_config = ConfigDict(from_attributes=True, extra="forbid")