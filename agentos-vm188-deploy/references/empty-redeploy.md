# VM188 路线三：复用基础设施、重建业务库

只在本轮授权明确覆盖目标数据丢弃时使用。以可用的新部署为目标，不继续把旧 owner 搬运、历史行一致性、47-only 清理或完整恢复演练当作前置条件。已完成证据留作历史即可。

适用：旧业务数据可以丢弃，现有集群和入口可继续使用；尤其是旧数据/私有表结构转换复杂、重新初始化更可控的情况。保留 kind、k3s/Caddy 入口、可复用的网络、有效证书与准确目标镜像；数据库进程本身可继续使用，按实际需要重建具名业务库、角色和运行输入。若需要删除并重建整个 kind 应用集群，转入 [路线四](cluster-rebuild.md)。

执行单分别列明业务数据库、对象存储文件、Keycloak/身份状态、Provider/模型配置和凭据材料的保留或重建方式。删业务库不等于对象文件也已删除；保留文件或 API Key Secret 也不等于新库已恢复其引用、账号和模型配置。不要把宿主机、其他环境或系统数据库纳入清空范围。

2026-09-09 e082 历史任务中，用户确认该任务所有需替换的旧业务数据库允许直接删除重建，无需迁移旧数据。该任务后续接管继续沿用此授权，不重复确认，不为已放弃的旧数据增加保留门槛。该任务已完成的新库可复用；必要的再次业务库重建也在该任务范围内，先固定目标并停止写入。该记录不自动授权未来升级丢弃后来产生的数据。

原生程序的 `migrate` 命令属于表结构初始化/检查步骤，名称不表示正在搬运旧业务数据。汇报时使用“初始化/检查表结构”。连接、DNS、服务路由或 Pod 启动故障需要按对应原因修复，不能靠跳过初始化、写假版本号或重复删库掩盖。

## 最短执行路线

1. 固定源码 SHA/tree 和现成镜像清单，复用有效制品。已导入的目标镜像不用因为换部署路线而重建或导入；不要追逐移动 dev 或引入旁路 PR。
2. 在桌面形成具名执行单，停入口、应用、后台 Job 和自动扩容。KEDA `paused-replicas=0` 要核对 HPA 已退出；Deployment spec0 不代表旧 Pod/Job 已结束。已授权丢弃的旧任务不再要求历史保留证明。
3. 用原生 PostgreSQL/Kubernetes/Keycloak 接口创建空存储和配置。可复用 PG 进程创建空同名库，也可替换已确认使用 emptyDir 的具名 Pod。数据库、角色、Secret 和新对象的真实身份要对应，不用保留旧 schema owner 或历史版本。
4. 运行固定镜像的原生初始化入口。空库仍需创建表和权限；不能手写版本号或把管理员 URL 用作长期 runtime。只读参考产品 SQL、接口和二进制，不调用或复制产品部署 shell。
5. 统一 runtime、init、域名专用 BFF 和 Sandbox 模板的镜像与启动模式，完成真实登录、授权、模型对话、文件和 Sandbox 验证，再清理旧镜像、退役库和失效资源。
6. 更新桌面手册与 skill。记录真实终态，不把计划通过、镜像导入或 Pod Ready 写成整套部署成功。

## e082 容易漏掉的初始化合同

以下提示仅绑定 `e08285df4cb91c1089905934dae10b17887f2528`；其他版本重新读取原生代码，不盲套。

