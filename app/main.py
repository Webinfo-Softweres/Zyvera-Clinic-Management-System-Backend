from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.core.database import engine, Base, get_db
from app.models.clinical_data import ClinicalData
from app.schemas.clinical import (
    ClinicalDataCreate,
    ClinicalDataUpdate,
    ClinicalDataResponse,
    StandardResponse
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up on shutdown
    await engine.dispose()

app = FastAPI(
    title="Clinical Data API",
    description="Simple Production Ready FastAPI Backend for ClinicalData",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"Internal server error: {str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.post("/api/v1/clinical", response_model=StandardResponse)
async def create_clinical_record(record_in: ClinicalDataCreate, db: AsyncSession = Depends(get_db)):
    db_record = ClinicalData(**record_in.model_dump())
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return StandardResponse(
        success=True,
        message="Record created successfully",
        data=ClinicalDataResponse.model_validate(db_record).model_dump()
    )

@app.get("/api/v1/clinical", response_model=StandardResponse)
async def get_all_records(
    centre_code: Optional[str] = None,
    hospital_no: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ClinicalData)
    if centre_code:
        query = query.where(ClinicalData.centre_code == centre_code)
    if hospital_no:
        query = query.where(ClinicalData.hospital_no == hospital_no)
        
    result = await db.execute(query)
    records = result.scalars().all()
    
    data = [ClinicalDataResponse.model_validate(r).model_dump() for r in records]
    
    return StandardResponse(
        success=True,
        message="Records retrieved successfully",
        data=data
    )

@app.get("/api/v1/clinical/{id}", response_model=StandardResponse)
async def get_single_record(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClinicalData).where(ClinicalData.id == id))
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    return StandardResponse(
        success=True,
        message="Record retrieved successfully",
        data=ClinicalDataResponse.model_validate(record).model_dump()
    )

@app.patch("/api/v1/clinical/{id}", response_model=StandardResponse)
async def update_record(id: str, record_in: ClinicalDataUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClinicalData).where(ClinicalData.id == id))
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Only update provided fields
    update_data = record_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
        
    await db.commit()
    await db.refresh(record)
    
    return StandardResponse(
        success=True,
        message="Record updated successfully",
        data=ClinicalDataResponse.model_validate(record).model_dump()
    )

@app.delete("/api/v1/clinical/{id}", response_model=StandardResponse)
async def delete_record(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClinicalData).where(ClinicalData.id == id))
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    await db.delete(record)
    await db.commit()
    
    return StandardResponse(
        success=True,
        message="Record deleted successfully",
        data=None
    )
