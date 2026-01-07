from fastapi import APIRouter
from pydantic import BaseModel
import psutil
import random

router = APIRouter()

class MetricsData(BaseModel):
    cpu_percent: float
    memory_percent: float
    requests_per_hour: list[int] # Mock data format for chart
    latency_p95: float

@router.get("/", response_model=MetricsData)
async def get_system_metrics():
    """
    Get current system metrics.
    """
    # Mocking historical request data for the dashboard demo
    # In real app, we'd query SystemMetrics table
    mock_requests = [random.randint(10, 50) for _ in range(24)]
    
    return MetricsData(
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent,
        requests_per_hour=mock_requests,
        latency_p95=random.uniform(0.1, 0.5)
    )
