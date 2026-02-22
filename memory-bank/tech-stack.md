# Tech Stack（V1）

## 1. 项目约束与目标
基于 `memory-bank/prd.md`，当前 V1 目标是构建“病例检索 + 参考倾向输出”的 RAG 系统，特点如下：
1. 单机运行，优先本地 CLI。
2. 以文本检索为主，图像仅做证据引用。
3. 嵌入模型与生成模型使用不同厂商、不同 API，需分开配置。
4. 当前阶段避免复杂化选型，先保证可用、可解释、可迭代。

## 2. 选型原则
1. 最简单但最稳健：先跑通主流程，再扩展能力。
2. 低门槛：避免引入你当前不熟悉的数据库和服务。
3. 可追溯：所有结果可回溯到病例与证据片段。
4. 可替换：后续可逐步替换组件，不一次性绑定重架构。

## 3. 技术栈总览（不锁定版本）
1. 运行环境：`conda`
2. 语言：`Python`
3. RAG 编排：`LangChain`（核心）
4. 向量存储：`Chroma`（本地持久化）
5. 元数据存储：`JSONL` 文件
6. HTTP 请求：`httpx`（调用第三方云 API）
7. 配置管理：`pydantic-settings`
8. 测试：`pytest`
9. 代码质量：`ruff`
10. 日志：`logging`（Python 标准库）

## 4. 数据与检索方案（V1）
1. 数据来源：`data/HSIL/*` 与 `data/LSIL/*`
2. 元数据：解析后写入 `JSONL`（`case_id`、`label`、路径、时间等）
3. 检索模式：`vector_only`
4. 检索流程：文本清洗 -> 向量化 -> Chroma 检索 -> 返回 Top-K -> 生成解释
5. 文本清洗：至少去除 `0x7F` 控制字符，统一 UTF-8 读取

说明：V1 暂不引入关键词检索（如 BM25/FTS），先保证向量检索主链路稳定。

## 5. 模型与 API 配置规范（双供应商）
嵌入模型与生成模型必须独立配置，禁止混用单一配置项。

```yaml
providers:
  embedding:
    provider: "<embedding_vendor>"
    base_url: "<embedding_api_base>"
    api_key_env: "EMBEDDING_API_KEY"
    model: "<embedding_model>"
    timeout_sec: 30
    max_retries: 3
  generation:
    provider: "<generation_vendor>"
    base_url: "<generation_api_base>"
    api_key_env: "GENERATION_API_KEY"
    model: "<generation_model>"
    timeout_sec: 60
    max_retries: 3
retrieval:
  mode: "vector_only"
  vector_store: "chroma"
  top_k: 5
ingestion:
  data_root: "./data"
  metadata_store: "jsonl"
  text_encoding: "utf-8"
  remove_control_chars: ["0x7F"]
```

## 6. 工程基线（最小但稳健）
1. 入口形态：CLI（命令入口细化留到 implementation 阶段）
2. 错误处理：API 超时与重试（按配置）
3. 日志：记录 query、召回病例、倾向结果、关键错误
4. 测试基线：
   - 数据解析测试
   - 文本清洗测试
   - 检索返回结构测试
   - API 配置加载测试

## 7. 依赖策略（当前决议）
1. 依赖库名称先确定，不指定版本号。
2. 如出现依赖冲突，后续单独处理并补充约束文档。
3. 当前阶段不做锁版本文件（如完整 lockfile）要求。

## 8. 本阶段不引入技术
1. 不引入 SQLite / PostgreSQL / MySQL
2. 不引入 Qdrant / Milvus / Elasticsearch
3. 不引入 FastAPI 或其他服务化框架
4. 不引入 Docker-first 部署要求
5. 不引入图像向量检索链路（图像仅证据引用）
6. 不引入 Agent、LangGraph、多代理编排
7. 不引入重型工作流编排器（如 Airflow、Celery）

## 9. 待定项（TBD）
1. PDF 处理细化策略：当前仅定义“可选抽取、失败不阻塞主流程”。
2. CLI 命令命名规范与参数标准：implementation 阶段确定。
3. 是否在后续增加关键词检索混合召回：feature 阶段评估。

## 10. Provider Env Mapping (Implemented 2026-02-22)
1. Embedding path: `EMBEDDING_API_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_TIMEOUT_SEC`, `EMBEDDING_MAX_RETRIES`.
2. Generation path: `GENERATION_API_BASE_URL`, `GENERATION_API_KEY`, `GENERATION_MODEL`, `GENERATION_TIMEOUT_SEC`, `GENERATION_MAX_RETRIES`.
3. `src/infra/api_client.py` routes `embed_texts` and `generate_reasoning` to different provider endpoints by design.

## 11. Localization & Beginner UX Policy（STEP-10）
1. 文案策略：
   - 用户可见内容默认中文优先。
   - 保留必要英文关键词/错误码，便于日志检索与跨团队排障。
2. 兼容策略：
   - 不破坏现有英文接口契约。
   - 允许新增中英并行参数与提示，但需保证旧调用路径可用。
3. 测试策略：
   - 对用户可见报错优先断言“错误码/关键字段/退出码”，降低整句文案耦合。
   - 文案变更不应引起无关功能回归。
4. 执行边界（本轮）：
   - STEP-10 为 docs-only，同步策略不落地代码实现。
   - 代码与测试实现留待后续实现轮次，在同一策略下推进。
