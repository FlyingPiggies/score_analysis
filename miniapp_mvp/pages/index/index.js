const { createTask } = require("../../utils/api");

Page({
  data: {
    firstFilePath: "",
    secondFilePath: "",
    firstFileName: "",
    secondFileName: "",
    topK: 10,
    submitting: false
  },

  pickFile() {
    return new Promise((resolve, reject) => {
      wx.chooseMessageFile({
        count: 1,
        type: "file",
        extension: ["xls", "xlsx"],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0];
          if (!file) {
            reject(new Error("未选择文件"));
            return;
          }
          resolve(file);
        },
        fail: () => reject(new Error("文件选择失败"))
      });
    });
  },

  onPickFirstFile() {
    this.pickFile()
      .then((file) => {
        this.setData({
          firstFilePath: file.path,
          firstFileName: file.name
        });
      })
      .catch((error) => {
        wx.showToast({ title: error.message, icon: "none" });
      });
  },

  onPickSecondFile() {
    this.pickFile()
      .then((file) => {
        this.setData({
          secondFilePath: file.path,
          secondFileName: file.name
        });
      })
      .catch((error) => {
        wx.showToast({ title: error.message, icon: "none" });
      });
  },

  onTopKChange(event) {
    this.setData({ topK: Number(event.detail.value) });
  },

  onSubmitTask() {
    const { firstFilePath, secondFilePath, topK } = this.data;
    if (!firstFilePath || !secondFilePath) {
      wx.showToast({ title: "请先选择两份成绩单", icon: "none" });
      return;
    }

    this.setData({ submitting: true });
    createTask(firstFilePath, secondFilePath, topK)
      .then((payload) => {
        wx.navigateTo({
          url: `/pages/result/result?taskId=${payload.task_id}`
        });
      })
      .catch((error) => {
        wx.showToast({ title: error.message, icon: "none" });
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  }
});
