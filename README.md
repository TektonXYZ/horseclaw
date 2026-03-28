# 🐴 HorseClaw

> **AI Token Budget Management for Moltbook Agents**
> **Moltbook 代理的 AI 代币预算管理**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-35+-brightgreen.svg)](tests/)

---

## 🌐 Language Selection | 语言选择

- [🇺🇸 English](#english)
- [🇨🇳 中文](#chinese)

---

<a name="english"></a>
## 🇺🇸 English

### Overview

HorseClaw is an autonomous AI agent that manages AI token budgets for the Moltbook ecosystem. It collects system fees, converts them to Claude and Kimi token pools, and distributes tokens to registered agents based on configurable allocation rules.

### Features

- 💰 **Fee Collection** - Receive USD/USDC/USDT payments
- 🔄 **Token Conversion** - Convert fees to Claude/Kimi tokens at fixed rates
- 📊 **Smart Allocation** - Distribute tokens with configurable rules
- 🛡️ **Safety First** - 10% reserve, max 30%/50% allocation limits
- 🌍 **Bilingual** - Full English and Chinese (中文) support
- 🔌 **JSON API** - Easy integration via JSON interface
- 💾 **Persistent** - Save/load complete system state
- 📈 **Observable** - Full statistics and transaction logging

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HorseClaw Core                        │
├─────────────┬─────────────┬─────────────┬───────────────┤
│ Fee         │ Token       │ Allocation  │ Agent         │
│ Collector   │ Converter   │ Engine      │ Registry      │
├─────────────┴─────────────┴─────────────┴───────────────┤
│              Transaction Logger + I18n                   │
└─────────────────────────────────────────────────────────┘
```

### Quick Start

```python
from horseclaw import HorseClaw

# Initialize
horse = HorseClaw(language="en")

# Register agents
horse.register_agent("trading_bot", "Trading Bot")

# Collect fees
horse.collect_fee("trading_bot", 1000.00, "USD")

# Convert to tokens
horse.convert_fees_to_tokens(800.00, {"claude": 0.6, "kimi": 0.4})

# Request tokens
result = horse.request_tokens("trading_bot", "claude", 5000, "high")
print(f"Granted: {result['tokens_granted']}")
```

### Token Pricing

| Model | Rate | Description |
|-------|------|-------------|
| **Claude** | $1 = 20,000 tokens | Anthropic Claude API |
| **Kimi** | $1 = 40,000 tokens | Moonshot Kimi API |

### Allocation Rules

1. **Never Negative** - System prevents overspending
2. **10% Reserve** - Always maintained for stability
3. **Max Allocation** - 30% normal, 50% high priority per request
4. **Partial Support** - Grant what's available if insufficient
5. **Registered Only** - Unregistered agents rejected

### JSON API

All operations available via JSON interface:

```python
# Register agent
request = {
    "action": "register_agent",
    "agent_id": "my_bot",
    "name": "My Bot"
}

# Collect fee
request = {
    "action": "collect_fee",
    "source": "my_bot",
    "amount": 100.00,
    "currency": "USD"
}

# Request tokens
request = {
    "action": "request_tokens",
    "agent_id": "my_bot",
    "model": "claude",
    "tokens": 5000,
    "priority": "high"
}

# Process
response = horse.process_json_request(json.dumps(request))
```

### Installation

```bash
# Clone repository
git clone https://github.com/TektonXYZ/horseclaw.git
cd horseclaw

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run demo
python examples/usage_demo.py
```

### Project Structure

```
horseclaw/
├── src/
│   ├── __init__.py              # Package exports
│   ├── horseclaw.py             # Main orchestrator (+i18n)
│   ├── agent_registry.py        # Agent management
│   ├── fee_collector.py         # Fee collection
│   ├── token_converter.py       # USD → tokens
│   ├── allocation_engine.py     # Allocation logic
│   └── transaction_logger.py    # Audit logging
├── locales/
│   ├── en.json                  # English strings
│   └── zh.json                  # Chinese strings
├── tests/
│   └── test_horseclaw.py        # 35+ unit tests
├── examples/
│   └── usage_demo.py            # Complete demos
├── README.md                    # This file
├── LICENSE                      # MIT License
└── requirements.txt             # Dependencies
```

### State Persistence

```python
# Save state
horse = HorseClaw(state_file="/path/to/state.json")
# ... operations ...
horse.save_state()

# Load state
horse2 = HorseClaw(state_file="/path/to/state.json")
# State restored: agents, balances, pools, history
```

### Safety Features

- **Decimal Precision** - No floating point errors
- **Validation** - All inputs validated
- **Reserve Requirements** - Prevents pool depletion
- **Audit Trail** - Every operation logged
- **State Recovery** - Restore from any saved state

---

<a name="chinese"></a>
## 🇨🇳 中文

### 概述

HorseClaw 是一个自主 AI 代理，为 Moltbook 生态系统管理 AI 代币预算。它收集系统费用，将其转换为 Claude 和 Kimi 代币池，并根据可配置的分配规则将代币分发给已注册的代理。

### 功能

- 💰 **费用收集** - 接收 USD/USDC/USDT 付款
- 🔄 **代币转换** - 按固定费率将费用转换为 Claude/Kimi 代币
- 📊 **智能分配** - 通过可配置规则分发代币
- 🛡️ **安全第一** - 10% 储备，最大 30%/50% 分配限制
- 🌍 **双语支持** - 完整的英语和中文支持
- 🔌 **JSON API** - 通过 JSON 接口轻松集成
- 💾 **持久化** - 保存/加载完整的系统状态
- 📈 **可观察** - 完整的统计和交易记录

### 架构

```
┌─────────────────────────────────────────────────────────┐
│                    HorseClaw 核心                        │
├─────────────┬─────────────┬─────────────┬───────────────┤
│ 费用        │ 代币        │ 分配        │ 代理          │
│ 收集器      │ 转换器      │ 引擎        │ 注册表        │
├─────────────┴─────────────┴─────────────┴───────────────┤
│              交易记录器 + 国际化                          │
└─────────────────────────────────────────────────────────┘
```

### 快速开始

```python
from horseclaw import HorseClaw

# 初始化
horse = HorseClaw(language="zh")

# 注册代理
horse.register_agent("trading_bot", "交易机器人")

# 收集费用
horse.collect_fee("trading_bot", 1000.00, "USD")

# 转换为代币
horse.convert_fees_to_tokens(800.00, {"claude": 0.6, "kimi": 0.4})

# 请求代币
result = horse.request_tokens("trading_bot", "claude", 5000, "high")
print(f"已授予: {result['tokens_granted']}")
```

### 代币定价

| 模型 | 费率 | 说明 |
|------|------|------|
| **Claude** | $1 = 20,000 代币 | Anthropic Claude API |
| **Kimi** | $1 = 40,000 代币 | Moonshot Kimi API |

### 分配规则

1. **永不负数** - 系统防止超支
2. **10% 储备** - 始终保持稳定性
3. **最大分配** - 普通 30%，高优先级 50%
4. **部分支持** - 不足时授予可用部分
5. **仅注册代理** - 拒绝未注册代理

### JSON API

所有操作都可通过 JSON 接口使用：

```python
# 注册代理
request = {
    "action": "register_agent",
    "agent_id": "my_bot",
    "name": "我的机器人"
}

# 收集费用
request = {
    "action": "collect_fee",
    "source": "my_bot",
    "amount": 100.00,
    "currency": "USD"
}

# 请求代币
request = {
    "action": "request_tokens",
    "agent_id": "my_bot",
    "model": "claude",
    "tokens": 5000,
    "priority": "high"
}

# 处理
response = horse.process_json_request(json.dumps(request))
```

### 安装

```bash
# 克隆仓库
git clone https://github.com/TektonXYZ/horseclaw.git
cd horseclaw

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 运行演示
python examples/usage_demo.py
```

### 项目结构

```
horseclaw/
├── src/
│   ├── __init__.py              # 包导出
│   ├── horseclaw.py             # 主协调器 (+i18n)
│   ├── agent_registry.py        # 代理管理
│   ├── fee_collector.py         # 费用收集
│   ├── token_converter.py       # USD → 代币
│   ├── allocation_engine.py     # 分配逻辑
│   └── transaction_logger.py    # 审计日志
├── locales/
│   ├── en.json                  # 英文字符串
│   └── zh.json                  # 中文字符串
├── tests/
│   └── test_horseclaw.py        # 35+ 单元测试
├── examples/
│   └── usage_demo.py            # 完整演示
├── README.md                    # 本文件
├── LICENSE                      # MIT 许可证
└── requirements.txt             # 依赖项
```

### 状态持久化

```python
# 保存状态
horse = HorseClaw(state_file="/path/to/state.json")
# ... 操作 ...
horse.save_state()

# 加载状态
horse2 = HorseClaw(state_file="/path/to/state.json")
# 状态恢复：代理、余额、池、历史
```

### 安全功能

- **Decimal 精度** - 无浮点错误
- **验证** - 所有输入都经过验证
- **储备要求** - 防止池耗尽
- **审计追踪** - 每个操作都记录
- **状态恢复** - 从任何保存的状态恢复

---

## 🚀 Roadmap

- [x] Part 1: Core modules (Agent Registry, Transaction Logger)
- [x] Part 2: Fee collection & token conversion
- [x] Part 3: Allocation engine with safety rules
- [x] Part 4: Main HorseClaw class + Bilingual i18n
- [x] Part 5: Tests & documentation

## 📊 Statistics

- **Total Lines of Code**: ~3,500+
- **Test Coverage**: 35+ unit tests
- **Languages**: English, 中文
- **Modules**: 5 core + 1 main
- **API Endpoints**: 10+ JSON actions

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Built for Moltbook** | **Powered by Tekton** | **Made with ❤️**

**为 Moltbook 构建** | **由 Tekton 驱动** | **用心制作 ❤️**
