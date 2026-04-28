const API_BASE_URL = "https://www.lulusmagicbox.cloud";

const API_PREFIX = "/api/v1";

const HTTP_METHOD = {
  GET: "GET",
  POST: "POST"
};

const HEADER_KEY = {
  CONTENT_TYPE: "content-type"
};

const CONTENT_TYPE = {
  FORM: "application/x-www-form-urlencoded"
};

const ERROR_MESSAGE = {
  REQUEST_FAILED: "请求失败",
  NETWORK_FAILED: "网络请求失败",
  QUERY_TASK_FAILED: "查询任务失败",
  DOWNLOAD_RESULT_FAILED: "下载结果失败",
  UPLOAD_FILE_FAILED: "上传文件失败",
  UPLOAD_RESPONSE_INVALID: "上传返回格式异常"
};

module.exports = {
  API_BASE_URL,
  API_PREFIX,
  HTTP_METHOD,
  HEADER_KEY,
  CONTENT_TYPE,
  ERROR_MESSAGE
};

