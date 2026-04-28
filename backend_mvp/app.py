from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from . import config
from .schemas import TaskCreateResponse, TaskStatusResponse
from .task_service import (
    build_task_payload,
    create_empty_task,
    create_task,
    get_task_or_404,
    run_task,
    start_task,
    upload_task_file,
)


app = FastAPI(title="成绩对比服务 MVP", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(f"{config.API_PREFIX}/tasks", response_model=TaskCreateResponse)
def create_analysis_task(
    background_tasks: BackgroundTasks,
    first_file: UploadFile = File(..., description="第一份成绩单"),
    second_file: UploadFile = File(..., description="第二份成绩单"),
    top_k: int = Form(default=config.DEFAULT_TOP_K, description="每个指标TopK"),
) -> TaskCreateResponse:
    task = create_task(first_file=first_file, second_file=second_file, top_k=top_k)
    background_tasks.add_task(run_task, task.task_id)
    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="任务已创建，正在排队执行",
    )


@app.post(f"{config.API_PREFIX}/tasks/init", response_model=TaskCreateResponse)
def init_analysis_task(top_k: int = Form(default=config.DEFAULT_TOP_K, description="每个指标TopK")) -> TaskCreateResponse:
    task = create_empty_task(top_k=top_k)
    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="任务已初始化，请上传两份成绩单后启动任务",
    )


@app.post(f"{config.API_PREFIX}/tasks/{{task_id}}/upload", response_model=TaskStatusResponse)
def upload_analysis_file(
    task_id: str,
    file_role: str = Form(..., description="first 或 second"),
    file: UploadFile = File(..., description="成绩单文件"),
) -> TaskStatusResponse:
    task = upload_task_file(task_id=task_id, file_role=file_role, upload_file=file)
    return TaskStatusResponse(**build_task_payload(task))


@app.post(f"{config.API_PREFIX}/tasks/{{task_id}}/start", response_model=TaskCreateResponse)
def start_analysis_task(task_id: str, background_tasks: BackgroundTasks) -> TaskCreateResponse:
    task = start_task(task_id)
    background_tasks.add_task(run_task, task.task_id)
    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="任务已启动",
    )


@app.get(f"{config.API_PREFIX}/tasks/{{task_id}}", response_model=TaskStatusResponse)
def get_analysis_task(task_id: str) -> TaskStatusResponse:
    task = get_task_or_404(task_id)
    return TaskStatusResponse(**build_task_payload(task))


@app.get(f"{config.API_PREFIX}/tasks/{{task_id}}/result")
def download_analysis_result(task_id: str) -> FileResponse:
    task = get_task_or_404(task_id)
    if task.status != config.STATUS_SUCCESS or not task.output_file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="结果文件尚未生成")
    return FileResponse(
        path=task.output_file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=config.OUTPUT_FILENAME,
    )
