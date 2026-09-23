---
name: agentos-vm188-deploy
description: Inspect and deploy private AgentOSNext VM188 with independent Desktop tools, choosing the appropriate update or authorized rebuild scope and documenting results. Do not modify or invoke product Deploy/CD scripts.
---

# AgentOS VM188 Deploy

## 用户边界与唯一执行入口

2026-09-07 用户明确要求：正式 Deploy/CD 由另一位负责人维护，正在推进集群化部署。VM188 使用自己的单服务器部署方式；脚本和经验全部放桌面 VM188 文件夹，不提交产品仓库。此要求覆盖本 Skill 的旧版仓库控制器流程。

**先读桌面的实际操作指南：**

- `C:\Users\27616\Desktop\vm188\single-server-deploy\README.md`
- 排障、后续部署步骤与证据：`C:\Users\27616\Desktop\vm188\single-server-deploy\DEPLOYMENT-NOTES.md`
- 实际脚本：`C:\Users\27616\Desktop\vm188\single-server-deploy\scripts\`
- 每次计划与证据：该目录的 `records\<本次时间与 SHA>\`。

后续 VM188 专用脚本直接在桌面目录开发维护。Skill 中的脚本只是兼容入口，转发到桌面；不维护第二份实现。桌面文件缺失时先查明位置，不回退到仓库部署脚本。

### 2026-09-16 经验与资料同步

涉及较新版本的初始化、镜像导入续接、构建容量、OIDC/对象存储接线、日志轮转或扫描 sidecar 时，阅读 [9月14至16日单机部署经验](references/single-server-lessons-20260916.md)。该参考整理了已有桌面回执，不是本次重新访问 VM 的健康结论；运行版本始终以具名组件的实机摘要为准。

用户指定 VM187 时先读 `C:\Users\27616\Desktop\vm187\single-server-deploy\README.md` 与该目录脚本。VM187 使用自己的 K3s 集群、连接客户端和 `/run/lock/agentos-vm187-deploy.lock`，不能套用 VM188 的 kind context、SSH pin 或历史清库授权。此 Skill 的 VM188 兼容入口不会自动转为 VM187。

用户只要求整理或同步部署资料时，只更新说明、脚本副本与 Skill；不启动部署执行器。发布资料保留源路径、采集时间与 SHA-256，日常入口和绑定版本的历史执行器分别说明；不收录账号文件、`private*`、原始 Secret、浏览器会话状态或缓存。上传完成后回读核对，历史证据与可执行入口分开存放。

不得为 VM188 部署修改正式 `deploy/`、`ops/forgejo/`、CD workflow 或部署脚本。不得调用、source、eval、提取或复制仓库部署脚本作为当前部署器，包括旧 `make dev-*`、phased rollout、acceptance controller 和 Sandbox reconcile 包装器。不得把旧 CD 修复 PR 的合并设为桌面部署前置条件。历史 PR #2744 已撤回、未合并，不自行恢复。

固定版本的产品代码、接口、迁移 SQL、Dockerfile 和锁文件可以作为只读兼容性与构建输入。独立脚本通过原生 Git、Docker、kind、kubectl、OpenSSL、Caddy 等命令工作，操作先做成桌面可核对的执行单。工具未覆盖的阶段就在桌面补齐。按下列四条部署路线确定操作范围，完成对应的原生表结构初始化或检查及实际使用验证。

## 四条部署路线

统一按以下四条路线向用户解释和选择。原有“保留升级／清空重部署”表示数据处理属性；局部更新与全组件升级、重建业务库与重建整个应用集群分别列明，避免把不同操作范围混在一起。

| 路线 | 数据处理 | 更新范围与适用条件 | 速度判断与详细步骤 |
| --- | --- | --- | --- |
| 1. 局部保留更新 | 保留现有业务数据 | 更新兼容性已核对的少数组件及其必要配套；适合范围明确的小修复 | 小修复通常最快；只能声明该范围完成。见 [保留更新·路线一](references/preserving-update.md) |
| 2. 全组件保留升级 | 保留业务数据，完成必要的表结构升级 | 将完整应用、初始化容器、两个 BFF、Sandbox 配套与运行配置对齐目标；适合需要保留数据的整套升级 | 兼容路径清晰时通常省事；私有 schema 分叉需要额外验证。见 [保留更新·路线二](references/preserving-update.md) |
| 3. 复用基础设施、重建业务库 | 丢弃具名旧业务数据，初始化新库 | 复用现有集群、入口、网络和有效制品，重建需要替换的业务存储及配置，再更新整套应用 | 数据可丢弃且旧结构适配复杂时优先考虑。见 [业务库重建](references/empty-redeploy.md) |
| 4. 整个应用集群从零重建 | 重建范围内的数据不自动保留；需保留的数据先落实恢复方案 | 重建具名 kind 应用集群、集群内网络、存储、身份与应用；适合集群本身确需重建或用户明确要求重新搭建 | 通常工作最多；范围不自动扩展到宿主机或 k3s 入口。见 [应用集群重建](references/cluster-rebuild.md) |

### 选择与提速

- 小范围修复先评估路线 1；用户要整套更新到最新且需要保留数据，采用路线 2。未经本任务授权丢弃的数据按保留处理。
- 用户允许丢弃目标业务数据时，比较路线 2 的兼容转换成本与路线 3 的重新初始化成本；不能一概认定删库更快。选择路线 3 后，不再为已放弃的旧数据增加搬运、逐行比对或恢复演练门槛。
- 只有操作范围确实包括重建应用集群时采用路线 4。仅“数据库不用保留”不足以把路线 3 扩大为路线 4；沿用同一任务已经明确覆盖的授权，不重复索要。
- “全组件更新”描述覆盖范围，“全量冷构建”描述制品准备，“清空数据”描述数据处理，三者独立。各路线都优先复用准确目标镜像与有效缓存，只构建、导入缺失制品；在容量和运行稳定性允许时，先准备制品再进入停机阶段。
- 四条路线是操作规范，不代表存在四个跨版本一键命令。状态查询、访问恢复、同镜像证书重载、构建和失败续接是辅助能力。执行前按桌面记录核对实际工具覆盖；历史具名脚本不直接重跑，缺少的阶段在桌面实现并验证。
- 清库或重建集群只能处理其范围内的环境与兼容问题，不能消除目标代码缺陷。切换前核对现有私有补丁是否已进入目标版本，完成与更新范围相称的真实功能验证后再汇报结果。

### 2026-09-09 e082 任务的历史授权

该次任务已获全清空授权，原文在桌面 `records/20260908-e08285df-deploy/EMPTY-STORE-AUTHORIZATION.json`；是否执行完成只看状态与实机证据，不从授权文件推断。这项记录适用于该任务续接，不是对未来升级中新产生数据的永久清空许可。

2026-09-09 用户再次明确：e082 任务中 VM188 的旧业务数据库都可以删除并创建新库，不需要旧数据迁移。该任务后续接管不再重复询问同一授权，不把数据搬迁、历史数据兼容、逐行比对或恢复演练列入剩余工作。需要替换的业务库按具名执行单重建；无关环境和系统数据库不在此范围。该任务已验证的新库可直接复用；确有必要再次重建该任务的业务库时，记录范围并停妥写入后执行。

区分旧数据迁移和新库表结构初始化：产品原生入口可能叫 `migrate`，其在空库上的作用是建立当前版本需要的表、索引、权限和版本表，在已初始化库上是检查当前结构。对用户应说“初始化/检查表结构”，不要只说“正在迁移数据库”。空库路线仍要运行实际初始化，不能通过跳过 init 容器或伪造 schema 版本宣布启动成功。数据库连接失败先处理连接问题，不能把反复删库当作网络修复。

## 保留的环境

VM188 是一台 VM 上的私有 kind 测试环境：应用是 `kind-agentos-dev-local / agentos-acceptance`；k3s 仅保留 `agentos-edge/Caddy` 域名入口。旧 k3s 业务环境已退役，不重建、不回退。kind 内名称含 dev/test 的配套 Sandbox、Keycloak realm 与转发服务仍属于保留环境。

固定连接和存储位置见 [references/environment.md](references/environment.md)。版本、证书、镜像、磁盘和队列必须实机刷新，不能沿用历史记录当实时状态。

## 操作路径

在 PowerShell 中设置自己的变量，不改 `$HOME` 或 `$CODEX_HOME`：

```powershell
$vm188Root = 'C:\Users\27616\Desktop\vm188\single-server-deploy'
$vm188Python = 'C:\Users\27616\AppData\Local\Programs\Python\Python312\python.exe'

