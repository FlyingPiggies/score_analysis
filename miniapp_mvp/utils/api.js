const BASE_URL = "https://请替换为你的后端域名";

const API_PREFIX = "/api/v1";

function buildUrl(path) {
  return `${BASE_URL}${path}`;
}

function postForm(path, formData = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(path),
      method: "POST",
      header: {
        "content-type": "application/x-www-form-urlencoded"
      },
      data: formData,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject(new Error(res.data.detail || "请求失败"));
      },
      fail: () => reject(new Error("网络请求失败"))
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
          reject(new Error(payload.detail || "上传文件失败"));
        } catch (error) {
          reject(new Error("上传返回格式异常"));
        }
      },
      fail: () => reject(new Error("网络请求失败"))
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
      method: "GET",
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject(new Error(res.data.detail || "查询任务失败"));
      },
      fail: () => reject(new Error("网络请求失败"))
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
        reject(new Error("下载结果失败"));
      },
      fail: () => reject(new Error("网络请求失败"))
    });
  });
}

module.exports = {
  BASE_URL,
  createTask,
  getTaskStatus,
  downloadResult
};
