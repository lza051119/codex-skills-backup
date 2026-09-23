#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Workflow Editor — 通过 Dify Console API + Service API 全面操控自托管 Dify。
登录用 cookie jar（requests.Session 自动管理 cookie；HttpOnly 不影响服务端客户端）。

配置（环境变量，二选一）：
  自托管(推荐)：DIFY_BASE + DIFY_EMAIL + DIFY_PASSWORD
  云手动     ：DIFY_BASE + DIFY_COOKIE + DIFY_CSRF
多实例：切换上面这组环境变量即可指向不同 Dify。

命令总览（python dify_admin.py <命令> --help 看细节）：
  应用: whoami list describe export import publish run stop rename copy delete-app
  组织: tag-list tag-create tag-bind tag-delete
  观测: runs run-detail node-outputs logs
  资源: resources install-plugin set-model-key config-model
  HITL: resume
  知识库: dataset-list dataset-create dataset-update dataset-delete
          dataset-add-text dataset-add-file dataset-docs dataset-doc-delete dataset-doc-status
          dataset-retrieve dataset-seg-list dataset-seg-add dataset-seg-update dataset-seg-delete
"""
import os, sys, json, time, base64, argparse, requests
try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台默认 gbk，避免 emoji 报错
except Exception:
    pass


# ----------------------------- 会话 / 辅助 -----------------------------
def make_session():
    base = os.environ.get("DIFY_BASE", "").rstrip("/")
    if not base:
        sys.exit("ERROR: 未设置 DIFY_BASE（如 https://your-dify.com）")
    api = base + "/console/api"
    s = requests.Session()
    cookie = os.environ.get("DIFY_COOKIE")
    if cookie:  # 云手动模式
        s.headers.update({"Cookie": cookie})
        return s, api, base, os.environ.get("DIFY_CSRF", ""), "manual-cookie"
    email, pw = os.environ.get("DIFY_EMAIL"), os.environ.get("DIFY_PASSWORD")
    if not (email and pw):
        sys.exit("ERROR: 需 DIFY_EMAIL+DIFY_PASSWORD（自托管）或 DIFY_COOKIE+DIFY_CSRF（云手动）")
    enc_pw = base64.b64encode(pw.encode()).decode()  # Dify 的"加密"就是 base64
    r = s.post(api + "/login", json={"email": email, "password": enc_pw, "remember_me": True})
    if r.status_code != 200:
        sys.exit(f"登录失败 HTTP {r.status_code}: {r.text[:300]}")
    try:
        at = (r.json().get("data") or {}).get("access_token")
        if at:
            s.headers.update({"Authorization": "Bearer " + at})
    except Exception:
        pass
    csrf = s.cookies.get("csrf_token") or s.cookies.get("__Host-csrf_token") or ""
    return s, api, base, csrf, "login"


def H(csrf):
    h = {"Content-Type": "application/json"}
    if csrf:
        h["x-csrf-token"] = csrf
    return h


def get_mode(s, api, csrf, app_id):
    r = s.get(f"{api}/apps/{app_id}", headers=H(csrf)); r.raise_for_status()
    return r.json().get("mode")


def get_app_key(s, api, csrf, app_id):
    rk = s.get(f"{api}/apps/{app_id}/api-keys", headers=H(csrf)); rk.raise_for_status()
    keys = rk.json().get("data", [])
    if keys:
        return keys[0]["token"]
    return s.post(f"{api}/apps/{app_id}/api-keys", headers=H(csrf), json={}).json()["token"]


def get_ds_key(s, api, csrf):
    r = s.get(f"{api}/datasets/api-keys", headers=H(csrf)); r.raise_for_status()
    keys = r.json().get("data", [])
    if keys:
        return keys[0]["token"]
    return s.post(f"{api}/datasets/api-keys", headers=H(csrf)).json()["token"]


def resolve_tag_ids(s, api, csrf, name):
    r = s.get(f"{api}/tags", params={"type": "app"}, headers=H(csrf)); r.raise_for_status()
    j = r.json(); tags = j if isinstance(j, list) else j.get("data", [])
    return [t["id"] for t in tags if t.get("name") == name]


def sse_run(url, headers, payload):
    """流式运行：解析 SSE，实时打印回答/节点事件，返回 task_id。"""
    task_id = None
    with requests.post(url, headers=headers, json=payload, stream=True) as rr:
        print("HTTP", rr.status_code, "(streaming…)")
        for line in rr.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            try:
                ev = json.loads(line[5:].strip())
            except Exception:
                continue
            task_id = task_id or ev.get("task_id")
            et = ev.get("event")
            if et in ("message", "agent_message"):
                print(ev.get("answer", ""), end="", flush=True)
            elif et == "text_chunk":
                print(ev.get("data", {}).get("text", ""), end="", flush=True)
            elif et in ("node_started", "node_finished"):
                print(f"\n[{et}] {ev.get('data', {}).get('title', '')}")
            elif et == "workflow_finished":
                outs = ev.get("data", {}).get("outputs")
                print("\n[workflow_finished] 输出:", json.dumps(outs, ensure_ascii=False))
    print(f"\n(task_id={task_id})")
    return task_id


# ----------------------------- 主程序 -----------------------------
def main():
    p = argparse.ArgumentParser(description="Dify workflow editor")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami")
    ls = sub.add_parser("list")
    ls.add_argument("--name", default=""); ls.add_argument("--mode", default=""); ls.add_argument("--tag", default="")
    ls.add_argument("--page", type=int, default=1); ls.add_argument("--limit", type=int, default=100)
    de = sub.add_parser("describe"); de.add_argument("app_id")
    e = sub.add_parser("export"); e.add_argument("app_id"); e.add_argument("--out")
    i = sub.add_parser("import"); i.add_argument("app_id", nargs="?"); i.add_argument("--file", required=True)
    i.add_argument("--new", action="store_true"); i.add_argument("--name", default="")
    pub = sub.add_parser("publish"); pub.add_argument("app_id")
    rn = sub.add_parser("run"); rn.add_argument("app_id"); rn.add_argument("--inputs", default="{}")
    rn.add_argument("--query", default=""); rn.add_argument("--conversation-id", default="", dest="conversation_id")
    rn.add_argument("--file", default=""); rn.add_argument("--file-var", default="", dest="file_var")
    rn.add_argument("--stream", action="store_true")
    st = sub.add_parser("stop"); st.add_argument("app_id"); st.add_argument("task_id")
    rena = sub.add_parser("rename"); rena.add_argument("app_id"); rena.add_argument("name")
    cp = sub.add_parser("copy"); cp.add_argument("app_id"); cp.add_argument("--name", default="")
    da = sub.add_parser("delete-app"); da.add_argument("app_id")

    sub.add_parser("tag-list")
    tc = sub.add_parser("tag-create"); tc.add_argument("name")
    tb = sub.add_parser("tag-bind"); tb.add_argument("app_id"); tb.add_argument("tag")
    td = sub.add_parser("tag-delete"); td.add_argument("tag")

    ru = sub.add_parser("runs"); ru.add_argument("app_id"); ru.add_argument("--limit", type=int, default=10)
    rd = sub.add_parser("run-detail"); rd.add_argument("app_id"); rd.add_argument("run_id")
    no = sub.add_parser("node-outputs"); no.add_argument("app_id"); no.add_argument("run_id")
    lg = sub.add_parser("logs"); lg.add_argument("app_id"); lg.add_argument("--keyword", default=""); lg.add_argument("--status", default="")

    sub.add_parser("resources")
    ip = sub.add_parser("install-plugin"); ip.add_argument("plugin")
    sk = sub.add_parser("set-model-key"); sk.add_argument("provider"); sk.add_argument("--key"); sk.add_argument("--credentials")
    cm = sub.add_parser("config-model"); cm.add_argument("app_id"); cm.add_argument("--file", required=True)

    res = sub.add_parser("resume"); res.add_argument("form_token"); res.add_argument("--inputs", default="{}"); res.add_argument("--action", default="")

    sub.add_parser("dataset-list")
    dc = sub.add_parser("dataset-create"); dc.add_argument("name")
    dc.add_argument("--indexing", default="economy", choices=["economy", "high_quality"])
    dc.add_argument("--embedding-provider", default="", dest="embedding_provider")
    dc.add_argument("--embedding-model", default="", dest="embedding_model")
    du = sub.add_parser("dataset-update"); du.add_argument("dataset_id"); du.add_argument("--name", default="")
    du.add_argument("--indexing", default=""); du.add_argument("--permission", default="")
    dde = sub.add_parser("dataset-delete"); dde.add_argument("dataset_id")
    dt = sub.add_parser("dataset-add-text"); dt.add_argument("dataset_id")
    dt.add_argument("--name", required=True); dt.add_argument("--text", required=True); dt.add_argument("--indexing", default="economy")
    dfp = sub.add_parser("dataset-add-file"); dfp.add_argument("dataset_id"); dfp.add_argument("--file", required=True); dfp.add_argument("--indexing", default="economy")
    dd = sub.add_parser("dataset-docs"); dd.add_argument("dataset_id")
    ddd = sub.add_parser("dataset-doc-delete"); ddd.add_argument("dataset_id"); ddd.add_argument("document_id")
    dst = sub.add_parser("dataset-doc-status"); dst.add_argument("dataset_id"); dst.add_argument("batch")
    dr = sub.add_parser("dataset-retrieve"); dr.add_argument("dataset_id"); dr.add_argument("--query", required=True)
    dr.add_argument("--method", default="keyword_search",
                    choices=["keyword_search", "semantic_search", "full_text_search", "hybrid_search"])
    dr.add_argument("--semantic", action="store_true")  # 等价 --method semantic_search（兼容旧用法）
    dr.add_argument("--top-k", type=int, default=3, dest="top_k")
    dr.add_argument("--rerank-provider", default="", dest="rerank_provider")
    dr.add_argument("--rerank-model", default="", dest="rerank_model")
    dr.add_argument("--filter", default="", help="metadata 过滤 JSON")
    sl = sub.add_parser("dataset-seg-list"); sl.add_argument("dataset_id"); sl.add_argument("document_id"); sl.add_argument("--keyword", default="")
    sa = sub.add_parser("dataset-seg-add"); sa.add_argument("dataset_id"); sa.add_argument("document_id")
    sa.add_argument("--content", required=True); sa.add_argument("--answer", default=""); sa.add_argument("--keywords", default="")
    su = sub.add_parser("dataset-seg-update"); su.add_argument("dataset_id"); su.add_argument("document_id"); su.add_argument("segment_id")
    su.add_argument("--content", default=""); su.add_argument("--answer", default=""); su.add_argument("--keywords", default=""); su.add_argument("--enabled", default="")
    sd = sub.add_parser("dataset-seg-delete"); sd.add_argument("dataset_id"); sd.add_argument("document_id"); sd.add_argument("segment_id")

    args = p.parse_args()
    s, api, base, csrf, authmode = make_session()
    v1 = base + "/v1"

    # ---------- 应用：基础 ----------
    if args.cmd == "whoami":
        r = s.get(api + "/account/profile", headers=H(csrf))
        print(("✅ 鉴权 OK" if r.status_code == 200 else "❌ 鉴权失败") + f" | {authmode} | HTTP {r.status_code} | {r.text[:120]}")
        return

    if args.cmd == "list":
        params = {"page": args.page, "limit": args.limit}
        if args.name: params["name"] = args.name
        if args.mode: params["mode"] = args.mode
        if args.tag:
            tids = resolve_tag_ids(s, api, csrf, args.tag)
            if not tids:
                print(f"(没找到标签 '{args.tag}')"); return
            for idx, tid in enumerate(tids):
                params[f"tag_ids[{idx}]"] = tid
        r = s.get(api + "/apps", params=params, headers=H(csrf)); r.raise_for_status()
        items = r.json().get("data", [])
        print(f"共 {len(items)} 个 app（page {args.page}）：")
        for a in items:
            tags = ",".join(t.get("name", "") for t in a.get("tags", []))
            print(f"  {a['id']}  [{a.get('mode')}]  {a.get('name')}" + (f"  #{tags}" if tags else ""))
        return

    if args.cmd == "describe":
        mode = get_mode(s, api, csrf, args.app_id)
        token = get_app_key(s, api, csrf, args.app_id)
        r = requests.get(f"{v1}/parameters", headers={"Authorization": "Bearer " + token})
        print(f"app 类型: {mode}")
        if r.status_code == 200:
            form = r.json().get("user_input_form", [])
            print("输入字段:")
            for it in form:
                for ftype, spec in it.items():
                    print(f"  - {spec.get('variable')} ({ftype}) label={spec.get('label')} required={spec.get('required')}")
            if not form:
                print("  (无显式输入字段)")
        else:
            print("HTTP", r.status_code, r.text[:200])
        return

    if args.cmd == "rename":
        r = s.post(f"{api}/apps/{args.app_id}/name", headers=H(csrf), json={"name": args.name})
        print("改名 HTTP", r.status_code, "|", r.text[:150])
        return

    if args.cmd == "copy":
        body = {"name": args.name} if args.name else {}
        r = s.post(f"{api}/apps/{args.app_id}/copy", headers=H(csrf), json=body)
        print("复制 HTTP", r.status_code)
        try:
            d = r.json(); print(f"新 app_id = {d.get('id')} | name = {d.get('name')}")
        except Exception:
            print(r.text[:200])
        return

    if args.cmd == "delete-app":
        r = s.delete(f"{api}/apps/{args.app_id}", headers=H(csrf))
        print("删除 HTTP", r.status_code, "(204=成功)")
        return

    # ---------- 应用：DSL ----------
    if args.cmd == "export":
        r = s.get(f"{api}/apps/{args.app_id}/export", params={"include_secret": "true"}, headers=H(csrf))
        r.raise_for_status(); y = r.json()["data"]
        if args.out:
            open(args.out, "w", encoding="utf-8").write(y)
            print(f"✅ 已导出到 {args.out}（{len(y)} 字节，⚠️含密钥，用完请删）")
        else:
            print(y)
        return

    if args.cmd == "import":
        y = open(args.file, "r", encoding="utf-8").read()
        body = {"mode": "yaml-content", "yaml_content": y}
        if args.new:
            if args.name: body["name"] = args.name
        else:
            if not args.app_id: sys.exit("更新现有需传 app_id；新建请加 --new")
            body["app_id"] = args.app_id
        r = s.post(api + "/apps/imports", headers=H(csrf), json=body); r.raise_for_status()
        res = r.json()
        print(f"导入状态: {res.get('status')}  {res.get('error') or ''}")
        if res.get("status") == "pending":
            s.post(f"{api}/apps/imports/{res['id']}/confirm", headers=H(csrf)).raise_for_status()
            print("已确认导入（版本不一致）")
        print(f"✅ 写入草稿。app_id = {res.get('app_id')}（需 publish 才线上生效）")
        return

    if args.cmd == "publish":
        mode = get_mode(s, api, csrf, args.app_id)
        if mode in ("workflow", "advanced-chat"):
            r = s.post(f"{api}/apps/{args.app_id}/workflows/publish", headers=H(csrf), json={}); r.raise_for_status()
            print(f"🚀 发布成功 (mode={mode}) HTTP {r.status_code}")
        else:
            print(f"✅ 基础应用 (mode={mode})：import 即生效，无需发布")
        return

    if args.cmd == "config-model":
        cfg = json.loads(open(args.file, "r", encoding="utf-8").read())
        r = s.post(f"{api}/apps/{args.app_id}/model-config", headers=H(csrf), json=cfg)
        print("配置基础应用 HTTP", r.status_code, "|", r.text[:200])
        return

    # ---------- 运行 ----------
    if args.cmd == "run":
        mode = get_mode(s, api, csrf, args.app_id)
        token = get_app_key(s, api, csrf, args.app_id)
        bh = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
        try:
            inputs = json.loads(args.inputs)
        except Exception:
            sys.exit("--inputs 必须是合法 JSON")
        files = []
        if args.file:
            up = requests.post(f"{v1}/files/upload",
                               headers={"Authorization": "Bearer " + token},
                               data={"user": "dify-skill"}, files={"file": open(args.file, "rb")})
            if up.status_code not in (200, 201):
                sys.exit(f"文件上传失败 HTTP {up.status_code}: {up.text[:200]}")
            fid = up.json()["id"]
            fobj = {"type": "document", "transfer_method": "local_file", "upload_file_id": fid}
            if args.file_var:
                inputs[args.file_var] = fobj           # workflow：放进对应输入变量
            else:
                files = [fobj]                          # chat/completion：放 files
            print(f"已上传文件 → upload_file_id={fid}")
        rmode = "streaming" if args.stream else "blocking"
        print(f"运行 (mode={mode}, {rmode}) …")
        if mode == "workflow":
            url = f"{v1}/workflows/run"; payload = {"inputs": inputs, "response_mode": rmode, "user": "dify-skill"}
        elif mode == "completion":
            if args.query: inputs.setdefault("query", args.query)
            url = f"{v1}/completion-messages"; payload = {"inputs": inputs, "files": files, "response_mode": rmode, "user": "dify-skill"}
        else:  # advanced-chat / chat / agent-chat
            if not args.query: sys.exit("聊天类需要 --query")
            url = f"{v1}/chat-messages"
            payload = {"inputs": inputs, "query": args.query, "files": files, "response_mode": rmode,
                       "user": "dify-skill", "conversation_id": args.conversation_id}
        if args.stream:
            sse_run(url, bh, payload); return
        rr = requests.post(url, headers=bh, json=payload); d = rr.json()
        if mode == "workflow":
            data = d.get("data", d)
            print("HTTP", rr.status_code, "| 状态:", data.get("status"), "| 输出:", json.dumps(data.get("outputs"), ensure_ascii=False))
            if data.get("error"): print("错误:", data["error"])
        else:
            print("HTTP", rr.status_code, "| 回答:", d.get("answer") or json.dumps(d, ensure_ascii=False)[:400])
            if d.get("conversation_id"): print("conversation_id:", d["conversation_id"])
        return

    if args.cmd == "stop":
        mode = get_mode(s, api, csrf, args.app_id)
        token = get_app_key(s, api, csrf, args.app_id)
        ep = {"workflow": "workflows", "completion": "completion-messages"}.get(mode, "chat-messages")
        r = requests.post(f"{v1}/{ep}/tasks/{args.task_id}/stop" if ep == "workflows" else f"{v1}/{ep}/{args.task_id}/stop",
                          headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
                          json={"user": "dify-skill"})
        print("停止 HTTP", r.status_code, "|", r.text[:150])
        return

    if args.cmd == "resume":  # 续接 human-input 暂停的工作流（HITL 表单，无需鉴权）
        try:
            inputs = json.loads(args.inputs)
        except Exception:
            sys.exit("--inputs 必须是合法 JSON")
        body = {"inputs": inputs}
        if args.action: body["action"] = args.action
        r = requests.post(f"{base}/api/form/human_input/{args.form_token}", json=body)
        print("续接 HTTP", r.status_code, "|", r.text[:200])
        return

    # ---------- 观测 ----------
    if args.cmd == "runs":
        mode = get_mode(s, api, csrf, args.app_id)
        path = "advanced-chat/workflow-runs" if mode == "advanced-chat" else "workflow-runs"
        r = s.get(f"{api}/apps/{args.app_id}/{path}", params={"limit": args.limit}, headers=H(csrf)); r.raise_for_status()
        for w in r.json().get("data", []):
            print(f"  {w.get('id')}  [{w.get('status')}]  {w.get('created_at')}  耗时{w.get('elapsed_time')}s")
        return

    if args.cmd == "run-detail":
        r = s.get(f"{api}/apps/{args.app_id}/workflow-runs/{args.run_id}", headers=H(csrf)); r.raise_for_status()
        d = r.json()
        print("状态:", d.get("status"), "| 错误:", d.get("error"))
        print("输入:", json.dumps(d.get("inputs"), ensure_ascii=False)[:300])
        print("输出:", json.dumps(d.get("outputs"), ensure_ascii=False)[:500])
        return

    if args.cmd == "node-outputs":
        r = s.get(f"{api}/apps/{args.app_id}/workflow-runs/{args.run_id}/node-executions", headers=H(csrf)); r.raise_for_status()
        for n in r.json().get("data", []):
            print(f"\n● {n.get('title')} [{n.get('node_type')}] {n.get('status')}")
            if n.get("error"): print("  错误:", n["error"])
            print("  in :", json.dumps(n.get("inputs"), ensure_ascii=False)[:200])
            print("  out:", json.dumps(n.get("outputs"), ensure_ascii=False)[:300])
        return

    if args.cmd == "logs":
        params = {"page": 1, "limit": 20}
        if args.keyword: params["keyword"] = args.keyword
        if args.status: params["status"] = args.status
        r = s.get(f"{api}/apps/{args.app_id}/workflow-app-logs", params=params, headers=H(csrf)); r.raise_for_status()
        for lo in r.json().get("data", []):
            wr = lo.get("workflow_run") or {}
            print(f"  run={wr.get('id')}  [{wr.get('status')}]  耗时{wr.get('elapsed_time')}s  (log {str(lo.get('id'))[:8]})")
        print("→ 用上面的 run=<id> 跑 node-outputs/run-detail 看节点级输入输出")
        return

    # ---------- 组织：标签 ----------
    if args.cmd == "tag-list":
        r = s.get(f"{api}/tags", params={"type": "app"}, headers=H(csrf)); r.raise_for_status()
        j = r.json(); tags = j if isinstance(j, list) else j.get("data", [])
        print(f"共 {len(tags)} 个 app 标签：")
        for t in tags:
            print(f"  {t.get('id')}  {t.get('name')}  (绑定 {t.get('binding_count', '?')} 个)")
        return

    if args.cmd == "tag-create":
        r = s.post(f"{api}/tags", headers=H(csrf), json={"name": args.name, "type": "app"})
        print("建标签 HTTP", r.status_code, "|", r.text[:200])
        return

    if args.cmd == "tag-bind":
        tids = resolve_tag_ids(s, api, csrf, args.tag)
        if not tids:
            tids = [s.post(f"{api}/tags", headers=H(csrf), json={"name": args.tag, "type": "app"}).json()["id"]]
            print(f"(自动新建标签 '{args.tag}')")
        r = s.post(f"{api}/tag-bindings", headers=H(csrf),
                   json={"tag_ids": tids, "target_id": args.app_id, "type": "app"})
        print("绑定 HTTP", r.status_code, "|", (r.text[:150] or "ok"))
        return

    if args.cmd == "tag-delete":
        tids = resolve_tag_ids(s, api, csrf, args.tag)
        if not tids:
            print(f"(没找到标签 '{args.tag}')"); return
        r = s.delete(f"{api}/tags/{tids[0]}", headers=H(csrf))
        print("删标签 HTTP", r.status_code, "(204=成功)")
        return

    # ---------- 资源 / 地基 ----------
    if args.cmd == "resources":
        for label, mtype in [("LLM 对话", "llm"), ("Embedding 嵌入", "text-embedding"), ("Rerank 重排", "rerank")]:
            print(f"==== 可用模型 ({label}) ====")
            r = s.get(f"{api}/workspaces/current/models/model-types/{mtype}", headers=H(csrf))
            if r.status_code == 200:
                shown = False
                for pv in r.json().get("data", []):
                    models = [m.get("model") for m in pv.get("models", []) if m.get("status") in (None, "active")]
                    if models:
                        print(f"  provider={pv.get('provider')}  models={models}"); shown = True
                if not shown:
                    print("  (无 —— 装插件并填 key)")
            else:
                print("  HTTP", r.status_code, r.text[:120])
        print("==== 已装模型供应商(含未配 key) ====")
        r = s.get(f"{api}/workspaces/current/model-providers", headers=H(csrf))
        if r.status_code == 200:
            for pv in r.json().get("data", []):
                print(f"  {pv.get('provider')}  [{(pv.get('custom_configuration') or {}).get('status', '?')}]")
        print("==== 知识库 ====")
        r = s.get(f"{api}/datasets", params={"page": 1, "limit": 100}, headers=H(csrf))
        for d in (r.json().get("data", []) if r.status_code == 200 else []):
            print(f"  {d.get('id')}  {d.get('name')}")
        print("==== 工具 ====")
        r = s.get(f"{api}/workspaces/current/tool-providers", headers=H(csrf))
        if r.status_code == 200:
            j = r.json(); tools = j.get("data", []) if isinstance(j, dict) else j
            for t in tools[:60]:
                print(f"  {t.get('name') or t.get('id')}  [{t.get('type', '')}]")
        return

    if args.cmd == "install-plugin":
        name = args.plugin if "/" in args.plugin else "langgenius/" + args.plugin
        org, pname = name.split("/", 1)
        mr = requests.get(f"https://marketplace.dify.ai/api/v1/plugins/{org}/{pname}", timeout=30); mr.raise_for_status()
        ident = mr.json()["data"]["plugin"]["latest_package_identifier"]
        print("市场标识符:", ident)
        ir = s.post(f"{api}/workspaces/current/plugin/install/marketplace", headers=H(csrf),
                    json={"plugin_unique_identifiers": [ident]}); ir.raise_for_status()
        res = ir.json()
        if res.get("all_installed"):
            print("✅ 已安装（无需等待）"); return
        tid = res.get("task_id"); print(f"安装任务 {tid} 轮询中…"); st = "running"
        for _ in range(60):
            time.sleep(3)
            task = s.get(f"{api}/workspaces/current/plugin/tasks/{tid}", headers=H(csrf)).json().get("task", {})
            st = task.get("status"); print("  status:", st)
            if st in ("success", "failed"): break
        print("✅ 安装完成" if st == "success" else f"结束: {st}")
        return

    if args.cmd == "set-model-key":
        creds = json.loads(args.credentials) if args.credentials else ({"api_key": args.key} if args.key else None)
        if not creds: sys.exit("需 --key 或 --credentials")
        r = s.post(f"{api}/workspaces/current/model-providers/{args.provider}/credentials",
                   headers=H(csrf), json={"credentials": creds})
        print("配置 key HTTP", r.status_code, "|", r.text[:300])
        return

    # ---------- 知识库 ----------
    if args.cmd.startswith("dataset"):
        dk = get_ds_key(s, api, csrf)
        DH = {"Authorization": "Bearer " + dk, "Content-Type": "application/json"}
        AH = {"Authorization": "Bearer " + dk}

        if args.cmd == "dataset-list":
            r = requests.get(f"{v1}/datasets", params={"page": 1, "limit": 100}, headers=DH)
            for d in r.json().get("data", []):
                print(f"  {d.get('id')}  {d.get('name')}  (docs={d.get('document_count')}, index={d.get('indexing_technique')})")
            return
        if args.cmd == "dataset-create":
            body = {"name": args.name, "permission": "only_me", "indexing_technique": args.indexing}
            if args.indexing == "high_quality":
                if not (args.embedding_provider and args.embedding_model):
                    sys.exit("high_quality 需 --embedding-provider 和 --embedding-model")
                body["embedding_model_provider"] = args.embedding_provider; body["embedding_model"] = args.embedding_model
            r = requests.post(f"{v1}/datasets", headers=DH, json=body)
            d = r.json(); print("HTTP", r.status_code, "| dataset_id =", d.get("id"), "| name =", d.get("name"))
            return
        if args.cmd == "dataset-update":
            body = {}
            if args.name: body["name"] = args.name
            if args.indexing: body["indexing_technique"] = args.indexing
            if args.permission: body["permission"] = args.permission
            r = requests.patch(f"{v1}/datasets/{args.dataset_id}", headers=DH, json=body)
            print("更新库 HTTP", r.status_code, "|", r.text[:200])
            return
        if args.cmd == "dataset-delete":
            r = requests.delete(f"{v1}/datasets/{args.dataset_id}", headers=DH)
            print("删库 HTTP", r.status_code, "(204=成功)")
            return
        if args.cmd == "dataset-add-text":
            r = requests.post(f"{v1}/datasets/{args.dataset_id}/document/create-by-text", headers=DH,
                              json={"name": args.name, "text": args.text, "indexing_technique": args.indexing,
                                    "process_rule": {"mode": "automatic"}})
            print("HTTP", r.status_code, r.text[:300])
            return
        if args.cmd == "dataset-add-file":
            meta = {"indexing_technique": args.indexing, "process_rule": {"mode": "automatic"}}
            r = requests.post(f"{v1}/datasets/{args.dataset_id}/document/create-by-file", headers=AH,
                              data={"data": json.dumps(meta)}, files={"file": open(args.file, "rb")})
            print("HTTP", r.status_code, r.text[:300])
            return
        if args.cmd == "dataset-docs":
            r = requests.get(f"{v1}/datasets/{args.dataset_id}/documents", headers=DH)
            for d in r.json().get("data", []):
                print(f"  {d.get('id')}  {d.get('name')}  [{d.get('indexing_status')}]")
            return
        if args.cmd == "dataset-doc-delete":
            r = requests.delete(f"{v1}/datasets/{args.dataset_id}/documents/{args.document_id}", headers=DH)
            print("删文档 HTTP", r.status_code, "|", r.text[:120])
            return
        if args.cmd == "dataset-doc-status":
            r = requests.get(f"{v1}/datasets/{args.dataset_id}/documents/{args.batch}/indexing-status", headers=DH)
            for d in r.json().get("data", []):
                print(f"  {d.get('id')}  {d.get('indexing_status')}  {d.get('completed_segments')}/{d.get('total_segments')} 段")
            return
        if args.cmd == "dataset-retrieve":
            method = "semantic_search" if args.semantic else args.method
            rm = {"search_method": method, "reranking_enable": False, "top_k": args.top_k, "score_threshold_enabled": False}
            if args.rerank_provider and args.rerank_model:
                rm["reranking_enable"] = True
                rm["reranking_model"] = {"reranking_provider_name": args.rerank_provider, "reranking_model_name": args.rerank_model}
            payload = {"query": args.query, "retrieval_model": rm}
            if args.filter:
                payload["retrieval_model"]["metadata_filtering_conditions"] = json.loads(args.filter)
            r = requests.post(f"{v1}/datasets/{args.dataset_id}/retrieve", headers=DH, json=payload)
            print("HTTP", r.status_code)
            if r.status_code != 200:
                print(r.text[:300]); return
            recs = r.json().get("records", [])
            if not recs: print("  (无命中)")
            for rec in recs[:5]:
                print("  score=", rec.get("score"), "|", rec.get("segment", {}).get("content", "")[:80])
            return
        if args.cmd == "dataset-seg-list":
            params = {"keyword": args.keyword} if args.keyword else {}
            r = requests.get(f"{v1}/datasets/{args.dataset_id}/documents/{args.document_id}/segments", params=params, headers=DH)
            for seg in r.json().get("data", []):
                print(f"  {seg.get('id')}  [{'on' if seg.get('enabled') else 'off'}]  {seg.get('content', '')[:70]}")
            return
        if args.cmd == "dataset-seg-add":
            seg = {"content": args.content}
            if args.answer: seg["answer"] = args.answer
            if args.keywords: seg["keywords"] = [k.strip() for k in args.keywords.split(",")]
            r = requests.post(f"{v1}/datasets/{args.dataset_id}/documents/{args.document_id}/segments",
                              headers=DH, json={"segments": [seg]})
            print("加分段 HTTP", r.status_code, "|", r.text[:200])
            return
        if args.cmd == "dataset-seg-update":
            seg = {}
            if args.content: seg["content"] = args.content
            if args.answer: seg["answer"] = args.answer
            if args.keywords: seg["keywords"] = [k.strip() for k in args.keywords.split(",")]
            if args.enabled: seg["enabled"] = args.enabled.lower() in ("1", "true", "yes", "on")
            r = requests.post(f"{v1}/datasets/{args.dataset_id}/documents/{args.document_id}/segments/{args.segment_id}",
                              headers=DH, json={"segment": seg})
            print("改分段 HTTP", r.status_code, "|", r.text[:200])
            return
        if args.cmd == "dataset-seg-delete":
            r = requests.delete(f"{v1}/datasets/{args.dataset_id}/documents/{args.document_id}/segments/{args.segment_id}", headers=DH)
            print("删分段 HTTP", r.status_code, "|", r.text[:120])
            return


if __name__ == "__main__":
    main()