# 只读诊断：镜像/Pod、队列、证书有效期、数据身份和转发服务。
& $vm188Python -X utf8 "$vm188Root\scripts\vm188.py" status

# 原桌面 CMD 的访问能力；此处只恢复转发。
& "$vm188Root\scripts\open-vm188.ps1" -NoBrowser -SkipVpnAutoConnect

# 严格 TLS 验证；localhost 项需要 SSH 转发。
& $vm188Python -X utf8 "$vm188Root\scripts\check-endpoints.py"

# 只读生成两个 AI 进程的同镜像证书重载计划。
& $vm188Python -X utf8 "$vm188Root\scripts\vm188.py" plan-trust-reload
```

实际保留更新按桌面指南固定一次 `refs/heads/dev` SHA/tree。先用现成精确源码/镜像和缓存；需要构建时使用桌面 `build-images` 默认只读计划，确认兼容性、磁盘和 API 稳定后在已有用户授权内执行 `--apply`。不要追逐移动 dev，也不要把目录 HEAD 当运行镜像版本。

e082 历史任务的阶段索引只维护在桌面 README：原生表结构终态为 `resume-e082-empty-schemas-v2.py`，身份种入收尾为 `verify-e082-identity-seed-final.py`，运行接线/网络/启动为 runtime-wiring、kubernetes-egress 和 activate-v2，另有真实 Provider、公网模型出口与 KEDA 续接执行器。逐项核对实际断点和回执，不直接重跑已完成的文件。`cf1c0e25869b` 的 `complete-*.py` 仅供历史参考；这些不是跨版本一键升级器，不从文件存在推断当前部署完成。

### 用户提问不回答时

先读队列是否 pending、Worker 是否领取任务失败、服务间 TLS 是否报 unknown authority；不凭 HTTP 200 或 Pod Ready 宣布可用。2026-09-07 曾因旧 Worker/Model Gateway 未加载新信任而积压提问，保留镜像只重载信任后恢复。这是诊断线索，不是所有故障的固定结论。

确需重载时先核对计划中的镜像、证书有效期、数据身份、活动租约和 Worker preStop。使用刚生成的计划执行 `apply-trust-reload --plan <绝对路径>`。脚本检查 30 分钟时限、对象版本、独占锁和每步状态；材料摘要一致时 no-op。它不续签证书、不更新镜像、不创建 NetworkPolicy。已有授权的恢复无需重复询问；状态查询不能自动扩张成重启或升级。

Drain 表示停领新任务、等待旧任务结束后安全替换。kubelet 探测成功不能证明 API Server 到 Worker 8082 管理端口可达。对用户清楚区分管理网络阻塞、TLS 加载问题、版本兼容问题和产品代码缺陷。

固定 e082 已遇到另一类“模型已回复、页面仍失败”：原生 entries 有完整 Agent Message，而 session-tails 因合法双角色同序号冲突返回500。重建旧库不能修复产品查询代码。用户在听取额外只修 Server 的说明后明确要求继续，已批准本次最小修复，见桌面 `server-tail-fix-authorization-01.json`。复用 PR #2890 的修复，精确回移到 e082；基础镜像与额外 Server 候选分别记 SHA/tree/digest，不把候选准备完成写成已部署。其他版本调整仍按本轮具体指示判断，不由清空授权推导采用任意新版本。

SSH 中断只阻塞 VM 上的安装与实机验证；本机源码核对、定向测试、固定 Git bundle、执行器评审和文档同步仍可继续。TCP 拒绝连接、超时、公钥不符、认证失败是不同阶段，保存原始失败与时间。已有 Web 443 可达不能代替远程管理连接，也不证明 Kubernetes 或 Worker 健康。

SSH 曾恢复又中断时，对齐 `ssh.service` 属性、22 端口实际监听、SSH/systemd journal 和 apt/unattended-upgrades 日志，再判断触发者。2026-09-09 的原始证据见桌面 `records/20260908-e08285df-deploy/SSH-INCIDENT-20260909.md`：系统自动更新批量重启 SSH 和转发后报 dependency job failed。区分“谁触发停止”“哪项依赖启动失败”和“部署负载是否参与资源不足”，不得由端口拒绝直接断定配置损坏或排除自身影响。`Too many open files` 与目录监听分配失败需分别检查进程 FD、全局文件表及 inotify 限额；跨进程 inotify 描述符可能共享，计数不等于独立实例数。短时恢复后先刷新转发、数据身份、原 Run 和当前操作者，不自动重启整机、关闭更新或扩大系统限额。

Kubernetes API 不可用时，可用桌面 `inspect-e082-native-runtime.py` / `inspect-e082-worker-network-native.py` 做固定主机、具名节点与已核对Pod UID的只读CRI诊断，区分Worker进程Ready、DNS/TCP连通、TokenReview可用与Run实际被领取。读到Unavailable及高I/O延迟只能支持相关性；没有认证响应或存储证据时不宣称唯一根因。该诊断路径不授权直接修改CRI容器、关闭fsync或绕过控制器。

SSH/网页转发和 VM 内 Pod 网络是两段链路，分别验证。若 Pod 到数据库的 Service 与直连 IP 都间歇超时、SYN 已进入节点但未送达目标，检查 kindnet NetworkPolicy 和全 namespace 的 Pod IP 归属，包含历史 Failed/Evicted 记录。2026-09-09 新 Server 与旧 Failed otel 记录共享 IP；只删除旧 UID 的终态 API 记录后，同一新 Server 完成表结构检查、2/2 Ready，PG 两条路径连续六次通过。处理方法和证据见 [pod-ip-reuse.md](references/pod-ip-reuse.md)。不要把该现象直接推广成所有超时的原因。

同日后续新 Pod 分配到其他 IP 时再次撞上同一退役 ReplicaSet 的剩余记录。用户明确要求直接删除这些无用旧 Pod；随后核对该 RS 已为零副本、41 条余下记录均 Failed/Evicted 且 CRI 无活动容器，按固定 UID/resourceVersion 清单归档并全部删除，新 Server 原 Pod 就绪、PG 六次复测通过。遇到这一已验证模式，应清完具名退役组件的终态残留集，避免只删当前冲突几条而使下次分配重现；不将此扩大为删除现役或无关 Pod。

本次桌面执行单已验证另一条管理路径：SSH 到 VM 后，对准确的 Worker Pod 建立仅监听 `127.0.0.1` 的原生 `kubectl port-forward`，调用真实 `/drain` 并验证活动租约归零。它没有跳过 drain，也不要求修改 NetworkPolicy 或正式 CD。端口转发只管理本次创建的进程，操作结束后关闭。

## VM188 联网构建授权

用户已授权这台私人 VM 联网取源码、依赖和直接构建。例外仅适用于 VM188 私人测试部署，不修改仓库 `AGENTS.md`，不扩展到共享 dev/test、生产或客户离线交付。

优先复用有效缓存与已验证镜像，缺少时直接构建，不等待 Harbor 发布。先验证实际 Git/依赖源的连接和认证；产品源码在 VM 上无法获取时，用操作员侧固定 SHA Git bundle。Git bundle 不包含项目的第三方依赖，缺失依赖按下节补齐。保持依赖锁定与镜像来源验证。未合并产品修复默认不混入；用户明确批准的具名私人部署候选须单独标明基线、补丁来源和实际验证，不能冒充已合并版本，也不代替产品 PR 的正式评审。

### 缺失依赖：服务器直取，本机通过 SSH 传输兜底

2026-09-11 用户明确：操作员在 Windows 本机通过 SSH 管理 VM188。已授权部署或验证所需的依赖，由助手按以下顺序准备；本机能够完成下载和传输时直接执行，不默认要求用户手工搬运。

1. **先核对实际执行位置的缓存。** 有效缓存直接复用；区分 VM 宿主机、Docker 构建环境和 Windows 本机，不能因为某处构建成功就认为其他位置也有同一份依赖。缺失时进入下载流程，不把“缓存优先”解释成“只能离线”。
2. **优先由 VM188 从上游源码仓库获取缺失依赖。** GitHub 托管的依赖优先从其实际 GitHub 仓库拉取；其他依赖使用其声明的上游地址。沿用项目锁定的版本和校验机制，使用对应包管理器下载，不擅自升级到 latest。Go 可在本次命令中使用 `GOPROXY=direct`；源码仓库、模块代理和校验服务分别检查，GitHub 可达不代表整条下载链已可用。
3. **服务器获取失败，就转到 Windows 本机准备。** 先复用与目标锁文件一致的本机依赖；本机也缺少时由助手下载补齐，再通过既有固定主机身份的 SSH/SCP/SFTP 通道传到 VM188。本机准备要覆盖目标 Linux 构建/测试需要的依赖；不能只传 Windows 当前用到的子集。Go 可传输模块源码/下载缓存，不能把 Windows 编译缓存或可执行文件当作 Linux 构建结果。使用具名临时目录、文件清单和摘要核对传输结果，再让实际构建/测试进程使用这份依赖；遵守 VM 写锁与现有缓存的所有权边界。
4. **补齐后继续原失败阶段。** 检查接收侧依赖完整性，继续编译或测试，不因依赖获取失败重建业务库，也不在已确认不可用的下载路径上反复空转。只有服务器直取与本机准备/传输都实际受阻，或缺少无法自行取得的必要访问条件时，才向用户说明具体缺项及需要提供的帮助。

不得在缓存未齐时默认设置 `GOPROXY=off`。仅在实际执行环境的所需依赖已准备完整、明确进行离线构建或验证时使用；发现缺项则回到上述补齐流程。保留锁文件和校验，不通过关闭 TLS 或跳过完整性校验来掩盖获取失败。

助手编写的临时部署/测试脚本同样必须落实此流程。向用户解释“执行器”时直接说是哪个临时脚本；依赖未准备好、编译失败与测试本身失败分别报告，测试程序尚未运行不能记作真实数据库测试已执行。

## 执行与汇报边界

- 所有 VM 写操作持有 `/run/lock/agentos-vm188-deploy.lock`，先验证固定 SSH 公钥与 hostname。锁被占用时不打断其他执行者。
- 显式应用 kubeconfig/context/namespace，避免误操作仅做入口的 k3s，保护其他工作负载。
- 保留升级时，PostgreSQL/SeaweedFS 的 `emptyDir` 依赖原 Pod/container；清空重部署时可按具名执行单替换并记录新身份。Keycloak 要检查当前 Pod 实际挂载，不能用“某个 PVC 仍 Bound”证明它正被使用。
- 用户使用服务时，不因整理工具、查状态或改文档启动版本切换。升级的已有授权与用户最新指示一并判断。
- 不复制私钥、Token、管理员凭据或 Secret 全量内容到文档/日志。已获授权的 Human 测试密码仅留在用户指定的原本地文件，更新手册保留对应行。
- 公开 CA 副本也会过期；从实机 authority 核对证书指纹与期限后更新。不得关闭 TLS 验证掩盖错误。
- 局部更新报告已更新组件与保留版本，可按证据声明具名修复完成；只有完整目标范围都核对后才宣布整套升级完成。入口、普通对话、Shell/Resource/Sandbox、业务任务和全版本统一分别列证据；VM188 结果不是共享 Candidate 验收证据。
- 持续写紧凑阶段结果；结束时统一更新桌面 README、DEPLOYMENT-NOTES、中文快速访问手册、部署复盘、账号连接说明及本轮记录。账号文件保留必要凭据，不复制到其他文档。注明真实完成项、未完成项、时间、版本和证据，删除或标为历史的过期“当前状态”。用户要求更新 skill 时同步本文件及适用参考；不提交个人部署文件到产品仓库，不修改 Codex memories，除非另获明确要求。

## 跨服务器共享与问题闭环（2026-09-20）

本 Skill 和桌面脚本会被整理到可分享的云盘资料包，目标是帮助其他维护者在**自己的单机服务器**上建立同类部署流程。VM188 的地址、主机名、kind context、namespace、写锁、证书、镜像摘要、路径和 operation 只属于 VM188 示例；换服务器时必须按 [references/portable-sharing-and-triage.md](references/portable-sharing-and-triage.md) 重新生成目标环境输入，不能直接复制历史执行单或私密材料。

部署过程中发现问题时，按第一真实错误位置分流并保留闭环：

1. **产品代码问题**：先在本轮固定 SHA/tree、镜像和数据状态下记录症状、请求/Run、首个真实错误和最小复现；确认不是版本混用或环境阻塞后，在独立产品工作树做最小修复，重新构建或导入具名候选，部署到已授权的私人环境并按受影响范围回归。部署成功只证明候选在该环境可用；随后仍要提交产品 PR，附源码、镜像、测试和实机证据，不能把桌面补丁当作产品仓库已修复。
2. **部署脚本问题**：直接在桌面 `single-server-deploy/scripts/` 修复脚本或生成器，保留旧执行单和失败回执；先做静态检查/只读 dry-run，再用新 record、唯一 operation-id 和对应写锁做最小回归。同步更新桌面 README、DEPLOYMENT-NOTES、脚本清单和 SHA-256；脚本修复属于桌面维护，不进入产品 Deploy/CD。
3. **Skill 缺口**：补充本 Skill 或 `references/` 的路由、输入契约、迁移前检查和证据要求，并在资料包中同步新文件；不复制第二套部署实现，也不把历史执行器包装成通用一键部署。

共享资料只包含说明、可审阅脚本和去除私密输入后的证据索引。账号文件、私钥、原始 Secret/DSN、浏览器会话、数据库内容、镜像归档和依赖缓存不进入云盘。每次发布保留源路径、采集时间和 SHA-256；上传后的回读只能证明副本完整，不等于在其他服务器重新通过功能验收。
