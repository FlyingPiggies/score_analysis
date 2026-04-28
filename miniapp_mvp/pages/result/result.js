const { downloadResult, getTaskStatus } = require("../../utils/api");

Page({
  data: {
    taskId: "",
    status: "pending",
    errorMessage: "",
    pollingTimer: null,
    downloading: false
  },

  onLoad(options) {
    const taskId = options.taskId || "";
    if (!taskId) {
      wx.showToast({ title: "缺少任务ID", icon: "none" });
      return;
    }
    this.setData({ taskId });
    this.startPolling();
  },

  onUnload() {
    this.stopPolling();
  },

  startPolling() {
    this.fetchStatus();
    const timer = setInterval(() => {
      this.fetchStatus();
    }, 2000);
    this.setData({ pollingTimer: timer });
  },

  stopPolling() {
    const { pollingTimer } = this.data;
    if (pollingTimer) {
      clearInterval(pollingTimer);
      this.setData({ pollingTimer: null });
    }
  },

  onRefreshStatus() {
    this.fetchStatus();
  },

  fetchStatus() {
    const { taskId } = this.data;
    getTaskStatus(taskId)
      .then((payload) => {
        this.setData({
          status: payload.status,
          errorMessage: payload.error_message || ""
        });
        if (payload.status === "success" || payload.status === "failed") {
          this.stopPolling();
        }
      })
      .catch((error) => {
        wx.showToast({ title: error.message, icon: "none" });
      });
  },

  onDownloadResult() {
    const { taskId } = this.data;
    this.setData({ downloading: true });
    downloadResult(taskId)
      .then((tempFilePath) => {
        wx.openDocument({
          filePath: tempFilePath,
          fileType: "xlsx",
          showMenu: true
        });
      })
      .catch((error) => {
        wx.showToast({ title: error.message, icon: "none" });
      })
      .finally(() => {
        this.setData({ downloading: false });
      });
  }
});
