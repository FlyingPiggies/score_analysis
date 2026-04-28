# 成绩对比后端 MVP（FastAPI）

## 1. 安装依赖

```bash
py -m pip install -r requirements-backend.txt
```

## 2. 启动服务

```bash
py -m uvicorn backend_mvp.app:app --host 0.0.0.0 --port 8000 --reload
```

## 3. Docker 启动（云部署推荐）

```bash
docker build -t score-analysis-api .
docker run -d --name score-analysis-api -p 8000:8000 score-analysis-api
```

## 4. API 说明

- `POST /api/v1/tasks`
  - 表单字段：
    - `first_file`: 第一份成绩单（`.xls/.xlsx`）
    - `second_file`: 第二份成绩单（`.xls/.xlsx`）
    - `top_k`: 可选，默认 `10`
  - 返回：`task_id`

- `GET /api/v1/tasks/{task_id}`
  - 查询任务状态与结果下载地址

- `GET /api/v1/tasks/{task_id}/result`
  - 下载结果文件（任务成功后）

### 小程序友好的分步上传接口

- `POST /api/v1/tasks/init`
  - 表单字段：
    - `top_k`: 可选，默认 `10`
  - 返回：`task_id`

- `POST /api/v1/tasks/{task_id}/upload`
  - 表单字段：
    - `file_role`: `first` 或 `second`
    - `file`: 单个成绩单文件（`.xls/.xlsx`）
  - 返回：任务状态（含上传进度）

- `POST /api/v1/tasks/{task_id}/start`
  - 启动任务（需先上传两份文件）

- `GET /api/v1/tasks/{task_id}`
  - 查询任务状态（含 `upload_state`）

- `GET /api/v1/tasks/{task_id}/result`
  - 下载结果文件

## 5. 本地任务目录

- 运行时文件会写入：`runtime_tasks/<task_id>/`
  - `input/`: 上传的两份成绩单
  - `output/成绩对比.xlsx`: 分析结果

## 6. 腾讯云部署

请参考：

- `deploy/tencentcloud/README.md`
- `deploy/tencentcloud/docker-compose.yml`
- `deploy/tencentcloud/nginx.conf`
- `deploy/tencentcloud/bootstrap.sh`
