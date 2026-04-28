from pathlib import Path

from score_analysis.constants import TOP_K_COUNT, TOP_K_MIN

API_PREFIX = "/api/v1"
ALLOWED_EXTENSIONS = {".xls", ".xlsx"}

TASKS_ROOT_DIR = Path(__file__).resolve().parent.parent / "runtime_tasks"
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"
OUTPUT_FILENAME = "成绩对比.xlsx"

DEFAULT_TOP_K = TOP_K_COUNT
MIN_TOP_K = TOP_K_MIN

STATUS_PENDING = "pending"
STATUS_AWAITING_UPLOAD = "awaiting_upload"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"

FILE_ROLE_FIRST = "first"
FILE_ROLE_SECOND = "second"
ALLOWED_FILE_ROLES = {FILE_ROLE_FIRST, FILE_ROLE_SECOND}
