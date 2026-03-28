#!/usr/bin/env python3
"""
HorseClaw Usage Demo
HorseClaw 使用演示

Comprehensive examples showing all HorseClaw features.
展示 HorseClaw 所有功能的综合示例。
"""

import json
from horseclaw import HorseClaw, Priority


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def demo_basic_usage():
    """Demo 1: Basic Usage / 基本使用"""
    print_section("Demo 1: Basic Usage / 基本使用")
    
    # Initialize HorseClaw (English)
    horse = HorseClaw(language="en")
    print("✓ HorseClaw initialized (English)")
    
    # Register agents
    print("\n--- Registering Agents / 注册代理 ---")
    result = horse.register_agent("trading_bot", "Trading Bot", {"type": "automation"})
    print_json(result)
    
    result = horse.register_agent("analyzer", "Market Analyzer", {"type": "analysis"})
    print_json(result)
    
    # Collect fees
    print("\n--- Collecting Fees / 收集费用 ---")
    result = horse.collect_fee("trading_bot", 500.00, "USD", {"period": "monthly"})
    print_json(result)
    
    result = horse.collect_fee("analyzer", 300.00, "USD", {"period": "monthly"})
    print_json(result)
    
    # Check balance
    print("\n--- Fee Balance / 费用余额 ---")
    balance = horse.get_fee_balance()
    print_json(balance)
    
    # Convert to tokens
    print("\n--- Converting to Tokens / 转换为代币 ---")
    result = horse.convert_fees_to_tokens(600.00, {"claude": 0.6, "kimi": 0.4})
    print_json(result)
    
    # Check token pools
    print("\n--- Token Pools / 代币池 ---")
    pools = horse.get_token_pools()
    print_json(pools)


def demo_allocation():
    """Demo 2: Token Allocation / 代币分配"""
    print_section("Demo 2: Token Allocation / 代币分配")
    
    horse = HorseClaw(language="en")
    
    # Setup
    horse.register_agent("agent_1", "Agent One")
    horse.register_agent("agent_2", "Agent Two")
    horse.collect_fee("system", 1000.00)
    horse.convert_fees_to_tokens(800.00)
    
    print(f"Initial pools: {json.dumps(horse.get_token_pools(), indent=2)}")
    
    # Request 1: Normal priority (max 30%)
    print("\n--- Request 1: Normal Priority (4000 tokens) ---")
    result = horse.request_tokens("agent_1", "claude", 4000, "normal")
    print(f"Status: {result['status']}")
    print(f"Granted: {result['tokens_granted']}")
    print(f"Reason: {result['reason']}")
    
    # Request 2: High priority (max 50%)
    print("\n--- Request 2: High Priority (5000 tokens) ---")
    result = horse.request_tokens("agent_2", "kimi", 5000, "high")
    print(f"Status: {result['status']}")
    print(f"Granted: {result['tokens_granted']}")
    
    # Request 3: Too much (should be partial)
    print("\n--- Request 3: Excessive Request (10000 tokens) ---")
    result = horse.request_tokens("agent_1", "claude", 10000, "normal")
    print(f"Status: {result['status']}")
    print(f"Granted: {result['tokens_granted']}")
    print(f"Reason: {result['reason']}")
    
    # Check stats
    print("\n--- Allocation Statistics / 分配统计 ---")
    stats = horse.get_allocation_stats()
    print_json(stats)


def demo_bilingual():
    """Demo 3: Bilingual Support / 双语支持"""
    print_section("Demo 3: Bilingual Support / 双语支持")
    
    # English
    print("\n--- English Mode / 英文模式 ---")
    horse_en = HorseClaw(language="en")
    print(f"Welcome: {horse_en.i18n('welcome')}")
    print(f"Status: {horse_en.i18n('status_ready')}")
    print(f"Pricing: {horse_en.i18n('price_claude')}")
    
    # Chinese
    print("\n--- Chinese Mode / 中文模式 ---")
    horse_zh = HorseClaw(language="zh")
    print(f"Welcome: {horse_zh.i18n('welcome')}")
    print(f"Status: {horse_zh.i18n('status_ready')}")
    print(f"Pricing: {horse_zh.i18n('price_claude')}")
    
    # Switch language
    print("\n--- Switching Language / 切换语言 ---")
    horse_en.set_language("zh")
    print(f"Now in Chinese: {horse_en.i18n('welcome')}")


