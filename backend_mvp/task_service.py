from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from score_analysis import run_analysis

from . import config
from .task_store import TaskRecord, build_result_download_url, task_store


def validate_top_k(top_k: int) -> int:
    if top_k < config.MIN_TOP_K:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"top_k 必须大于等于 {config.MIN_TOP_K}",
        )
    return top_k


def validate_excel_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传文件缺少文件名",
        )
    extension = Path(filename).suffix.lower()
    if extension not in config.ALLOWED_EXTENSIONS:
        allowed_text = "、".join(sorted(config.ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持上传 {allowed_text} 文件",
        )
    return filename


def create_task_directories(task_id: str) -> tuple[Path, Path, Path]:
    task_dir = config.TASKS_ROOT_DIR / task_id
    input_dir = task_dir / config.INPUT_DIR_NAME
    output_dir = task_dir / config.OUTPUT_DIR_NAME
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return task_dir, input_dir, output_dir


def save_upload_file(file: UploadFile, target_path: Path) -> None:
    file.file.seek(0)
    with target_path.open("wb") as output_handle:
        output_handle.write(file.file.read())


def create_task(first_file: UploadFile, second_file: UploadFile, top_k: int) -> TaskRecord:
    top_k_value = validate_top_k(top_k)
    first_name = validate_excel_filename(first_file.filename)
    second_name = validate_excel_filename(second_file.filename)

    task_id = uuid4().hex
    task_dir, input_dir, output_dir = create_task_directories(task_id)
    first_file_path = input_dir / first_name
    second_file_path = input_dir / second_name
    output_file_path = output_dir / config.OUTPUT_FILENAME

    save_upload_file(first_file, first_file_path)
    save_upload_file(second_file, second_file_path)

    now = datetime.utcnow()
    record = TaskRecord(
        task_id=task_id,
        status=config.STATUS_PENDING,
        top_k=top_k_value,
        created_at=now,
        updated_at=now,
        task_dir=task_dir,
        first_file_path=first_file_path,
        second_file_path=second_file_path,
        output_file_path=output_file_path,
    )
    task_store.create(record)
    return record


def create_empty_task(top_k: int) -> TaskRecord:
    top_k_value = validate_top_k(top_k)
    task_id = uuid4().hex
    task_dir, _input_dir, output_dir = create_task_directories(task_id)
    now = datetime.utcnow()
    record = TaskRecord(
        task_id=task_id,
        status=config.STATUS_AWAITING_UPLOAD,
        top_k=top_k_value,
        created_at=now,
        updated_at=now,
        task_dir=task_dir,
        first_file_path=None,
        second_file_path=None,
        output_file_path=output_dir / config.OUTPUT_FILENAME,
    )
    task_store.create(record)
    return record


def _build_upload_target_path(task: TaskRecord, file_name: str) -> Path:
    input_dir = task.task_dir / config.INPUT_DIR_NAME
    input_dir.mkdir(parents=True, exist_ok=True)
    return input_dir / file_name


def upload_task_file(task_id: str, file_role: str, upload_file: UploadFile) -> TaskRecord:
    if file_role not in config.ALLOWED_FILE_ROLES:
        role_text = "、".join(sorted(config.ALLOWED_FILE_ROLES))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"file_role 仅支持 {role_text}",
        )

    task = get_task_or_404(task_id)
    if task.status in {config.STATUS_RUNNING, config.STATUS_SUCCESS}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="任务已执行或完成，不允许重新上传",
        )

    file_name = validate_excel_filename(upload_file.filename)
    target_path = _build_upload_target_path(task, file_name)
    save_upload_file(upload_file, target_path)
    updated = task_store.update_file_path(task_id, file_role=file_role, file_path=target_path)
    if updated.status == config.STATUS_PENDING:
        task_store.update_status(task_id, config.STATUS_AWAITING_UPLOAD)
        updated = get_task_or_404(task_id)
    return updated


def start_task(task_id: str) -> TaskRecord:
    task = get_task_or_404(task_id)
    if task.first_file_path is None or task.second_file_path is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="请先上传 first 与 second 两份成绩单",
        )
    if task.status in {config.STATUS_RUNNING, config.STATUS_SUCCESS}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="任务已启动或已完成")
    return task_store.update_status(task_id, config.STATUS_PENDING)


def run_task(task_id: str) -> None:
    task = task_store.get(task_id)
    if task is None:
        return
    if task.first_file_path is None or task.second_file_path is None:
        task_store.update_status(task_id, config.STATUS_FAILED, error_message="任务缺少输入文件")
        return
    task_store.update_status(task_id, config.STATUS_RUNNING)
    try:
        run_analysis(
            base_dir=task.task_dir,
            first_exam_filename=str(task.first_file_path),
            second_exam_filename=str(task.second_file_path),
            output_filename=str(task.output_file_path),
            top_k=task.top_k,
        )
    except Exception as exc:  # noqa: BLE001
        task_store.update_status(task_id, config.STATUS_FAILED, error_message=str(exc))
        return
    task_store.update_status(task_id, config.STATUS_SUCCESS)


def get_task_or_404(task_id: str) -> TaskRecord:
    task = task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return task


def build_task_payload(task: TaskRecord) -> dict[str, object]:
    download_url = None
    if task.status == config.STATUS_SUCCESS and task.output_file_path.exists():
        download_url = build_result_download_url(task.task_id)
    upload_state = {
        "first_uploaded": task.first_file_path is not None,
        "second_uploaded": task.second_file_path is not None,
    }
    return {
        "task_id": task.task_id,
        "status": task.status,
        "top_k": task.top_k,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "error_message": task.error_message,
        "result_download_url": download_url,
        "upload_state": upload_state,
    }
