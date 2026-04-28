from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock

from . import config


@dataclass
class TaskRecord:
    task_id: str
    status: str
    top_k: int
    created_at: datetime
    updated_at: datetime
    task_dir: Path
    first_file_path: Path | None
    second_file_path: Path | None
    output_file_path: Path
    error_message: str | None = None


class InMemoryTaskStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._tasks: dict[str, TaskRecord] = {}

    def create(self, record: TaskRecord) -> None:
        with self._lock:
            self._tasks[record.task_id] = record

    def get(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: str, error_message: str | None = None) -> TaskRecord:
        with self._lock:
            record = self._tasks[task_id]
            record.status = status
            record.updated_at = datetime.utcnow()
            record.error_message = error_message
            return record

    def update_file_path(self, task_id: str, file_role: str, file_path: Path) -> TaskRecord:
        with self._lock:
            record = self._tasks[task_id]
            if file_role == config.FILE_ROLE_FIRST:
                record.first_file_path = file_path
            else:
                record.second_file_path = file_path
            record.updated_at = datetime.utcnow()
            return record


task_store = InMemoryTaskStore()


def build_result_download_url(task_id: str) -> str:
    return f"{config.API_PREFIX}/tasks/{task_id}/result"