def demo_json_api():
    """Demo 4: JSON API Interface / JSON API 接口"""
    print_section("Demo 4: JSON API / JSON 接口")
    
    horse = HorseClaw(language="en")
    
    # Example 1: Register via JSON
    print("\n--- JSON: Register Agent ---")
    request = json.dumps({
        "action": "register_agent",
        "agent_id": "json_bot",
        "name": "JSON Bot",
        "metadata": {"source": "json_api"}
    })
    response = horse.process_json_request(request)
    print("Request:", request)
    print("Response:", response)
    
    # Example 2: Collect fee via JSON
    print("\n--- JSON: Collect Fee ---")
    request = json.dumps({
        "action": "collect_fee",
        "source": "json_bot",
        "amount": 250.00,
        "currency": "USD"
    })
    response = horse.process_json_request(request)
    print("Response:", response)
    
    # Example 3: Get status
    print("\n--- JSON: Get Status ---")
    request = json.dumps({"action": "get_status"})
    response = horse.process_json_request(request)
    print("Response:", response)
    
    # Example 4: Error handling
    print("\n--- JSON: Error Handling ---")
    request = json.dumps({"action": "unknown_action"})
    response = horse.process_json_request(request)
    print("Response:", response)


def demo_persistence():
    """Demo 5: State Persistence / 状态持久化"""
    print_section("Demo 5: State Persistence / 状态持久化")
    
    # Create and populate
    print("\n--- Creating State / 创建状态 ---")
    horse = HorseClaw(language="en", state_file="/tmp/horseclaw_state.json")
    
    horse.register_agent("persistent_agent", "Persistent Agent")
    horse.collect_fee("system", 500.00)
    horse.convert_fees_to_tokens(400.00)
    horse.request_tokens("persistent_agent", "claude", 2000, "high")
    
    print(f"Agents: {horse.registry.get_agent_count()}")
    print(f"Fees: {horse.fee_collector.get_total_balance_usd()}")
    print(f"Tokens: {horse.token_converter.get_total_tokens()}")
    
    # Save state
    print("\n--- Saving State / 保存状态 ---")
    result = horse.save_state()
    print_json(result)
    
    # Create new instance and load
    print("\n--- Loading State / 加载状态 ---")
    horse2 = HorseClaw(language="en", state_file="/tmp/horseclaw_state.json")
    
    print(f"Agents: {horse2.registry.get_agent_count()}")
    print(f"Fees: {horse2.fee_collector.get_total_balance_usd()}")
    print(f"Tokens: {horse2.token_converter.get_total_tokens()}")
    print(f"Transactions: {len(horse2.logger.get_all_transactions())}")


def demo_full_report():
    """Demo 6: Full System Report / 完整系统报告"""
    print_section("Demo 6: Full Report / 完整报告")
    
    horse = HorseClaw(language="en")
    
    # Populate with data
    for i in range(5):
        horse.register_agent(f"agent_{i}", f"Agent {i}")
    
    for i in range(10):
        horse.collect_fee(f"agent_{i % 5}", 100.00 + i * 10)
    
    horse.convert_fees_to_tokens(500.00)
    
    # Generate full report
    report = horse.get_full_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))


def demo_edge_cases():
    """Demo 7: Edge Cases / 边界情况"""
    print_section("Demo 7: Edge Cases / 边界情况")
    
    horse = HorseClaw(language="en")
    horse.collect_fee("system", 100.00)
    horse.convert_fees_to_tokens(100.00)
    
    # Unregistered agent
    print("\n--- Unregistered Agent / 未注册代理 ---")
    result = horse.request_tokens("unknown_agent", "claude", 1000)
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    # Excessive request
    print("\n--- Excessive Request / 过度请求 ---")
    horse.register_agent("test_agent", "Test Agent")
    result = horse.request_tokens("test_agent", "claude", 100000, "normal")
    print(f"Status: {result['status']}")
    print(f"Granted: {result['tokens_granted']}")
    print(f"Reason: {result['reason']}")
    
    # Negative fee attempt
    print("\n--- Negative Fee / 负费用 ---")
    result = horse.collect_fee("system", -50.00)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  HorseClaw Complete Demo")
    print("  HorseClaw 完整演示")
    print("=" * 60)
    
    demo_basic_usage()
    demo_allocation()
    demo_bilingual()
    demo_json_api()
    demo_persistence()
    demo_full_report()
    demo_edge_cases()
    
    print("\n" + "=" * 60)
    print("  All demos completed!")
    print("  所有演示完成！")
    print("=" * 60)
