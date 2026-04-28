# 腾讯云部署指南（CVM + Docker + Nginx + HTTPS）

## 目标架构

- 腾讯云 CVM（Ubuntu 22.04）
- Docker 运行 `backend_mvp`（FastAPI）
- Nginx 做 HTTPS 入口与反向代理
- 小程序访问域名示例：`https://api.your-domain.com`

## 1. 购买与准备

1. 购买腾讯云 CVM（建议上海/广州，2C2G 即可满足每天 20 次任务）
2. 安全组放行端口：`22`、`80`、`443`
3. 域名解析：`api.your-domain.com` A 记录指向 CVM 公网 IP

## 2. 服务器初始化

SSH 登录服务器后执行：

```bash
sudo bash deploy/tencentcloud/bootstrap.sh
```

如果你的代码还未上传到服务器，先上传项目目录（例如 `scp` 或 `git clone`）。

## 3. 构建并启动 API

在项目根目录执行：

```bash
docker build -t score-analysis-api:latest .
mkdir -p deploy/tencentcloud/runtime_tasks
docker compose -f deploy/tencentcloud/docker-compose.yml up -d
docker compose -f deploy/tencentcloud/docker-compose.yml ps
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 4. 配置 Nginx

1. 修改 `deploy/tencentcloud/nginx.conf` 中域名 `api.your-domain.com`
2. 拷贝配置到 Nginx：

```bash
sudo cp deploy/tencentcloud/nginx.conf /etc/nginx/conf.d/score-analysis.conf
sudo nginx -t
sudo systemctl restart nginx
```

## 5. 申请 HTTPS 证书

```bash
sudo certbot --nginx -d api.your-domain.com
```

验证：

```bash
curl https://api.your-domain.com/health
```

## 6. 小程序配置

在微信公众平台 -> 开发管理 -> 开发设置，增加以下合法域名：

- request 合法域名：`https://api.your-domain.com`
- uploadFile 合法域名：`https://api.your-domain.com`
- downloadFile 合法域名：`https://api.your-domain.com`

并修改 `miniapp_mvp/utils/api.js`：

```js
const BASE_URL = "https://api.your-domain.com";
```

## 7. 发布更新

代码更新后在服务器执行：

```bash
docker build -t score-analysis-api:latest .
docker compose -f deploy/tencentcloud/docker-compose.yml up -d
```

## 8. 常用排查命令

```bash
docker compose -f deploy/tencentcloud/docker-compose.yml logs -f
docker ps
sudo journalctl -u nginx -f
curl -v https://api.your-domain.com/health
```
