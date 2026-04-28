# 微信小程序 MVP（成绩对比）

## 1. 导入项目

1. 打开微信开发者工具
2. 选择 `miniapp_mvp` 目录导入
3. 在 `project.config.json` 中替换真实 `appid`

## 2. 修改后端地址

编辑 `utils/api.js`：

```js
const BASE_URL = "https://你的后端域名";
```

## 3. 页面流程

- `pages/index/index`：
  - 选择第一份文件
  - 选择第二份文件
  - 设置 TopK
  - 提交任务（走分步上传接口）

- `pages/result/result`：
  - 轮询任务状态
  - 成功后下载并打开结果 Excel

## 4. 小程序后台配置

在微信公众平台 -> 开发管理 -> 开发设置：

- request 合法域名：`https://你的后端域名`
- uploadFile 合法域名：`https://你的后端域名`
- downloadFile 合法域名：`https://你的后端域名`

注意：必须是 HTTPS 且证书有效。
