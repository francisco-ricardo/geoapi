"""
Link endpoints for the API.
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from geoalchemy2 import WKBElement
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_request_logger
from app.core.logging import ContextLogger
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkList, LinkResponse, LinkUpdate

router = APIRouter()


@router.get("/links/", response_model=List[LinkResponse])
async def get_links(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> List[LinkResponse]:
    """
    Get a list of links.

    Args:
        limit: Maximum number of links to return (default: 100)
        offset: Number of links to skip (default: 0)
        db: Database session
        logger: Request-scoped logger

    Returns:
        List[LinkResponse]: List of links
    """
    logger.info(f"Fetching links with limit={limit}, offset={offset}")

    links = db.query(Link).offset(offset).limit(limit).all()

    response_links = []
    for link in links:
        # Convert geometry to GeoJSON dict
        geometry_dict = None
        if link.geometry is not None:
            try:
                # Get GeoJSON string from PostGIS
                geojson_str = db.scalar(ST_AsGeoJSON(link.geometry))
                if geojson_str:
                    geometry_dict = json.loads(geojson_str)
            except Exception as e:
                logger.error(
                    f"Error converting geometry to GeoJSON for link_id={link.link_id}",
                    extra={"error": str(e), "link_id": link.link_id},
                )
                geometry_dict = None

        response_data = {
            "link_id": link.link_id,
            "road_name": link.road_name,
            "length": link.length,
            "road_type": link.road_type,
            "speed_limit": link.speed_limit,
            "geometry": geometry_dict,
            "speed_records_count": (
                link.speed_records.count() if hasattr(link, "speed_records") else 0
            ),
        }
        response_links.append(LinkResponse(**response_data))

    logger.info(f"Returned {len(response_links)} links")
    return response_links


@router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: int,
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> LinkResponse:
    """
    Get a specific link by ID.

    Args:
        link_id: ID of the link to retrieve
        db: Database session
        logger: Request-scoped logger

    Returns:
        LinkResponse: Link data

    Raises:
        HTTPException: If link not found
    """
    logger.info(f"Fetching link with ID {link_id}")

    link = db.query(Link).filter(Link.link_id == link_id).first()
    if not link:
        logger.warning(f"Link with ID {link_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with ID {link_id} not found",
        )

    # Convert geometry to GeoJSON dict
    geometry_dict = None
    if link.geometry is not None:
        try:
            geojson_str = db.scalar(ST_AsGeoJSON(link.geometry))
            if geojson_str:
                geometry_dict = json.loads(geojson_str)
        except Exception as e:
            logger.error(
                f"Error converting geometry to GeoJSON for link_id={link_id}",
                extra={"error": str(e), "link_id": link_id},
            )
            geometry_dict = None

    response_data = {
        "link_id": link.link_id,
        "road_name": link.road_name,
        "length": link.length,
        "road_type": link.road_type,
        "speed_limit": link.speed_limit,
        "geometry": geometry_dict,
        "speed_records_count": (
            link.speed_records.count() if hasattr(link, "speed_records") else 0
        ),
    }

    logger.info(f"Successfully retrieved link with ID {link_id}")
    return LinkResponse(**response_data)


@router.post(
    "/links/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    logger: ContextLogger = Depends(get_request_logger),
) -> LinkResponse:
    """
    Create a new link.

    Args:
        link: Link data to create
        db: Database session
        logger: Request-scoped logger

    Returns:
        LinkResponse: Created link data

    Raises:
        HTTPException: If link_id already exists or other database error
    """
    logger.info(f"Creating new link with ID {link.link_id}")

    # Check if link_id already exists
    existing_link = db.query(Link).filter(Link.link_id == link.link_id).first()
    if existing_link:
        logger.warning(f"Attempt to create link with existing ID {link.link_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Link with ID {link.link_id} already exists",
        )

    # Create new link
    # Convert geometry dict to proper format for PostGIS
    geometry_value = None
    if link.geometry:
        try:
            geometry_json = json.dumps(link.geometry)
            geometry_value = ST_GeomFromGeoJSON(geometry_json)
            logger.debug(f"Converted geometry for link_id={link.link_id}")
        except Exception as e:
            logger.error(
                f"Error converting GeoJSON to PostGIS geometry",
                extra={"error": str(e), "link_id": link.link_id},
            )

    db_link = Link(
        link_id=link.link_id,
        road_name=link.road_name,
        length=link.length,
        road_type=link.road_type,
        speed_limit=link.speed_limit,
        geometry=geometry_value,
    )

    try:
        db.add(db_link)
        db.commit()
        db.refresh(db_link)

        # Create response manually (avoiding geometry conversion for now)
        response_data = {
            "link_id": db_link.link_id,
            "road_name": db_link.road_name,
            "length": db_link.length,
            "road_type": db_link.road_type,
            "speed_limit": db_link.speed_limit,
            "geometry": link.geometry,  # Return original dict from request
            "speed_records_count": 0,  # New link has no speed records yet
        }

        logger.info(f"Successfully created link with ID {link.link_id}")
        return LinkResponse(**response_data)

    except IntegrityError as e:
        db.rollback()
        logger.error(
            f"Database integrity error creating link",
            extra={"error": str(e), "link_id": link.link_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}",
        )
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Internal server error creating link",
            extra={"error": str(e), "link_id": link.link_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
