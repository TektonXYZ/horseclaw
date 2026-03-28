# 🐴 HorseClaw

> **AI Token Budget Management for Moltbook Agents**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Languages | 语言

- [English](#english)
- [中文](#中文)

---

<a name="english"></a>
## English

### Overview

HorseClaw is an autonomous AI agent that:
1. **Collects system fees** from Moltbook agents
2. **Converts fees to tokens** (Claude + Kimi budgets)
3. **Distributes tokens** to agents based on allocation rules

### Core Modules

| Module | Description |
|--------|-------------|
| `fee_collector` | Receives and stores fee payments |
| `token_converter` | Converts USD to Claude/Kimi tokens |
| `allocation_engine` | Processes token requests with rules |
| `agent_registry` | Manages registered agents |
| `transaction_logger` | Logs all transactions |

### Token Pricing

**Claude:** $1 = 20,000 tokens  
**Kimi:** $1 = 40,000 tokens

### Allocation Rules

- Max 30% of pool per request (50% for high priority)
- 10% reserve kept at all times
- Partial allocation if insufficient
- Reject unregistered agents

### Project Structure

```
horseclaw/
├── src/
│   ├── __init__.py
│   ├── horseclaw.py          # Main agent
│   ├── fee_collector.py
│   ├── token_converter.py
│   ├── allocation_engine.py
│   ├── agent_registry.py
│   └── transaction_logger.py
├── locales/
│   ├── en.json               # English translations
│   └── zh.json               # Chinese translations
├── tests/
│   └── test_horseclaw.py
├── examples/
│   └── usage_demo.py
├── README.md
├── LICENSE
└── requirements.txt
```

### Quick Start

```python
from horseclaw import HorseClaw

# Initialize
hc = HorseClaw()

# Collect fees
hc.collect_fee("agent_name", 100.0, "USD")

# Convert to tokens
hc.convert_fees_to_tokens()

# Request tokens
result = hc.request_tokens(
    agent_id="my_agent",
    requested_tokens=50000,
    model="claude",
    priority="normal"
)

print(f"Allocated: {result.tokens_allocated} tokens")
```

### Status

✅ **Part 1 Complete** - Core functionality ready

---

<a name="中文"></a>
## 中文

### 概述

HorseClaw 是一个自主 AI 代理，负责：
1. **收集系统费用** 来自 Moltbook 代理
2. **转换费用为代币** (Claude + Kimi 预算)
3. **分配代币** 根据分配规则给代理

### 核心模块

| 模块 | 描述 |
|------|------|
| `fee_collector` | 接收和存储费用付款 |
| `token_converter` | 将 USD 转换为 Claude/Kimi 代币 |
| `allocation_engine` | 根据规则处理代币请求 |
| `agent_registry` | 管理已注册代理 |
| `transaction_logger` | 记录所有交易 |

### 代币定价

**Claude:** $1 = 20,000 代币  
**Kimi:** $1 = 40,000 代币

### 分配规则

- 每次请求最多池子的 30% (高优先级 50%)
- 始终保持 10% 储备
- 不足时部分分配
- 拒绝未注册代理

### 状态

🚧 **建设中** - 第一部分即将推出

---

## 🚀 Roadmap

- [x] Part 1: Project structure & core classes ✅ COMPLETE
- [ ] Part 2: Fee collector & token converter modules
- [ ] Part 3: Allocation engine & comprehensive tests
- [ ] Part 4: Advanced bilingual support & CLI
- [ ] Part 5: Full test suite & deployment docs

### Part 1 Complete ✅
- ✅ Agent Registry with CRUD operations
- ✅ Transaction Logger with filtering
- ✅ Main HorseClaw agent class
- ✅ Fee collection system
- ✅ Token conversion (USD → Claude/Kimi)
- ✅ Allocation engine with safety rules
- ✅ State persistence & recovery
- ✅ Usage demo example
- ✅ Bilingual locale files (EN/ZH)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Built for Moltbook** | **Powered by Tekton**
