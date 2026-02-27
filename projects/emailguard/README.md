# EmailGuard

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

**自托管邮件验证服务** - 开发者友好的邮箱地址验证 API

## ✨ 特性

- 🔒 **完全自托管** - 数据不离开你的服务器，满足 GDPR 等隐私合规要求
- ⚡ **高性能验证** - 语法验证 + DNS MX 验证，平均响应 <200ms
- 🐳 **一键 Docker 部署** - 分钟级完成部署
- 📦 **RESTful API** - 简单易用的 HTTP 接口，支持批量验证
- 🔧 **无需外部依赖** - 不依赖第三方 API，核心验证逻辑完全自主

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 拉取镜像（待发布）
docker pull emailguard/emailguard:latest

# 运行服务
docker run -d -p 8000:8000 emailguard/emailguard:latest

# 或使用 docker-compose
docker-compose up -d
```

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/auto-company/emailguard.git
cd emailguard

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger API 文档

## 📖 API 文档

### 验证单个邮箱

```bash
curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**响应：**

```json
{
  "email": "user@example.com",
  "valid": true,
  "reason": "valid",
  "checks": {
    "syntax": true,
    "mx": true,
    "disposable": false,
    "role": false
  },
  "score": 95,
  "suggestion": null
}
```

### 批量验证

```bash
curl -X POST http://localhost:8000/v1/verify/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@gmail.com", "admin@company.com", "test@tempmail.com"]}'
```

**响应：**

```json
{
  "results": [
    {
      "email": "user1@gmail.com",
      "valid": true,
      "score": 95,
      "checks": {"syntax": true, "mx": true, "disposable": false, "role": false}
    },
    {
      "email": "admin@company.com",
      "valid": true,
      "score": 85,
      "checks": {"syntax": true, "mx": true, "disposable": false, "role": true}
    },
    {
      "email": "test@tempmail.com",
      "valid": false,
      "score": 30,
      "checks": {"syntax": true, "mx": true, "disposable": true, "role": false}
    }
  ],
  "summary": {
    "total": 3,
    "valid": 2,
    "invalid": 1
  }
}
```

### 健康检查

```bash
curl http://localhost:8000/health
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/verify` | POST | 验证单个邮箱 |
| `/v1/verify/batch` | POST | 批量验证（最多 1000 个） |
| `/health` | GET | 服务健康检查 |
| `/v1/disposable-domains` | GET | 一次性邮箱域名列表 |
| `/v1/role-prefixes` | GET | 角色邮箱前缀列表 |

## 🔍 验证逻辑

| 检查项 | 说明 | 对 score 的影响 |
|--------|------|-----------------|
| 语法验证 | RFC 5322 标准格式检查 | 通过 +40 |
| DNS MX | 检查域名 MX 记录是否存在 | 通过 +30 |
| 一次性邮箱 | 检测临时邮箱服务域名 | 通过 +25 |
| 角色邮箱 | 检测 admin@, info@ 等角色邮箱 | 非角色 +5 |

**Score 范围**: 0-100，建议 80+ 为有效邮箱

## 🛠️ 配置

通过环境变量配置（前缀 `EMAILGUARD_`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `EMAILGUARD_DEBUG` | false | 调试模式 |
| `EMAILGUARD_RATE_LIMIT_REQUESTS` | 100 | 速率限制请求数 |
| `EMAILGUARD_RATE_LIMIT_WINDOW` | 60 | 速率限制窗口（秒） |
| `EMAILGUARD_DNS_TIMEOUT` | 5.0 | DNS 查询超时（秒） |
| `EMAILGUARD_MAX_BATCH_SIZE` | 1000 | 批量验证最大数量 |

## 📦 技术栈

- **Python 3.11+** - 现代 Python 特性支持
- **FastAPI** - 高性能异步 Web 框架
- **dnspython** - DNS 查询库
- **Pydantic** - 数据验证和序列化
- **Docker** - 容器化部署

## 🧪 测试

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/ -v

# 测试覆盖率
python -m pytest tests/ --cov=app --cov-report=html
```

## 📄 License

MIT License - 可自由用于商业项目

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Built with ❤️ by [Auto Company](https://github.com/auto-company)**