- e082 全空库存在跨域顺序：Server 到 181（内部 Credential 到 15），Identity `adopt → migrate` 到 14，再 Server 到 187、`complete-model-online`。本次 Server 184 遇到旧列触发器依赖，使用已评审的窄范围空库兼容事务后由原生 184 完成最终 DDL；不得手写版本或用 CASCADE 绕过。以 `resume-e082-empty-schemas-v2.py` 及完整回执为准，不重跑已完成阶段。Identity `fresh-activate → assert-active` 在空 Ledger、seed之前执行；最后 `maintenance-seed → verify → status`。
- Authority 使用本次 UUID、epoch、SHA/tree，同步 runtime expect Secret。保留 Keycloak 时核对真实 ownership nonce；新 Realm 可避免旧 nonce 冲突。seed 使用受限可写文件，失败续接使用同一份，不能把只读 Secret 当可写 seed。
- PAP 使用独立 owner/migrator/service-runtime，删除 `AOS_E5B_*`，设置 `AOS_PAP_KEYCLOAK_*`，投射 raw32 `cursor.key`。空库 baseline 需要真实 Server catalog 和 Gateway/OPA 加载结果。
- Knowledge 空库初始化也创建 TEMP 表。仅在初始化窗口对其准确角色授 TEMP，连接关闭后撤销；不给 PUBLIC TEMP。ParadeDB 扩展默认的 public schema CREATE 需按产品 SQL 收紧。
- BFF 原生 migrate 要求初始两表存在。一次性 Node 适配只调用镜像内 `schema.mjs` 的 `ensureSessionTable`/`ensureLoginTransactionTable`，同事务执行完整角色/ownership/ACL合同，再原生 migrate；两套长期 BFF 使用专用 runtime URL 并关闭自动迁移。
- Sandbox、Workflow 也要原生初始化；主 BFF、temp8 BFF、Sandbox 服务/检查 init/node-attestor/模板都纳入镜像核对。
- Server E14 客户端六项、独立身份交付 listener 五项、9107 Service/容器端口、主 BFF 与 temp8 BFF 各五项必须整条核对；仅修 E5d 启动错误不会自动启用一次性交付。URI 按实际 namespace 与已签发的 workload SAN 对齐。已存在 NetworkPolicy 不代表应用 env 和 Service 已接通。
- Kubernetes API egress 同时核对 Service 443 和 DNAT 后真实 control-plane `/32:6443`。`192.0.2.7`、Broker 的 `192.0.2.8` 是模板占位；从当前 Endpoint/EndpointSlice/Node 交叉验证后精准替换。Sandbox informer 首次同步失败发生于 E11 listener 前，先查其 CRD served version、实际 namespace 的 list/watch 权限及 Pod 网络，不归因于 Server E14。
- Provider、连接、模型、Endpoint 配置权威在 Server。清库后保留 API Key Secret 不会自动恢复模型；按正常 Admin API/secure-upload 重建运行配置并实际调用，不把夹具回包当真实 AI 成功。
- e082 非空 `AOS_MODEL_PROVIDER_ALLOWED_PRIVATE_CIDRS` 选择排他私网模式，`10/8` 会阻断 DeepSeek/百炼公网。公网模式删除该 env 项，精确限定两个供应商 Host 与443并保留TLS；设空字符串会启动失败，`0.0.0.0/0` 不合法。当前固定客户端不能同时承载私网夹具与公网模式。变更后从新Pod及新的真实Run核验，目录可选不是调用证据。
- 真实 Provider Key 只从已确认 UID 的 Broker Kubernetes Secret 对应 `model_provider_api_key` 字段在内存读取，使用同一 Human 会话 `PUT /onboarding/materializations/{operationId}/material`；不是 POST，也不是旧 runtime_ref。创建返回 `provider.models[]`，端点使用 `endpoint_id` 与该模型版本；Provider PATCH 前重新 GET Provider version。未知上传结果先原生读回/reconcile，不重发 Key。
- 浏览器连续 eval 共享 JavaScript realm，每段用 IIFE，避免顶层 const 重名。首 Provider 已创建而后续失败时，依据同一 Human/Provider/operation 读回续接；新 guard 接管必须确认旧进程身份、原锁及实际已执行步骤，不能把未知结果当未写入。
- 对话要分别核对真实模型Run、原生entries与session-tails页面投影。e082存在同一Message同时为latest/latest_message时误判重复的产品缺陷；清库不能解决。本轮用户已批准此前说明的额外Server最小修复；精确候选与实施进度见桌面 `server-tail-e082-candidate-01.json` 和最新状态。候选只含PR #2890的修复，不引入整个最新dev；定向测试、真实PG回归、镜像构建和实机页面复验分别留证据。
- 文件上传、原件字节校验、页面预览、AI读取、Shell生成和结果下载各自留证据。会话列表出错时，可从正常“会话空间 → 文件”入口独立验证原件和预览；不得伪造页面响应或将原件可下载写成Shell已完成。
- 暖池已自动换到目标 Python digest 时直接复用；分别核对模板、Sandbox、实际 Pod/init，不盲删所有池。NodeJS第三方基础镜像不是旧第一方制品。KEDA恢复后验证PausedFalse、原生HPA有效指标及零Fallback。
- 原生 workload 证书有效期上限 30 天，本次叶证书 29 天；根证书可另设期限。Keycloak 26.7 的 TLS 自动重载从 HTTPS listener 启动计时，不能按 Pod/container 启动时间推算，也不能把 Secret 更新当作实际握手换证。桌面 service CA 与 temp8 域名 CA 是不同信任链。
- Keycloak Admin API 批次跨越短 token 有效期时，事先按到期时间刷新；最终只读验证因 401 失败，应复用已完成的原生命令/Pod 回执继续验证，不重新 seed。

e082 历史任务的阶段记录在桌面 `records/20260908-e08285df-deploy/SOLE-WRITER-PROGRESS.json`、`CURRENT-DEPLOYMENT-GAPS.md`。`quiesce-e082-empty-redeploy.py`、`reset-e082-empty-database.py` 和后续具名脚本是该次执行单；新部署复用前核对目标版本、对象身份和完成记录，不无条件重跑。

## 失败处理

原生步骤失败时，保存退出码、已提交阶段和实际版本/角色状态，针对失败点继续，不反复整套重建。密码/DSN 只经 Secret、受限文件或 stdin，私密材料先持久化再创建角色。结果不确定时先读实际状态，不盲重置口令或重复更新 Secret。

网络从真实消费者检查。PG 自身可连不证明 Service 正常；未发送协议数据的 nc 退出码也未必代表 TCP 成败。区分工具错误、超时、拒绝后检查准确节点的路由/转发/防火墙，不以关闭 TLS 或全局清空规则代替定位。

API预检失败时先保留错误及新旧容器启动尝试，不继续旧清理或滚动执行单。可从原生CRI做具名只读诊断、从/proc及/sys读取块设备延迟和cgroup限额；本轮5秒样本曾在约0.25MB/s低吞吐下出现约469ms写等待。不能仅凭剩余空间、Pod Ready或DNS/TCP成功排除控制面问题，不能把延迟相关性当成已确认宿主机根因。诊断脚本和最新证据只维护桌面一份。
