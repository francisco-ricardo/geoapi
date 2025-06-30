"""
Aggregation endpoints for the API.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_request_logger
from app.core.logging import ContextLogger
from app.schemas.aggregation import (
    AggregatedSpeedResponse,
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
        response_data = [AggregatedSpeedResponse(**item) for item in aggregated_data]

        # Build final response
        response = AggregationListResponse(
            data=response_data, total_count=len(response_data), day=day, period=period
        )

        logger.info(f"Returned {len(response_data)} aggregated records")
        return response

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
async def get_aggregate_by_link(
    link_id: int,
    day: str = Query(..., description="Day of week (Monday, Tuesday, etc.)"),
    period: str = Query(..., description="Time period (AM Peak, PM Peak, etc.)"),
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> SingleLinkAggregateResponse:
    """
    Get speed and metadata for a single road segment.

    Returns aggregated speed data for a specific link including:
    - Average speed for the specified day/period
    - Statistical measures for that link
    - Link metadata and geometry
    - Number of records used in aggregation

    Args:
        link_id: ID of the specific link
        day: Day of week (e.g., "Monday", "Tuesday")
        period: Time period (e.g., "AM Peak", "PM Peak", "Midday")
        db: Database session
        logger: Request-scoped logger

    Returns:
        SingleLinkAggregateResponse: Aggregated data for the specific link

    Raises:
        HTTPException: If link not found or parameters invalid
    """
    logger.info(f"Getting aggregate for link_id={link_id}, day={day}, period={period}")

    try:
        # Create aggregation service
        aggregation_service = AggregationService(db)

        # Get single link aggregated data
        link_data = aggregation_service.get_single_link_aggregate(link_id, day, period)

        if not link_data:
            logger.warning(
                f"No data found for link_id={link_id}, day={day}, period={period}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for link {link_id} on {day} during {period}",
            )

        # Convert to response object
        response = SingleLinkAggregateResponse(**link_data)

        logger.info(f"Successfully retrieved aggregate for link_id={link_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error getting aggregate for link {link_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
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
