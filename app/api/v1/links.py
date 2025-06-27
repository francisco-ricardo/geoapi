"""
Link endpoints for the API.
"""
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from geoalchemy2.functions import ST_GeomFromGeoJSON, ST_AsGeoJSON
from geoalchemy2 import WKBElement

from app.api.dependencies import get_db
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkResponse, LinkUpdate, LinkList

router = APIRouter()


@router.post("/links/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db)
) -> LinkResponse:
    """
    Create a new link.
    
    Args:
        link: Link data to create
        db: Database session
        
    Returns:
        LinkResponse: Created link data
        
    Raises:
        HTTPException: If link_id already exists or other database error
    """
    # Check if link_id already exists
    existing_link = db.query(Link).filter(Link.link_id == link.link_id).first()
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Link with ID {link.link_id} already exists"
        )
    
    # Create new link
    # Convert geometry dict to proper format for PostGIS
    geometry_value = None
    if link.geometry:
        geometry_json = json.dumps(link.geometry)
        geometry_value = ST_GeomFromGeoJSON(geometry_json)
    
    db_link = Link(
        link_id=link.link_id,
        road_name=link.road_name,
        length=link.length,
        road_type=link.road_type,
        speed_limit=link.speed_limit,
        geometry=geometry_value
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
            "speed_records_count": 0  # New link has no speed records yet
        }
        
        return LinkResponse(**response_data)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
