from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreateResponse(BaseModel):
    task_id: str = Field(..., description="任务唯一标识")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="任务创建结果说明")


class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="任务唯一标识")
    status: str = Field(..., description="任务状态")
    top_k: int = Field(..., description="TopK配置")
    created_at: datetime = Field(..., description="任务创建时间")
    updated_at: datetime = Field(..., description="任务更新时间")
    error_message: str | None = Field(default=None, description="失败原因")
    result_download_url: str | None = Field(default=None, description="结果下载地址")
    upload_state: dict[str, bool] = Field(..., description="文件上传状态")
