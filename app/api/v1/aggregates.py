"""
Aggregation endpoints for the API.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_request_logger
from app.core.logging import ContextLogger
from app.schemas.aggregation import (
    AggregatedSpeedData,
    AggregationListResponse,
    DataSummaryResponse,
    SingleLinkAggregateResponse,
)
from app.services.aggregation_service import AggregationService

router = APIRouter()


@router.get("/aggregates/", response_model=AggregationListResponse)
async def get_aggregates(
    day: str = Query(..., description="Day of week (Monday, Tuesday, etc.)"),
    period: str = Query(..., description="Time period (AM Peak, PM Peak, etc.)"),
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> AggregationListResponse:
    """
    Get aggregated average speed per link for the given day and time period.

    Returns aggregated speed data including:
    - Average speed per link
    - Statistical measures (min, max, standard deviation)
    - Link metadata (road name, geometry, etc.)
    - Number of records used in aggregation

    Args:
        day: Day of week (e.g., "Monday", "Tuesday")
        period: Time period (e.g., "AM Peak", "PM Peak", "Midday")
        db: Database session
        logger: Request-scoped logger

    Returns:
        AggregationListResponse: List of aggregated speed data

    Raises:
        HTTPException: If day or period parameters are invalid
    """
    logger.info(f"Getting aggregates for day={day}, period={period}")

    try:
        # Create aggregation service
        aggregation_service = AggregationService(db)

        # Get aggregated data
        aggregated_data = aggregation_service.get_aggregated_speeds(day, period)

        # Convert to response objects
        response_data = [AggregatedSpeedData(**item) for item in aggregated_data]

        # Return direct list for client compatibility (overview.txt requirement)
        logger.info(f"Returned {len(response_data)} aggregated records")
        return response_data

    except ValueError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error getting aggregates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/aggregates/{link_id}", response_model=SingleLinkAggregateResponse)
async def get_link_aggregate(
    link_id: int,
    day: str = Query(..., description="Day of week (Monday, Tuesday, etc.)"),
    period: str = Query(..., description="Time period (AM Peak, PM Peak, etc.)"),
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> SingleLinkAggregateResponse:
    """
    Get speed and metadata for a single road segment.

    Returns detailed aggregation data for a specific link including:
    - Average speed for the given day/period
    - Statistical measures (min, max, standard deviation)
    - Link metadata (road name, geometry, length)
    - Number of speed records used in calculation

    Args:
        link_id: Unique identifier for the road link
        day: Day of week (e.g., "Monday", "Tuesday")
        period: Time period (e.g., "AM Peak", "PM Peak", "Midday")
        db: Database session
        logger: Request-scoped logger

    Returns:
        SingleLinkAggregateResponse: Aggregated data for the specific link

    Raises:
        HTTPException: If link_id not found or day/period parameters are invalid
    """
    logger.info(
        f"Getting aggregate data for link {link_id}",
        extra={"link_id": link_id, "day": day, "period": period},
    )

    try:
        # Use service layer for business logic
        service = AggregationService(db)
        result = service.get_single_link_aggregate(
            link_id=link_id, day=day, period=period
        )

        if result is None:
            logger.warning(
                f"Link {link_id} not found or no data available",
                extra={"link_id": link_id, "day": day, "period": period},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Link {link_id} not found or no data available for {day} {period}",
            )

        # Convert dict result to schema
        response_data = SingleLinkAggregateResponse(**result)

        logger.info(
            f"Successfully retrieved data for link {link_id}",
            extra={
                "link_id": link_id,
                "record_count": response_data.record_count,
                "average_speed": response_data.average_speed,
            },
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting aggregate for link {link_id}: {str(e)}",
            extra={"link_id": link_id, "day": day, "period": period, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing request",
        )


@router.get("/aggregates/summary/", response_model=DataSummaryResponse)
async def get_data_summary(
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> DataSummaryResponse:
    """
    Get summary statistics of the available data.

    Returns overview of the dataset including:
    - Total number of speed records and links
    - Overall speed statistics
    - Available time periods and days
    - Data coverage information

    Args:
        db: Database session
        logger: Request-scoped logger

    Returns:
        DataSummaryResponse: Summary statistics of the data
    """
    logger.info("Getting data summary")

    try:
        # Create aggregation service
        aggregation_service = AggregationService(db)

        # Get summary data
        summary_data = aggregation_service.get_data_summary()

        # Convert to response object
        response = DataSummaryResponse(**summary_data)

        logger.info("Successfully retrieved data summary")
        return response

    except Exception as e:
        logger.exception(f"Error getting data summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/patterns/slow_links/", response_model=List[AggregatedSpeedData])
async def get_slow_links(
    period: str = Query(..., description="Time period (AM Peak, PM Peak, etc.)"),
    threshold: float = Query(..., description="Speed threshold in mph (e.g., 15.0)"),
    min_days: int = Query(
        ..., description="Minimum number of days the condition must be met (1-7)"
    ),
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> List[AggregatedSpeedData]:
    """
    Get links with average speeds below threshold for at least min_days in a week.

    Identifies chronically slow road segments by analyzing speed patterns across
    multiple days of the week for a specific time period.

    Args:
        period: Time period (e.g., "AM Peak", "PM Peak", "Midday")
        threshold: Speed threshold in mph (links below this are considered slow)
        min_days: Minimum number of days the condition must be met (1-7)
        db: Database session
        logger: Request-scoped logger

    Returns:
        List[AggregatedSpeedData]: Links meeting the slow speed criteria

    Raises:
        HTTPException: If parameters are invalid or out of range
    """
    logger.info(
        f"Getting slow links for period={period}, threshold={threshold}, min_days={min_days}",
        extra={"period": period, "threshold": threshold, "min_days": min_days},
    )

    try:
        # Validate parameters
        if threshold <= 0:
            raise ValueError("Threshold must be positive")
        if not (1 <= min_days <= 7):
            raise ValueError("min_days must be between 1 and 7")

        # Use service layer for business logic
        service = AggregationService(db)
        results = service.get_slow_links_pattern(
            period=period, threshold=threshold, min_days=min_days
        )

        # Convert to response objects
        response_data = [AggregatedSpeedData(**item) for item in results]

        logger.info(
            f"Found {len(response_data)} slow links meeting criteria",
            extra={
                "count": len(response_data),
                "period": period,
                "threshold": threshold,
                "min_days": min_days,
            },
        )

        return response_data

    except ValueError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error getting slow links: {str(e)}",
            extra={"period": period, "threshold": threshold, "min_days": min_days},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing request",
        )
