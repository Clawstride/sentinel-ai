"""
Service layer for the Authentication Log Upload feature.
"""

import io
import logging

import pandas as pd

from app.models.log_event import LogEvent
from app.repositories.log_event_repository import LogEventRepository
from app.schemas.log_event import REQUIRED_CSV_COLUMNS
from app.utils.exceptions import InvalidCSVError, InvalidFileTypeError, MissingColumnsError

logger = logging.getLogger(__name__)

ALLOWED_EXTENSION = ".csv"
ALLOWED_CONTENT_TYPES = {"text/csv", "application/vnd.ms-excel", "application/csv"}


class LogUploadService:
    """Coordinates validation, parsing, and persistence of uploaded log files."""

    def __init__(self, repository: LogEventRepository):
        self.repository = repository

    def validate_file_type(self, filename: str | None, content_type: str | None) -> None:
        if not filename or not filename.lower().endswith(ALLOWED_EXTENSION):
            raise InvalidFileTypeError(
                f"Invalid file type. Only {ALLOWED_EXTENSION} files are accepted."
            )

        if content_type and content_type not in ALLOWED_CONTENT_TYPES and "csv" not in content_type:
            raise InvalidFileTypeError(
                f"Invalid file content type '{content_type}'. Only CSV files are accepted."
            )

    def parse_csv(self, file_bytes: bytes) -> pd.DataFrame:
        if not file_bytes:
            raise InvalidCSVError("The uploaded file is empty.")

        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except pd.errors.EmptyDataError as exc:
            raise InvalidCSVError("The uploaded CSV file has no data.") from exc
        except pd.errors.ParserError as exc:
            raise InvalidCSVError(f"The uploaded CSV file could not be parsed: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise InvalidCSVError("The uploaded file is not a valid text/CSV file.") from exc

        if df.empty:
            raise InvalidCSVError("The uploaded CSV file contains no rows.")

        return df

    def validate_columns(self, df: pd.DataFrame) -> None:
        missing = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
        if missing:
            raise MissingColumnsError(missing)

    def transform_to_models(self, df: pd.DataFrame) -> list[LogEvent]:
        df = df[REQUIRED_CSV_COLUMNS].copy()

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["is_privileged"] = df["is_privileged"].apply(self._to_bool)

        if df["timestamp"].isna().any():
            raise InvalidCSVError("One or more rows contain an invalid 'timestamp' value.")

        log_events: list[LogEvent] = []
        for row in df.to_dict(orient="records"):
            log_events.append(
                LogEvent(
                    timestamp=row["timestamp"],
                    username=str(row["username"]).strip(),
                    ip_address=str(row["ip_address"]).strip(),
                    country=str(row["country"]).strip(),
                    device=str(row["device"]).strip(),
                    login_status=str(row["login_status"]).strip(),
                    is_privileged=row["is_privileged"],
                )
            )

        return log_events

    def process_upload(self, filename: str | None, content_type: str | None, file_bytes: bytes) -> int:
        self.validate_file_type(filename, content_type)
        df = self.parse_csv(file_bytes)
        self.validate_columns(df)
        log_events = self.transform_to_models(df)

        rows_imported = self.repository.bulk_insert(log_events)
        logger.info(f"Processed upload '{filename}': {rows_imported} rows imported")
        return rows_imported

    @staticmethod
    def _to_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if pd.isna(value):
            return False
        text = str(value).strip().lower()
        return text in {"true", "1", "yes", "y"}
