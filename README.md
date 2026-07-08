# Stock Analyzer

Stock Analyzer 是一个面向 A 股数据采集、分析和展示的本地化平台。系统通过采集服务提前同步行情、指数、板块、企业信息、财务、股东高管等数据，API 服务只读取本地数据库并为前端提供稳定的查询接口。

## 当前架构

```text
Miana / Tushare / AkShare / Eastmoney
                |
                v
        collector service
                |
                v
              MySQL
                |
                v
          api service
                |
                v
             frontend
```

核心原则：

- `collector` 负责所有远程数据采集、定时任务、补采、重试和数据新鲜度维护。
- `api` 只负责读取本地数据、返回页面所需数据和数据状态。
- 用户点击页面时不直接请求远程数据源。
- 缺失数据通过 `sync_requests` 入队，由 collector 异步处理。
- 数据新鲜度通过 `dataset_freshness` 记录，避免反复采集已知为空的数据。

## 主要功能

- A 股股票列表、K 线、指标、信号和筛选结果。
- 行情中心：指数概览、板块热度、涨跌幅榜和成交额排行。
- 企业信息：公司资料、股本、公司行动、股东、高管、薪酬、财务报表、财务指标、资金流。
- 数据中心：同步任务、覆盖率、采集请求和数据状态。
- collector/API 服务拆分，支持本地 Docker Compose 运行。

## 项目结构

```text
stock_analyzer_app/       Python 应用源码
  api/                    FastAPI 接口
  data_provider/          数据源适配器
  storage/                MySQL 和本地仓储
  sync/                   同步 pipeline 与任务状态
  collector.py            数据采集服务
db/migrations/            数据库迁移
public/                   前端静态资源
scripts/                  本地初始化、迁移、种子、部署脚本
tests/                    自动化测试
docs/                     设计文档和工作记录
miana-api.md              Miana 接口文档
docker-compose.yml        本地 MySQL/API/collector 编排
```

## 环境要求

- Windows PowerShell
- Docker Desktop
- Python 3.12
- MySQL 8.4（Docker Compose 会自动启动）

## 配置

复制 `.env.example` 为 `.env`，并根据需要填写 provider token。

关键配置：

```text
STOCK_ANALYZER_DB_HOST=mysql
STOCK_ANALYZER_DB_NAME=stock_analyzer
STOCK_ANALYZER_DB_USER=stock_analyzer
STOCK_ANALYZER_DB_PASSWORD=change-me
STOCK_ANALYZER_MIANA_TOKEN=
STOCK_ANALYZER_MIANA_BASE_URL=http://124.222.142.232:9876/api
STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE=500
STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE=5
STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS=7
```

说明：

- provider token 只应提供给 collector。
- API 服务不需要 Miana/Tushare/AkShare 凭证。
- 本地开发时 `docker-compose.yml` 会把源码挂载进容器，代码改动后通常不需要重建镜像。

## 快速启动

启动数据库、API 和 collector：

```powershell
docker compose up -d --no-build mysql api collector
```

查看服务状态：

```powershell
docker compose ps -a
```

访问应用：

```text
http://127.0.0.1:8000
```

如果需要初始化数据库：

```powershell
scripts\migrate_db.ps1
scripts\seed_db.ps1
```

## 运行模式

API 模式：

```powershell
python -m stock_analyzer_app api
```

Collector 模式：

```powershell
python -m stock_analyzer_app collector
```

单次采集处理：

```powershell
python -m stock_analyzer_app collect --once --limit 10
```

## 数据采集说明

API 创建采集请求后会写入 `sync_requests`，collector 按优先级处理。

常见请求：

- `full_daily_pipeline`：日线、复权、分析数据。
- `fundamental_refresh_pipeline`：企业信息、股东高管、财务等。
- `market_structure_pipeline`：指数、板块、结构化市场数据。

企业信息补采策略：

- 用户打开股票详情并请求缺失企业信息时，API 创建高优先级 on-demand 请求。
- 同一股票已有 `pending` 或 `claimed` 请求时不会重复创建。
- 最近 `STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS` 天已经尝试过的股票不会重复补采。
- 自动补采批次由 `STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE` 控制。

## 常用排障命令

查看队列：

```powershell
docker compose exec -T mysql mysql -ustock_analyzer -pchange-me stock_analyzer -e "SELECT status, request_type, reason, COUNT(*) cnt FROM sync_requests GROUP BY status, request_type, reason ORDER BY status, request_type, reason;"
```

查看数据新鲜度：

```powershell
docker compose exec -T mysql mysql -ustock_analyzer -pchange-me stock_analyzer -e "SELECT dataset, status, COUNT(*) cnt, MAX(updated_at) latest_update FROM dataset_freshness GROUP BY dataset, status ORDER BY dataset, status;"
```

确认容器加载的是当前源码：

```powershell
docker compose exec -T api python -c "import importlib; m=importlib.import_module('stock_analyzer_app.api.app'); print(hasattr(m, '_enqueue_enterprise_on_demand_request'))"
docker compose exec -T collector python -c "import stock_analyzer_app.collector as c; print(hasattr(c.CollectorService, '_recent_enterprise_attempt'))"
```

## 测试

本地 Docker 测试和运行中的 collector 可能共用同一个 MySQL。跑全量测试前建议先暂停 collector：

```powershell
docker compose stop collector
docker compose run --rm -v "${PWD}:/work" -w /work api python -m pytest -q
docker compose up -d --no-build collector
```

最近一次完整验证结果记录在：

```text
docs/WORK_RECORD.md
```

## 重要文档

- `docs/WORK_RECORD.md`：最近工作记录和下次继续入口。
- `docs/superpowers/specs/2026-07-08-collector-service-detailed-design.md`：collector 服务详细设计。
- `docs/superpowers/specs/2026-07-07-data-collector-api-service-split-design.md`：API/collector 拆分设计。
- `docs/superpowers/plans/2026-07-07-collector-api-service-split-implementation.md`：拆分实现计划。
- `docs/superpowers/specs/2026-07-07-miana-api-gap-next-version-design.md`：Miana 接口能力补齐设计。

## 下一步建议

1. 为 `sync_requests` 增加 claim 超时恢复。
2. 增加请求重试次数、下次重试时间和取消能力。
3. 增加 collector dataset manifest，用配置驱动每日覆盖率。
4. 在数据中心展示 collector backlog、stale dataset 和 stuck request。
5. 统一所有可选数据接口的 `data_status` 响应。
6. 增加 provider call log，记录请求速率、耗时、空数据和失败原因。
