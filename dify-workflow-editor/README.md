# dify-workflow-editor —— 上手与分享说明

> 一个 **Claude Code 技能(skill)**：让 Claude(AI agent)用大白话指令，**编程式全面操控一台 Dify** —— 找/改/建/跑/调试工作流、建 RAG 知识库、装模型配 key、看运行日志与逐节点输出。

---

## 0. 这个文件夹有什么
```
dify-workflow-editor/
├── README.md             ← 你正在看的这份（上手 + 分享说明）
├── SKILL.md              ← 给 Claude 读的说明书（触发条件 / 标准流程 / 安全红线）
├── scripts/dify_admin.py ← 命令行工具（登录 + 全部 ~38 个命令）
└── references/dify-dsl.md ← Dify 工作流 DSL(YAML) 结构速查 + 强校验清单
```

## 1. 接收者怎么装（3 步）
1. **放对位置**：把整个 `dify-workflow-editor` 文件夹放到你的 `~/.claude/skills/`
   （Windows：`C:\Users\<你>\.claude\skills\dify-workflow-editor\`）。重开 Claude Code 即识别。
2. **装依赖**：需要 Python 3.8+ 和 requests：`pip install requests pyyaml`
3. **设连接（环境变量）**：见下一节。设好后跟 Claude 说"用 dify-workflow-editor 列出工作流"即可。

## 2. 连接的 Dify（云服务器）+ 登录账号
本 skill 连的是部署在**阿里云服务器**上的自托管 Dify：

| 项 | 值 |
|---|---|
| **Dify 网址** | `http://47.106.203.137` （浏览器打开可看后台） |
| **登录邮箱** | `2761663493@qq.com` |
| **登录密码** | `Asdlkj20051119` |

**环境变量这样设**（PowerShell，临时；永久可写进系统环境变量）：
```powershell
$env:DIFY_BASE="http://47.106.203.137"
$env:DIFY_EMAIL="2761663493@qq.com"
$env:DIFY_PASSWORD="Asdlkj20051119"
```
> macOS/Linux 用 `export DIFY_BASE=... DIFY_EMAIL=... DIFY_PASSWORD=...`

> ⚠️ **安全须知（重要，分享前务必读）**
> - 上面是**管理员账号**，谁拿到这份文档就能**完全控制这台 Dify**（建/删工作流、看所有数据）。
> - **更稳妥的做法**：在 Dify 后台「设置 → 成员」给每个人**单独邀请一个成员账号**，别共用管理员；本文档里就只留网址，账号各自发。
> - 这个密码**别和服务器 SSH 密码用同一个**；若已泄露请尽快在 Dify「设置 → 账户」改掉。
> - 这份 README 含明文密码，**只在可信范围内分享**，别传公开仓库/群。

## 3. 怎么用：跟 Claude 说人话即可
你不用记命令，直接说需求，Claude 读到 skill 后自动执行。例如：
- "列出我 Dify 里所有工作流" / "找做客服的那个工作流"
- "把『科技新闻摘要』的提示词改成只输出 3 条要点，然后发布"
- "建一个工作流：输入文章 → DeepSeek 生成 3 个标题 → 输出，并跑一遍"
- "某工作流跑挂了，看看是哪个节点出错"
- "把这份文档建成知识库，问它『XX 是什么』"

## 4. 全部功能（~38 个命令，6 类）
命令行直跑：`python scripts/dify_admin.py <命令>`（Claude 会替你跑）

### A. 应用生命周期
| 命令 | 作用 |
|---|---|
| `whoami` | 验证登录 |
| `list [--name --mode --tag --page]` | 列出/过滤所有 app（多工作流定位） |
| `describe <id>` | 看 app 类型 + 输入字段 |
| `export <id> [--out f]` | 导出工作流 DSL(YAML) |
| `import <id> --file f` | 改：把 DSL 导回草稿 |
| `import --new --name N --file f` | 新建工作流 |
| `publish <id>` | 发布草稿到线上 |
| `run <id> [--inputs '{}'] [--query ..] [--file f --file-var v] [--stream]` | 运行拿结果（自动识别 工作流/对话/补全；支持文件入参、流式） |
| `stop <id> <task_id>` | 中断运行 |
| `rename <id> <name>` / `copy <id> [--name]` / `delete-app <id>` | 改名 / 复制 / 删除 |

### B. 组织 / 定位（工作流多时找对那个）
`tag-list` · `tag-create <name>` · `tag-bind <id> <tag>` · `tag-delete <tag>` —— 打标签后用 `list --tag` 精确定位。

### C. 观测 / 调试
| 命令 | 作用 |
|---|---|
| `runs <id>` | 画布调试运行历史 |
| `logs <id> [--keyword --status]` | API/线上运行历史（含 run_id） |
| `run-detail <id> <run_id>` | 单次运行的输入/输出 |
| `node-outputs <id> <run_id>` | **逐节点输入/输出（排错核心）** |

### D. 资源 / 地基
`resources`（列可用 LLM/Embedding/Rerank 模型 + 供应商 + 知识库 + 工具）· `install-plugin <org/name>`（从市场装，如 `deepseek`）· `set-model-key <provider> --key k`（给供应商配 key）· `config-model <id> --file f`（改基础应用配置）

### E. 人工介入（HITL）
`resume <form_token> [--inputs] [--action]` —— 续接带「人工输入」暂停节点的工作流。

### F. 知识库（RAG）
| 命令 | 作用 |
|---|---|
| `dataset-list` | 列知识库 |
| `dataset-create <name> --indexing economy/high_quality [--embedding-provider P --embedding-model M]` | 建库（高质量=语义需 embedding 模型） |
| `dataset-update <id>` / `dataset-delete <id>` | 改 / 删库 |
| `dataset-add-text <id> --name N --text T` | 加文本文档 |
| `dataset-add-file <id> --file F` | 上传文件建文档（pdf/docx/md/txt…） |
| `dataset-docs <id>` | 列文档及索引状态 |
| `dataset-doc-delete <id> <doc>` | 删文档 |
| `dataset-doc-status <id> <batch>` | 索引进度 |
| `dataset-retrieve <id> --query Q [--method keyword/semantic/hybrid/full_text] [--top-k N] [--rerank-provider/--rerank-model] [--filter JSON]` | 检索测试 |
| `dataset-seg-list/-seg-add/-seg-update/-seg-delete` | 分段增删改 |

## 5. 关键认知（少踩坑）
- **模型两层**：先 `install-plugin`+`set-model-key` 在供应商层配 key（一次，全局）；工作流里只**引用**模型名，**不写 key**。
- **建/改工作流前先 `resources`**：只引用这台 Dify **已装好**的模型/知识库/工具。
- **运行历史**：画布调试看 `runs`；API/线上看 `logs`（再用其 run_id 跑 `node-outputs` 排错）。
- **发布有风险**：`publish` 会让改动**线上生效**，Claude 会先跟你确认。

## 6. 这台 Dify 已配好的资源（开箱可用）
- 对话模型：DeepSeek、智谱 GLM（已配 key）
- Embedding：智谱 embedding-3（已配，可建语义知识库）
- 内置工具：code / webscraper / time / audio / google / github

## 7. 故障速查
- 登录报 `Invalid encrypted data`：脚本已用 base64 处理密码；若仍报错，确认环境变量没设错。
- 命令 404 / 字段报错：这台 Dify 版本与脚本不匹配（Console API 是内部接口、版本间会变）——告诉作者升级脚本。
- 拉插件慢/失败：服务器访问插件市场慢，重试或换模型。
