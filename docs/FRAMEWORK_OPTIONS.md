# Agent framework options

Written for: the owner, who chooses the framework. No choice has been made. `AGENTS.md` says a human decides before agent code is written.

## What the agent app needs

| Need | Why |
|---|---|
| Tool calling with a schema per tool | The PokeAPI tool already has `TOOL_SPEC` and `run_tool()` in `src/pokedex_agent/tools/`. |
| A hard limit on tool calls per request | `POKEDEX_MAX_TOOL_CALLS` (1 to 20). Required by `AGENTS.md`, and it must be tested. |
| Source attribution in every answer that uses tool output | `AGENTS.md` rule. The framework must let us attach `sources` to the answer. |
| Runs in a container with a managed identity | `DefaultAzureCredential`, no keys in code. |
| Small surface that is easy to test without Azure | `AGENTS.md`: unit tests must not call Azure. |

The current scope is one answering agent and one tool. The app will grow, so the choice should also cover multi-agent work.

## Options

### 1. Plain Python with the model API (Anthropic SDK, tool-use loop)

We write the loop ourselves: send messages, read `tool_use` blocks, run the tool, return `tool_result`, stop at the call limit.

| Area | Assessment |
|---|---|
| Fit to the limits | Best. The call limit is a counter in our loop, so it is simple to test. |
| Dependencies | One SDK, which is already small. Few moving parts. |
| Learning curve | Low for this scope. |
| Multi-agent | We build it. Fine for two or three agents. Harder later. |
| Lock-in | Low. Our tools and prompts stay portable. |
| Azure fit | We still use `DefaultAzureCredential` for Azure resources. The model endpoint is a separate decision (see below). |
| Risk | We own the bugs in orchestration. More code to review. |

### 2. Semantic Kernel (Microsoft)

A mature SDK with plugins (our tools map to plugins), planners, and connectors for several model providers. It is Microsoft-backed and has documented Azure integration.

| Area | Assessment |
|---|---|
| Fit to the limits | Good. Function-calling filters can enforce a call limit. |
| Dependencies | Larger. Many connectors we would not use. |
| Learning curve | Medium. It has its own concepts (kernel, plugins, filters). |
| Multi-agent | Available through its agent APIs. |
| Lock-in | Medium. Our tools become Semantic Kernel plugins. |
| Maturity | Established. Confirm its current release status and the direction Microsoft gives it before choosing. |

### 3. Microsoft Agent Framework

Microsoft's newer agent SDK. It is positioned as the successor to parts of Semantic Kernel and AutoGen. Check its release status before choosing: it may still be preview, and its APIs may change.

| Area | Assessment |
|---|---|
| Fit to the limits | Good, if its tool-call controls cover the limit. Verify this in its docs. |
| Dependencies | Medium. |
| Learning curve | Medium. |
| Multi-agent | Designed for it. |
| Lock-in | Medium to high if its API is still changing. |
| Maturity | Verify before choosing. A preview API is a risk for a production app. |

### 4. LangGraph (LangChain)

Builds agents as explicit graphs of steps and state. Good for loops with branches, retries, and human review.

| Area | Assessment |
|---|---|
| Fit to the limits | Good. The call limit is a graph state counter. |
| Dependencies | Medium to large (LangChain packages). |
| Learning curve | Medium to high. Graphs and state need care. |
| Multi-agent | Strong. |
| Lock-in | Medium. A third-party framework, not from Microsoft. |
| Maturity | Widely used. Confirm the current version and its license before choosing. |

## Comparison

| Criterion | 1. Plain Python | 2. Semantic Kernel | 3. Agent Framework | 4. LangGraph |
|---|---|---|---|---|
| Fit for one agent with one tool | High | Medium | Medium | Medium |
| Fit for many agents later | Low | High | High | High |
| Code to own and review | Most | Less | Less | Less |
| Dependency weight | Smallest | Large | Medium | Large |
| Test without Azure | Easiest | Medium | Medium | Medium |
| Lock-in | Lowest | Medium | Medium to high | Medium |
| Maturity risk | Low | Low | Check status | Low |

## Recommendation

**Option 1 (plain Python with the model API)** for now. The scope is one agent and one tool. Our code enforces the call limit and source rules directly, and it is the easiest to test without Azure. When the design needs several agents, we can move to Semantic Kernel or Agent Framework. Our tool functions would carry over.

The reason to pick a framework now is multi-agent work. If that is planned soon, **Option 2 (Semantic Kernel)** is the safer choice, because it is established. I recommend against Option 3 until its release status is confirmed.

## Decisions you must make

1. **Framework:** option 1, 2, 3, or 4.
2. **Model provider:** the frameworks differ in which providers they support. Choose the model endpoint (Azure AI Foundry or the Anthropic API) before the framework is final. The endpoint choice changes how the managed identity and the API key are handled.
3. **Multi-agent timing:** do you need several agents soon?

## Not decided here

- Model provider and its authentication (decision 2).
- Prompt design and the list of tools beyond PokeAPI.
