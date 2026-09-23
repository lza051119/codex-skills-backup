# VM188 固定连接与所有权

实际操作入口：`C:\Users\27616\Desktop\vm188\single-server-deploy\README.md`。脚本实现全部在桌面目录，本参考仅存稳定连接事实。

- VM：`root@10.10.20.188:22`，预期 hostname：`vm188`。
- SSH 私钥：`C:\Users\27616\.ssh\agentos-vm188-access-ed25519`，不复制私钥。
- VM ED25519 指纹：`SHA256:26d5ym1Qmdd30lYMTotN/NbZAvSPtuq6ia+7J4xQsnI`。
- 产品代码：`https://git.infra.qingtianji.com/agentos/AgentOSNext.git`，固定 ref `refs/heads/dev`；Git 网络传输走 HTTPS。
- 原源码目录：`/opt/agentos/AgentOSNext`。独立固定版本源码：`/opt/agentos/deploy-worktrees/`。目录版本不等于全套运行镜像版本。
- 应用 kubeconfig：`/etc/agentos/agentos-dev-local.kubeconfig`，context：`kind-agentos-dev-local`，namespace：`agentos-acceptance`。
- 独占写锁：`/run/lock/agentos-vm188-deploy.lock`。
- 远端私有记录：`/opt/agentos/vm188-deploy-records/`。本地实现与公开证据以桌面目录为准。
- SSH 转发：OIDC `https://localhost:18443`，Web `https://localhost:18486`；服务 `agentos-dev-forward.service`。
- 域名：`https://temp8.agentos.infra.qingtianji.com/`，内网或 VPN 使用。
- k3s kubeconfig：`/etc/rancher/k3s/k3s.yaml`，仅入口与其基础设施；Caddy 是 `agentos-edge/caddy`，保留 `caddy-config`、`caddy-data` PVC。
- 路由：k3s Caddy → kind `vm188-temp8-entry` → 同一套应用。网络服务 `vm188-temp8-network.service`。独立域名 BFF 也要纳入版本清单。
- Caddy acceptance 信任：`agentos-edge/agentos-edge-external-routes` 中的 `vm188-acceptance-ca.pem`。
- 原桌面 CMD：`C:\Users\27616\Desktop\vm188\打开-AgentOSNext-vm188.cmd`，调用桌面 `single-server-deploy\scripts\open-vm188.ps1`。
- 账号与访问手册：桌面 `vm188` 目录现有中文手册；保留用户指定的凭据行，不复制到新脚本或日志。

旧 k3s 业务环境已退役。kind 集群名、realm、服务名保留 dev 是正常现状，不能据此清理。版本、磁盘、镜像、证书和数据状态均需重新实测。
