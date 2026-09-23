# Dify DSL 结构速查（编辑前必读）

Dify DSL = 一个应用的完整定义，YAML 格式，本质是前端画布数据的序列化。**没有官方 schema**，字段以目标 Dify 导出的实际内容为准。

## 顶层结构
```yaml
app:
  name: 我的工作流
  description: ''
  mode: workflow          # ★ 类型：workflow / advanced-chat(=Chatflow) / chat / agent-chat / completion
  icon: 🤖
  icon_background: '#FFEAD5'
kind: app
version: 0.3.0            # ★ DSL 规范版本（不是业务版本）；保守做法=沿用目标实例导出的值
workflow:                 # 仅 workflow / advanced-chat 有
  features: {...}         # 文件上传/TTS/STT/敏感词等开关
  environment_variables: []
  conversation_variables: []   # 仅 Chatflow(advanced-chat)
  graph:
    nodes: [...]
    edges: [...]
```

## 节点 nodes（最易错：业务类型在 `data.type`）
```yaml
nodes:
- id: '1720794829558'    # ★ 全图唯一，通常是毫秒时间戳字符串
  type: custom           # ReactFlow 渲染类型，几乎恒为 custom
  position: {x: 80, y: 282}
  data:
    type: start          # ★★ 真正的业务类型在这里：start/end/answer/llm/
                         #    knowledge-retrieval/question-classifier/if-else/code/
                         #    template-transform/variable-aggregator/assigner/
                         #    iteration/loop/http-request/tool/agent/
                         #    parameter-extractor/document-extractor/list-operator
    title: 开始
    # ...各类型自己的字段
```
**陷阱**：顶层 `type` 是渲染类型(custom)；要判断/修改节点种类看 `data.type`。

## 连线 edges（sourceHandle 语义随节点变）
```yaml
edges:
- id: A-source-B-target
  source: 'A_id'
  target: 'B_id'
  sourceHandle: source   # 普通节点=source；IF/ELSE 真=true 假=false；
                         # 问题分类器=该 class 的 id；带错误处理=success-branch/fail-branch
  targetHandle: target   # 几乎恒为 target
  type: custom
```

## 变量引用（两套，必须互相对得上）
1. **结构化** `value_selector: [节点id, 输出字段]` —— 用在节点配置字段里（LLM 的 context、End 的 outputs、Code 的 variables 等）。
   - 全局：系统变量 `['sys','query']`/`['sys','files']`；会话变量 `['conversation','x']`；环境变量 `['env','x']`。
2. **模板字符串** `{{#节点id.字段#}}` —— 用在 prompt 文本、template-transform 模板等自由文本里。

两者引用的"节点id.字段"必须真实存在、且该节点在上游（edges 可达），否则运行时找不到变量。

## 常见节点 data 关键字段（改这些最常用）
**LLM 节点**（改 prompt / 换模型 / 调参常用）：
```yaml
data:
  type: llm
  model: {provider: openai, name: gpt-4o-mini, mode: chat,
          completion_params: {temperature: 0.7}}   # ← 改模型/温度
  prompt_template:
  - {role: system, text: '你是助手'}                # ← 改系统提示词
  - {role: user, text: '{{#start1.query#}}'}        # ← 改用户提示词（注意变量引用）
  context: {enabled: false, variable_selector: []}
  vision: {enabled: false}
```
**知识检索**：`query_variable_selector: [id, 字段]`、`dataset_ids: [...]`（知识库 id 必须在目标 Dify 已存在）。
**IF/ELSE**：`logical_operator: and/or`、`conditions: [{comparison_operator, value, variable_selector}]`。
**Code**：`code_language: python3`、`code: |...`、`variables: [{variable, value_selector}]`、`outputs: [{variable, type}]`。
**Start**：`variables: [{variable, label, type, required, max_length}]`（定义工作流入参）。
**End**：`outputs: [{variable, value_selector:[id,字段]}]`。

