const {
  API_BASE_URL,
  API_PREFIX,
  HTTP_METHOD,
  HEADER_KEY,
  CONTENT_TYPE,
  ERROR_MESSAGE
} = require("../config/api");

function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

function postForm(path, formData = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(path),
      method: HTTP_METHOD.POST,
      header: {
        [HEADER_KEY.CONTENT_TYPE]: CONTENT_TYPE.FORM
      },
      data: formData,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject(new Error(res.data.detail || ERROR_MESSAGE.REQUEST_FAILED));
      },
      fail: () => reject(new Error(ERROR_MESSAGE.NETWORK_FAILED))
    });
  });
}

function initTask(topK) {
  return postForm(`${API_PREFIX}/tasks/init`, { top_k: String(topK) });
}

function uploadTaskFile(taskId, fileRole, filePath) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: buildUrl(`${API_PREFIX}/tasks/${taskId}/upload`),
      filePath,
      name: "file",
      formData: { file_role: fileRole },
      success: (res) => {
        try {
          const payload = JSON.parse(res.data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(payload);
            return;
          }
          reject(new Error(payload.detail || ERROR_MESSAGE.UPLOAD_FILE_FAILED));
        } catch (error) {
          reject(new Error(ERROR_MESSAGE.UPLOAD_RESPONSE_INVALID));
        }
      },
      fail: () => reject(new Error(ERROR_MESSAGE.NETWORK_FAILED))
    });
  });
}

function createTask(firstFilePath, secondFilePath, topK) {
  return initTask(topK)
    .then((taskPayload) => uploadTaskFile(taskPayload.task_id, "first", firstFilePath).then(() => taskPayload))
    .then((taskPayload) => uploadTaskFile(taskPayload.task_id, "second", secondFilePath).then(() => taskPayload))
    .then((taskPayload) =>
      postForm(`${API_PREFIX}/tasks/${taskPayload.task_id}/start`).then((startPayload) => ({
        task_id: startPayload.task_id
      }))
    );
}

function getTaskStatus(taskId) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(`${API_PREFIX}/tasks/${taskId}`),
      method: HTTP_METHOD.GET,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject(new Error(res.data.detail || ERROR_MESSAGE.QUERY_TASK_FAILED));
      },
      fail: () => reject(new Error(ERROR_MESSAGE.NETWORK_FAILED))
    });
  });
}

function downloadResult(taskId) {
  return new Promise((resolve, reject) => {
    wx.downloadFile({
      url: buildUrl(`${API_PREFIX}/tasks/${taskId}/result`),
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.tempFilePath);
          return;
        }
        reject(new Error(ERROR_MESSAGE.DOWNLOAD_RESULT_FAILED));
      },
      fail: () => reject(new Error(ERROR_MESSAGE.NETWORK_FAILED))
    });
  });
}

module.exports = {
  API_BASE_URL,
  createTask,
  getTaskStatus,
  downloadResult
};
