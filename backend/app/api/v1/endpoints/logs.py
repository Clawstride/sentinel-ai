"""
Authentication Log Upload endpoint.

POST /logs/upload accepts a CSV file of authentication log events and
persists each row as a LogEvent. This endpoint only handles HTTP
concerns (reading the upload, wiring dependencies, translating domain
exceptions to HTTP responses) — all parsing/validation logic lives in
the service layer.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.log_event_repository import LogEventRepository
from app.schemas.log_event import LogUploadResponse
from app.services.log_event_service import LogUploadService
from app.utils.exceptions import InvalidCSVError, InvalidFileTypeError, MissingColumnsError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])


def get_log_upload_service(db: Session = Depends(get_db)) -> LogUploadService:
    """Wires the repository into the service (simple manual DI for this MVP)."""
    repository = LogEventRepository(db)
    return LogUploadService(repository)


@router.post(
    "/upload",
    response_model=LogUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an authentication log CSV file",
)
async def upload_log_file(
    file: UploadFile = File(..., description="CSV file containing authentication log events"),
    service: LogUploadService = Depends(get_log_upload_service),
) -> LogUploadResponse:
    """
    Accepts a CSV file, validates it, and bulk-inserts its rows as
    LogEvent records.

    - **400** if the file is not a CSV, is empty, or cannot be parsed
    - **422** if required columns are missing from the CSV
    - **500** for any unexpected error
    """
    try:
        file_bytes = await file.read()
        rows_imported = service.process_upload(
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
        )
    except InvalidFileTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvalidCSVError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MissingColumnsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Missing required columns", "missing_columns": exc.missing_columns},
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error while processing log file upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the file.",
        ) from exc
    finally:
        await file.close()

    return LogUploadResponse(
        message="Log file uploaded and processed successfully",
        rows_imported=rows_imported,
    )
