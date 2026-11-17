from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal, seed_initial_data
from app.config import db_info, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from app import schemas, crud

router = APIRouter(prefix="/api", tags=["Analytics & System"])

@router.get("/analytics/stats", response_model=schemas.StatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve comprehensive system statistics and KPI metrics."""
    return crud.get_system_stats(db)

@router.get("/system/status", response_model=schemas.DBStatusResponse)
def get_system_status():
    """Retrieve database connectivity status and configuration."""
    return schemas.DBStatusResponse(
        engine=db_info["engine"],
        connected=db_info["connected"],
        host=db_info["host"],
        port=db_info["port"],
        database=db_info["database"],
        message=db_info["message"]
    )

@router.post("/system/reseed", response_model=schemas.MessageResponse)
def reseed_database(db: Session = Depends(get_db)):
    """Re-seed sample departments, courses, students, and enrollments."""
    try:
        seed_initial_data(db)
        return schemas.MessageResponse(message="Sample database successfully populated / re-seeded!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-seed database: {str(e)}")

@router.post("/system/test-mysql", response_model=schemas.MessageResponse)
def test_mysql_connection():
    """Test connection to MySQL server using configured credentials."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=3
        )
        conn.close()
        return schemas.MessageResponse(
            message=f"MySQL connection to {DB_HOST}:{DB_PORT} as '{DB_USER}' succeeded!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"MySQL connection to {DB_HOST}:{DB_PORT} failed: {str(e)}"
        )

