---
name: dify-workflow-editor
description: Read, edit, create, run, publish, and observe Dify apps/workflows, and manage models/knowledge-bases — via Dify's Console + Service API. Use when the user wants to programmatically list/find/modify/create/run/debug a Dify workflow (change prompts, model params, nodes, edges), build a RAG knowledge base, install a model plugin + set its key, or inspect run logs / node-level outputs. Requires a self-hosted Dify (email/password login) or manually-supplied browser cookies for Dify Cloud.
---

# Dify Workflow Editor

通过 Dify 的 **Console API + Service API** 全面操控自托管 Dify：列/找/改/建/运行/调试工作流、建知识库、装模型配 key、看运行日志与节点级输出。

## 何时用
用户想：找/改/建/跑某个 Dify 工作流、看工作流跑挂在哪个节点、建 RAG 知识库、装模型+配 key、把草稿发布。

## 前置条件（环境变量，二选一）
- **自托管（推荐）**：`DIFY_BASE`（如 `http://your-dify`，不带 `/console/api`）+ `DIFY_EMAIL` + `DIFY_PASSWORD`
- **Dify Cloud（手动）**：`DIFY_BASE` + `DIFY_COOKIE` + `DIFY_CSRF`（DevTools 抓）
- 多实例：切这组环境变量即指向不同 Dify。没设就先停下让用户设。

## 标准工作流（建/改前必做）
1. `whoami` 验证登录 → 2. `resources` 看有哪些可用模型/知识库/工具 → 3. `list [--name/--mode/--tag]` 定位目标 app → 4. `export <id>` 导出 DSL → 5. **改之前读 [`references/dify-dsl.md`](references/dify-dsl.md)**（依赖块/引号/节点字段/校验清单）→ 6. 精准改 + 自检 → 7. `import` 进草稿 → 8. `run` 试跑；挂了用 `logs`+`node-outputs` 看节点级报错、自修复 → 9.（问过用户）`publish`。

## 全部命令（`python scripts/dify_admin.py <命令>`）
**应用**：`whoami` · `list --name/--mode/--tag/--page` · `describe <id>`(看输入字段) · `export <id> [--out f]` · `import <id> --file f` / `import --new --name N --file f` · `publish <id>` · `run <id> [--inputs '{}'] [--query ..] [--file f --file-var v] [--stream]`(自动按类型路由) · `stop <id> <task_id>` · `rename <id> <name>` · `copy <id> [--name]` · `delete-app <id>`
**组织/定位**：`tag-list` · `tag-create <name>` · `tag-bind <id> <tag>` · `tag-delete <tag>`（多工作流时先打标签，再 `list --tag` 定位）
**观测/调试**：`runs <id>`(画布调试运行) · `logs <id> [--keyword --status]`(API/线上运行) · `run-detail <id> <run_id>` · `node-outputs <id> <run_id>`(**逐节点输入/输出，排错核心**)
**资源/地基**：`resources` · `install-plugin <org/name>` · `set-model-key <provider> --key k` · `config-model <id> --file f`(改基础应用)
**HITL**：`resume <form_token> [--inputs] [--action]`(续接 human-input 暂停的工作流)
**知识库**：`dataset-list` · `dataset-create <name> --indexing economy|high_quality [--embedding-provider P --embedding-model M]` · `dataset-update <id>` · `dataset-delete <id>` · `dataset-add-text/-add-file` · `dataset-docs <id>` · `dataset-doc-delete <id> <doc>` · `dataset-doc-status <id> <batch>`(索引进度) · `dataset-retrieve <id> --query Q [--method keyword/semantic/hybrid/full_text] [--top-k N] [--rerank-provider/--rerank-model] [--filter JSON]` · `dataset-seg-list/-seg-add/-seg-update/-seg-delete`

## 关键认知
- **模型两层**：`install-plugin`+`set-model-key` 配在供应商层（一次，全局）；工作流 DSL 里只**引用**模型名，**不写 key**。
- **建/改工作流前先 `resources`**：只引用目标实例**已存在**的模型/知识库/工具，否则导入的工作流引用空。
- **运行历史**：画布调试 → `runs`；API/线上触发 → `logs`（再用其 `run=<id>` 跑 `node-outputs`）。
- **DSL 生成两大坑**（见 references）：缺顶层 `dependencies` 块 + 节点 id 没加引号。

## 安全红线
- **`publish` 前必须用户确认**（改的是线上工作流）。
- `export`/`config-model` 等含密钥，导出文件用完即删。
- Console API 是 Dify **内部接口、不保证稳定**，升级 Dify 可能变 → pin 版本、升级回归。