## 最小可用示例（Start→LLM→End）
```yaml
app: {name: demo, description: '', mode: workflow, icon: 🤖, icon_background: '#FFEAD5'}
kind: app
version: 0.3.0
workflow:
  features: {file_upload: {image: {enabled: false}}, retriever_resource: {enabled: false},
             sensitive_word_avoidance: {enabled: false}, speech_to_text: {enabled: false},
             text_to_speech: {enabled: false}}
  environment_variables: []
  conversation_variables: []
  graph:
    nodes:
    - {id: start1, type: custom, position: {x: 80, y: 282},
       data: {type: start, title: 开始, variables: [{variable: query, label: 输入, type: text-input, required: true, max_length: 256}]}}
    - {id: llm1, type: custom, position: {x: 380, y: 282},
       data: {type: llm, title: LLM, model: {provider: openai, name: gpt-4o-mini, mode: chat, completion_params: {temperature: 0.7}},
              prompt_template: [{role: user, text: '{{#start1.query#}}'}], context: {enabled: false, variable_selector: []}, vision: {enabled: false}}}
    - {id: end1, type: custom, position: {x: 680, y: 282},
       data: {type: end, title: 结束, outputs: [{variable: result, value_selector: [llm1, text]}]}}
    edges:
    - {id: e1, source: start1, target: llm1, sourceHandle: source, targetHandle: target, type: custom}
    - {id: e2, source: llm1, target: end1, sourceHandle: source, targetHandle: target, type: custom}
```

## 编辑后自检清单（导回前必过）
- [ ] 所有节点 `id` 唯一
- [ ] 每条 edge 的 source/target 都指向真实存在的节点 id
- [ ] `sourceHandle` 取值符合该源节点类型（分支节点尤其注意）
- [ ] 所有 `value_selector:[id,字段]` 和 `{{#id.字段#}}` 引用的节点真实、且在上游可达
- [ ] 各节点必填字段没缺（缺字段会导入失败甚至搞坏 app）
- [ ] `model.provider`/`model.name`、`dataset_ids`、自定义工具 在目标 Dify 实例已存在
- [ ] `version` 用目标实例能接受的值（不确定就沿用导出时的值）

## 版本兼容
- 1.0 前后断层最大（插件化后 tool/model 标识方式变）。导入时平台会做版本检查并告警；版本太低可能报错。
- 知识库（dataset）不随 DSL 导出，`dataset_ids` 只是引用，目标实例必须已有同 id 知识库。

---

# ⚠️ 两大致命坑（agent 生成 DSL 导入失败的头号原因）

## 坑1：缺顶层 `dependencies` 块 → "Leaked Dependencies"
1.0+ 插件化后，凡用到 **tool / agent 节点 / 非默认 model provider**，DSL 顶层必须声明依赖插件，否则导入报缺插件：
```yaml
dependencies:
- current_identifier: null
  type: marketplace          # marketplace | github | package
  value:
    marketplace_plugin_unique_identifier: langgenius/deepseek:0.0.17@<sha256>
```
- 标识符带 `@checksum`，**编不出来** → 生成时**沿用目标实例导出的真实 dependencies 块**（先 `export` 一个同类已有工作流抄它的 dependencies）。
- 纯 Start+LLM(默认provider)+Code+知识检索 可 `dependencies: []`。

## 坑2：节点 id / value_selector 的 id 必须**带引号当字符串**
时间戳形 id（`'1718246807593'`）不加引号会被 YAML 解析成整数 → selector 匹配失败、分支静默断链。生成器用时间戳 id 一律加引号；或像本文档示例用 `start1` 这种短字符串 id。

---

# 进阶节点速查（最小字段 + 片段）

> 通用：壳恒 `type: custom`；业务类型在 `data.type`（**连字符**拼写）；`data.title` 必填。

**参数提取器 parameter-extractor**：`query`(选择器)+`model`+`parameters[]`(每项 name/type/description非空/required；type 用 `boolean` 非 bool，select 配 options)。输出=各 param + `__is_success`/`__reason`。

**问题分类器 question-classifier**：`query_variable_selector`+`model`+`classes[]`(每项 `{id,name}`)+单数 `instruction`。**出边 sourceHandle 必须逐字=某 class.id**。

**迭代 iteration**：子节点不嵌套、同层放 `nodes[]`，靠 `parentId`+`data.iteration_id`+`isInIteration:true` 归属；容器带 `start_node_id`(内部 start 壳 `type: custom-iteration-start`)；取当前项用容器id `['容器id', item]`；进入边 target=容器id。

