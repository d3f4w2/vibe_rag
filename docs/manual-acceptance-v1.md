# V1 手工验收清单（STEP-09）

## 范围
- 确认 V1 基线在 CLI 输出、不确定性处理、失败路径诊断方面的验收行为。
- 本清单用于补充自动化测试，是关闭 STEP-09 前的必要人工验证项。

## 环境
- 工作目录：`C:\Users\ljh\Desktop\rag`
- Conda 环境：`vibe-rag`
- 命令前缀：`conda run -n vibe-rag`

## 人工场景

### M1：缺少必填染色输入时应快速失败
1. 执行：
   `conda run -n vibe-rag python -m src.cli.main --top-k 5`
2. 预期：
   - 进程退出码为 `2`。
   - `stderr` 包含 `argument error`（参数错误）。
   - 错误信息提及 `--stain-text` 或 `--stain-file`。

### M2：无效 UTF-8 染色文件应报告为参数错误
1. 创建一个包含无效 UTF-8 字节的文件（PowerShell）：
   `Set-Content -Path .\pytest_tmp_manual\manual_invalid_utf8.txt -Value ([byte[]](0xff,0xfe,0xfd)) -AsByteStream`
2. 执行：
   `conda run -n vibe-rag python -m src.cli.main --stain-file .\pytest_tmp_manual\manual_invalid_utf8.txt --top-k 5`
3. 预期：
   - 进程退出码为 `2`。
   - `stderr` 包含 `argument error`（参数错误）。
   - 错误信息包含 `UTF-8` 和 `--stain-file`。

### M3：成功查询应返回结构化 JSON
1. 前置条件：
   - 已配置 embedding provider 环境变量。
   - 检索所需的向量索引可用。
2. 执行：
   `conda run -n vibe-rag python -m src.cli.main --stain-text "manual smoke query" --top-k 5`
3. 预期：
   - 进程退出码为 `0`。
   - `stdout` 为合法 JSON，且包含键：
     - `similar_cases`
     - `tendency`
     - `reason`
     - `disclaimer`
     - `meta`
   - `meta.top_k == 5`。

### M4：运行时失败应返回运行时退出码
1. 前置条件：
   - 人为触发 API 超时（例如将 embedding endpoint 设置为不可路由地址）。
2. 执行：
   `conda run -n vibe-rag python -m src.cli.main --stain-text "timeout smoke query" --top-k 5`
3. 预期：
   - 进程退出码为 `1`。
   - `stderr` 包含 `runtime error`（运行时错误）。

## 最终通过标准
- M1 与 M2 在任意本地机器上必须通过。
- M3 与 M4 在满足对应外部前置条件时通过。
- 结果应与自动化基线一致：
  `conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221`
