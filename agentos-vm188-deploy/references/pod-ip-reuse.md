# VM188 Pod IP reuse and retained terminal records

First distinguish operator SSH/local forwarding from application Pod traffic.
The following private incident was verified on 2026-09-09; refresh current
identities and observations before applying it to a later deployment.

New Server Pod IP 10.244.1.201 also appeared on a historical Failed/Evicted otel
Pod with different labels. NetworkPolicy allowed Server to PostgreSQL, but
repeated SYN probes through both the Service and direct PostgreSQL Pod IP were
intermittently lost inside the kind node. Routing, backlog, conntrack capacity,
and drop counters did not explain it; kindnet's NetworkPolicy NFQUEUE was active.

The operator removed only the exact old terminal Pod API record using a native
DELETE with UID and resourceVersion preconditions. The new Server was retained.
Its next native schema check finished in two seconds; both main containers
became Ready; six alternating Service/direct-Pod TCP connections passed.
Five additional exact terminal-record conflicts affecting current sandbox,
fixture-provider and otel IPs were then removed with the same bounded method.
No CNI restart, policy/route/firewall change, database deletion or current Pod
replacement was part of these cleanups.

For a new incident:

1. Capture source/target Pod UID, IP, node, Service and EndpointSlice and test
   both TCP paths. Inspect retained terminal Pod IPs across namespaces.
2. Require exactly the known old and new UID on the affected IP. Require the
   old record is terminal with no running container, finalizer or pending
   deletion, and the new Pod is the intended current workload.
3. Under the VM188 operator lock, use a fresh exact plan and one native
   UID/resourceVersion-preconditioned DELETE of the old record. Record intent
   before submission. On uncertain or partial outcome, inspect rather than
   replay. Do not blanket-delete historical Pods.
4. Verify the old UID is absent, the current UID and storage identities remain,
   and controllers and policies are unchanged. Repeat actual connectivity and
   readiness checks before claiming recovery.

Desktop evidence directory: `single-server-deploy/records/20260908-e08285df-deploy`.
Key evidence: `finish-ip-conflict-result-01.json`,
`finish-pg-direct-route-after-03.json`, `finish-rollout-readiness-07.json`, and
`finish-ip-conflicts-result-02.json`. The named scripts encode this incident's
UIDs and are not reusable blindly on new Pods.

Even after this recovery, a pending Run can be waiting on an application
condition. Check attachment bind/outbox terminal state and actual Worker
acquisition separately. Do not describe an exhausted bind as a continuing
network repair or silently reset application database rows to make it pass.

## Recurrence and retirement of the remaining old records

At 11:37 on the same day, newly allocated IPs 203 through 207 collided with
other records of the same retired otel ReplicaSet. Deleting only currently
colliding records had left the next IP allocations exposed. The user explicitly
confirmed that these obsolete Pods should be removed directly.

The operator inventoried the exact ReplicaSet UID
`e1a194f5-3e61-48b6-9112-ee27eb409879`, verified desired and actual replicas were
zero, and pinned its remaining 41 Failed/Evicted Pod names, UIDs and resource
versions. Both nodes' CRI inventories showed no live sandbox or container for
those UIDs. Metadata/status evidence was archived durably before any DELETE,
including fsync of the new record directory's parent. All 41 exact records were
removed at 11:50:14, with storage identities, workload specs and policies
unchanged. The same new Server Pod at IP 207 then became Ready, with schema
check exit 0 and all six direct/Service PostgreSQL probes passing. This did not
require rebuilding images, replacing that new Pod, or deleting the database.

For this verified pattern, clean the reviewed fixed residual set of the fully
retired owner in one operation; do not retain its other obsolete terminal
records until each becomes an active conflict. This is still a named UID/RV
allowlist, not a blanket deletion of live or unrelated Pods. Preserve the
original failed rollout observer receipt and separately record later
convergence; never replay a successful image patch because its observer timed
out.

Evidence: `finish-retired-otel-inventory-01.json`,
`finish-retired-otel-review-01.json`, `finish-retired-otel-result-03.json`,
`finish-fixes-pg-before-retirement-01.json`,
`finish-fixes-server-convergence-03.json`, and
`finish-fixes-active-ip-conflicts-03.json`.