**循环 loop**：`loop_count`+`break_conditions`+`logical_operator`+`loop_variables`；**比较符用 Unicode `≥ ≤ ≠`**；内部 start 壳 `custom-loop-start`。

**变量聚合器 variable-aggregator**：`output_type`(写 `array[string]` 字面量)+`variables`(**数组的数组**，每项一个 selector)。（注意 `assigner` 是另一个节点）

**变量赋值 assigner**(写会话变量唯一节点)：**必用 v2** → `version:'2'`+`items[]`(每项 variable_selector/input_type/operation/value)；算术算子 `+= -= *= /=`(带等号)。

**模板转换 template-transform**：`template`(Jinja2)+`variables[]`(每项 variable/value_selector)；**输出恒 `output`，不写 outputs**。

**HTTP http-request**：`method` 小写；`headers`/`params` 是**字符串**(每行 Key:Value)；`body.data` 是**列表**；no-auth 时 `authorization.config: null`。

**工具 tool**：`provider_id`(builtin 三段式 `langgenius/tavily/tavily`；api/workflow 工具是**实例 UUID 取自目标**)+`tool_name`+`tool_configurations`(标量)+`tool_parameters`(每值 `{type:mixed/variable/constant, value}`)。

**Agent 节点**：`agent_strategy_name`/`agent_strategy_provider_name`+`agent_parameters`(每值 `{type,value}`)；model value 带 `type: model-selector`；tools 条目 `enabled:true`。策略插件须在 dependencies 声明。

**文档提取 document-extractor**：只需 `variable_selector`(指向 file/array[file])；输出恒 `text`。

**列表操作 list-operator**：必带 `filter_by`/`order_by`/`limit` 三块(不用也给空壳 enabled:false)；输出 `result`/`first_record`/`last_record`。

**直接回复 answer**(chatflow 专属)：`answer`(模板，用 `{{#id.字段#}}`/`{{#sys.query#}}`)；多 answer 可分布在分支按序流式拼出回复。

---

# Chatflow（mode: advanced-chat）要点
- 判定 `app.mode: advanced-chat`；**用 `answer` 节点收尾，不用 `end`**。
- `conversation_variables[]`：每项必填 `name`/`value_type`/`value`(缺任一报错)；写它只能用 assigner v2。
- 专属系统变量：`{{#sys.query#}}`(本轮输入)、`{{#sys.files#}}`、`{{#sys.conversation_id#}}`、`{{#sys.dialogue_count#}}`。
- 开场白在 `workflow.features`：`opening_statement`、`suggested_questions:[...]`。

---

# 导入失败 Top 原因
1. **插件/依赖缺失**(头号)→ 顶层 dependencies 声明全 + 目标实例先装好 provider/工具。
2. **版本不匹配** → 用相近 Dify 版本；不手填高 version；不确定沿用导出值。
3. **`dataset_ids` 指向不存在的知识库** → 跨实例后重绑。
4. **node 缺 id/type/data** → 每节点齐全、id 全局唯一(缺 id 会搞崩 /apps 页)。
5. **edge/变量引用不存在或非上游** → source/target 真实、引用上游可达。

---

# Agent 生成 DSL 强校验清单（必过）
```
[结构] app/kind:app/version/workflow 四块；用 tool/agent/非默认provider 时 dependencies 已声明(带真实@checksum)
[节点] 每 node 有 id+type:custom+data；data 有 type+title；id 全局唯一且时间戳id加引号；data.type 连字符拼写
[引用] value_selector=[节点id,字段]字符串数组；{{#id.字段#}} 与 selector 引用的节点真实且上游可达；sys/conversation/env 前缀正确
[边]   edge.source/target 真实；targetHandle:target；普通=source；IF/ELSE=true/false；分类器=class.id；fail-branch 仅 error_strategy:fail-branch
[特例] 分类器单数instruction；iteration 子节点 parentId+iteration_id；loop 用Unicode≥≤≠；assigner version:'2'；聚合器 variables 是数组的数组；template 不写outputs；http headers/params 是字符串、no-auth config:null；tool 区分 configurations/parameters；agent tools enabled:true
[chatflow] advanced-chat 用 answer 收尾；conversation_variables 项全字段；sys.query 仅 chatflow
[目标实例] model.provider+name 已配；dataset_ids/自定义工具UUID 真实存在；version 取目标可接受值
```
