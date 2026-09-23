# 9月14至16日单机部署经验

本页于 2026-09-16 从桌面部署回执整理，未执行实机检查。只记录已出现的问题及后续执行会用到的判断；数值和版本属于各次记录，不作为所有环境默认值。

## 读取入口与环境边界

- VM188：`C:\Users\27616\Desktop\vm188\single-server-deploy\README.md`、`DEPLOYMENT-NOTES.md`，以及 `records\20260914-dev-full-rebuild\STATUS.md`。应用是 kind；独立 k3s/Caddy 是入口。
- VM187：`C:\Users\27616\Desktop\vm187\single-server-deploy\README.md`、`records\20260915-full-refresh\DEPLOYMENT-RESULT.md`、`ISSUE-CLASSIFICATION.md`。使用本机独立 K3s，不能套用 VM188 的 kubeconfig、节点名、存储身份和授权。
- 两者都由桌面脚本调用原生命令。产品源码仅作为固定版本构建/兼容输入；不操作产品正式 Deploy/CD。

## 版本、阶段与原生初始化

局部更新逐组件记源码 SHA/tree、镜像 digest、init 镜像和配套 sidecar；代码目录 HEAD、PR 合并或候选镜像存在均不能替代已部署事实。VM188 在 9 月 14 日完成整套重建后又有 Server/Web/扫描器局部更新，不能仍用第一次重建的 SHA 代表全部组件。

新一轮使用新的 record/operation，并先生成本轮自己的 cluster-before、database-before。`run-script.py` 的 detached 启动只证明请求已发出；完成必须读取远端 result.json、阶段 summary 和实际对象。SSH/导入响应丢失后区分“已完成并验证”“已执行待补证”“未执行”，只续接剩余阶段。写操作不因返回超时自动重放。

VM188 `import-r914-images.py` 已处理 kind load 成功后收据未写完的续接；API 瞬时不可用只允许有界只读等待，恢复后重新核验节点与基础设施。VM187 `prepare-refresh-stages-local.py` 生成具名阶段单，`operation-status-local.py` 读取状态，`verify-refresh-records-local.py` 比对阶段证据。历史默认日期/SHA不用于新任务。

空库仍要跑目标版本原生表结构初始化；旧版本号和手写表结构不能通用复用。BFF 真空库首次初始化与 OIDC scope 是两类问题：前者按目标产品实现验证，后者按运行配置修复。不能通过伪造 schema 版本、跳过 init 或把所有连接换成 DBA 宣布成功。

## 构建容量与精确清理

VM188 9月14日构建把磁盘余量降至约5GB，触发承载 Caddy 的 k3s DiskPressure，入口中断约1小时。构建前同时估算镜像层、导出归档、节点导入副本和运行余量；共享宿主磁盘意味着业务 Pod Ready 不保证入口不受影响。保持容量门槛，按精确引用清理具名闲置对象后续接，不放宽驱逐阈值。

镜像清理要分开检查宿主 Docker、节点 CRI、OCI index/config/别名、控制器与 init 模板、SandboxTemplate、运行及停止容器。镜像归档和 OCI 传输副本另列清单，不用全局 prune。VM188 的 Docker Mounts 顺序要稳定排序后比较；导出验证用 stdout 流至 DEVNULL，不把字符设备作为 docker save 的普通目标文件。

VM187 `cleanup-superseded-images.py` 曾因 CRI 默认2秒超时中断，后改60秒并从实时清单续接。超时先核对实际删除结果，不能从超时直接判定未执行。清理后分别检查 owned-images、oci-copies、image-archives，不以磁盘变大代替目标消失验证。

## 接线与日志

- OIDC `invalid_scope` / AUTH107：核对保留或新建 realm 中 `profile` / `email` 的定义、ID及BFF绑定，按对应环境实际要求补齐。VM188 使用 `repair-r914-oidc-scopes.py`；VM187 的修复已进入 `prepare-fresh-material.py` 和 `refresh-keycloak-browser-scopes.py`。不扩大角色或随意改标准 scope 请求。
- VM187 Knowledge SSRF 拒绝内部对象存储：精确允许 `seaweedfs`，修复进入 `prepare-refresh-runtime.py`；不放开任意 host。生成器要保留用户当前模型、Embedding域名及词表输入，不能用旧恢复快照覆盖后续配置。
- OTel file exporter 必须原生 validate 并实际观察轮转。VM188 历史配置每路4MiB/3备份/1天；VM187为16MB/2备份/1天，emptyDir 128Mi。二者不是统一默认值，按目标容量计算。
- 旧 Failed/Evicted Pod 与新 Pod 共用 IP、并与数据库路径失败相关时，沿 `pod-ip-reuse.md` 核对退役 ReplicaSet、Pod UID/resourceVersion及无活动CRI容器后处理具名终态残留。9月15日 VM188 同类事件涉及272条，不能据此删除现役 Pod 或全量网络策略。

## 扫描 sidecar 与使用验证

VM188 9月15至16日候选先因构建上下文0600权限使UID65532无法读 `/app/server.py`，后暴露 `/var/run` 到 `/run` 的系统别名路径校验问题。切换前按实际非root UID、只读rootfs、挂载路径与必要文件权限验证；固定可信根的系统别名与不可信请求目录中的 symlink 分别处理。

仅替换扫描器镜像也要核对 Server Pod 全容器就绪、原数据 Pod/container身份、活动执行、扫描真实业务入口与失败恢复。扫描健康、业务上传成功、模型调用成功分别取证。故障或超时按既有拒绝策略处理；客户端等待结束后先看原幂等键状态，不换键盲目重交。

9月16日历史终态为 scanner源码 `d67de82a89cbfc3cbb50e0f30cd61e6dba69f98c`、digest `ab1878f55165c3e25e23b67d087f460e4d9e7ef83e2d9027d47ff38f9069574d`，只改变该镜像字段，188个页面样本及104个临时技能清理有记录。这不是整套升级，也不是本页更新时重新完成的验收。

## 原始依据

- `C:\Users\27616\Desktop\vm188\report-20260914-deployment-issues\README.md`：D01–D20 与实机证据入口；PR状态采用文件顶部后续更正。
- `C:\Users\27616\Desktop\vm187\single-server-deploy\records\20260915-full-refresh\ISSUE-CLASSIFICATION.md` 与 `DEPLOYMENT-RESULT.md`。
- `D:\projects\report-20260914-skill-upload-admission\report.md`：容量、Pod IP残留、扫描截止与同键恢复。
- `D:\projects\report-20260915-skill-contextual-admission\report.md`：非root权限、系统别名、正式构建、部署及清理。

以上报告的观察时间和覆盖范围应随引用保留。本页没有重跑测试、刷新服务器状态或调整部署脚本实现。
