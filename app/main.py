from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, clinics, users
from app.core.exceptions import NotFoundException, UnauthorizedException, ForbiddenException, BadRequestException, ConflictException
from app.schemas.common import ErrorResponse
from app.middleware.audit import AuditMiddleware

app = FastAPI(
    title="Homoeo Clinic Management System API",
    description="Multi-tenant backend for clinic management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).model_dump())

@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).model_dump(), headers=exc.headers)

@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).model_dump())

@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).model_dump())

@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).model_dump())

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(clinics.router, prefix="/api/v1/clinics")
app.include_router(users.router, prefix="/api/v1/users")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
