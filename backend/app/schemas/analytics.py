from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date

class MetricSummary(BaseModel):
    """Aggregated statistics for a specific numerical health metric (e.g., Steps, Sleep)."""
    avg: float = Field(0.0, description="The average value recorded over the period.")
    min: float = Field(0.0, description="The minimum value recorded over the period.")
    max: float = Field(0.0, description="The maximum value recorded over the period.")
    total: float = Field(0.0, description="The sum total of all values recorded over the period.")
    days_recorded: int = Field(0, description="Total number of days that have data logs for this metric.")
    target: float = Field(0.0, description="The daily goal/threshold for this metric.")
    achievement_rate: float = Field(0.0, description="Percentage of days where the daily target was successfully met.")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "avg": 8500.5,
                "min": 4000.0,
                "max": 12000.0,
                "total": 59503.5,
                "days_recorded": 7,
                "target": 10000.0,
                "achievement_rate": 71.43
            }
        }
    )

class CategoricalMetricSummary(BaseModel):
    """Summary for non-numerical metrics like Sleep Quality (Poor, Good, etc.)."""
    most_frequent: Optional[str] = Field(None, description="The most common category recorded (the mode).")
    recorded_days: int = Field(0, description="Total days this metric was logged.")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "most_frequent": "Good",
                "recorded_days": 5
            }
        }
    )

class OverallSummaryResponse(BaseModel):
    """Holistic health report containing aggregated summaries for all core metrics."""
    message: str = Field(..., description="Status message explaining the result of the analytics calculation.")
    steps: MetricSummary = Field(default_factory=MetricSummary)
    sleep: MetricSummary = Field(default_factory=MetricSummary)
    water: MetricSummary = Field(default_factory=MetricSummary)
    activity: MetricSummary = Field(default_factory=MetricSummary)
    sedentary: MetricSummary = Field(default_factory=MetricSummary)
    sugar: MetricSummary = Field(default_factory=MetricSummary)
    fruits: MetricSummary = Field(default_factory=MetricSummary)
    sleep_quality: CategoricalMetricSummary = Field(
        default_factory=CategoricalMetricSummary,
        description="Summary of sleep quality ratings over the selected period."
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "message": "Overall health summary fetched successfully",
                "steps": {
                    "avg": 8500.0,
                    "target": 10000.0,
                    "achievement_rate": 71.4,
                    "days_recorded": 7
                },
                "sleep": {
                    "avg": 7.2,
                    "target": 8.0,
                    "achievement_rate": 42.8,
                    "days_recorded": 7
                },
                "sleep_quality": {
                    "most_frequent": "Good",
                    "recorded_days": 5
                }
            }
        }
    )

class HealthInsight(BaseModel):
    """A single actionable health recommendation or observation derived from data correlation."""
    category: str = Field(..., description="The area of health (e.g., Sleep, Heart Health, Medical Context).")
    message: str = Field(..., description="The personalized advice or observation message.")
    priority: str = Field("low", description="The urgency level: low, medium, high.")
    trend: Optional[str] = Field(None, description="The direction of change: improving, declining, or stable.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "category": "Sleep Hygiene",
                "message": "High screen time correlates with your lower sleep quality this week.",
                "priority": "medium",
                "trend": "declining"
            }
        }
    )

class InsightsResponse(BaseModel):
    """Comprehensive health insights and scoring report for the last 7 days."""
    health_score: float = Field(..., description="Overall health score (0-100) combining behavior and context.")
    risk_level: str = Field(..., description="Health risk category: Low, Moderate, High, Critical.")
    insights: List[HealthInsight] = Field(default_factory=list, description="List of personalized insights.")
    summary_message: str = Field(..., description="A high-level summary of the user's current health status.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "health_score": 78.5,
                "risk_level": "Low",
                "insights": [
                    {
                        "category": "Medical Context",
                        "message": "Your sugar intake is well-managed for your diabetes profile.",
                        "priority": "high",
                        "trend": "stable"
                    }
                ],
                "summary_message": "High-performance health assessment completed."
            }
        }
    )

class TrendDataPoint(BaseModel):
    """Daily health score snapshot used for plotting progress over time."""
    log_date: date = Field(..., description="The date for this record.")
    health_score: float = Field(0.0, description="Calculated holistic health score for this specific day.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "log_date": "2026-05-03",
                "health_score": 82.4
            }
        }
    )

class TrendsResponse(BaseModel):
    """Collection of time-series data points for multi-day health analysis."""
    message: str = Field(..., description="Status message.")
    data: List[TrendDataPoint] = Field(..., description="Ordered list of daily health records.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "message": "Trend analysis complete",
                "data": [
                    {"log_date": "2026-05-01", "health_score": 75.0},
                    {"log_date": "2026-05-02", "health_score": 78.5},
                    {"log_date": "2026-05-03", "health_score": 82.4}
                ]
            }
        }
    )

class Recommendation(BaseModel):
    """A prioritized actionable task provided by the Digital Coach."""
    task: str = Field(..., description="The specific action the user should take today.")
    benefit: str = Field(..., description="The health benefit of completing this task.")
    priority: str = Field("low", description="Urgency: low, medium, or high.")
    category: str = Field(..., description="The health area (e.g., Nutrition, Activity, Sleep).")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "task": "Take a 5-minute movement break every hour.",
                "benefit": "Reduces pressure on your arteries and improves circulation.",
                "priority": "high",
                "category": "Activity"
            }
        }
    )

class RecommendationsResponse(BaseModel):
    """Collection of prioritized tasks for the user's digital coaching experience."""
    message: str = Field(..., description="Status message.")
    recommendations: List[Recommendation] = Field(default_factory=list, description="List of actionable tasks.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "message": "Coach tasks generated",
                "recommendations": [
                    {
                        "task": "Walk 2000 more steps today.",
                        "benefit": "Strengthens your heart.",
                        "priority": "medium",
                        "category": "Activity"
                    }
                ]
            }
        }
    )

class HealthStatusResponse(BaseModel):
    """Response for the dashboard 'Hero' section showing the overall score and risk category."""
    health_score: float = Field(..., description="All-time overall health score (0-100).")
    risk_level: str = Field(..., description="Health risk assessment: Low, Moderate, High, Critical.")
    summary_message: str = Field(..., description="A high-level summary of the holistic health baseline.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "health_score": 85.0,
                "risk_level": "Low",
                "summary_message": "Holistic health baseline established."
            }
        }
    )