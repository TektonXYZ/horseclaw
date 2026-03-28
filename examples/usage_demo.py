"""
HorseClaw Usage Example
HorseClaw 使用示例

Demonstrates how to use the HorseClaw agent.
演示如何使用 HorseClaw 代理。
"""

from src.horseclaw import HorseClaw
from src.agent_registry import AgentRegistry


def main():
    """Main demonstration."""
    print("=" * 60)
    print("🐴 HorseClaw - AI Token Budget Manager")
    print("=" * 60)
    print()
    
    # Initialize HorseClaw
    print("📦 Initializing HorseClaw...")
    horseclaw = HorseClaw()
    print("✅ HorseClaw initialized")
    print()
    
    # Show initial status
    print("📊 Initial Status:")
    status = horseclaw.get_status()
    print(f"   Total Agents: {status['agents']['total']}")
    print(f"   Active Agents: {status['agents']['active']}")
    print(f"   Token Pool Value: ${status['token_pool']['total_value_usd']}")
    print()
    
    # Part 1: Collect Fees
    print("💰 Part 1: Collecting Fees")
    print("-" * 40)
    
    result = horseclaw.collect_fee(
        source="market_analyzer",
        amount=100.0,
        currency="USD"
    )
    print(f"✅ Fee collected: {result['message']}")
    print(f"   New balance: ${result['new_balance_usd']}")
    print()
    
    # Part 2: Convert to Tokens
    print("🔄 Part 2: Converting Fees to Tokens")
    print("-" * 40)
    
    result = horseclaw.convert_fees_to_tokens()
    print(f"✅ {result['message']}")
    print(f"   Claude tokens: {result['conversion']['claude_tokens']:,}")
    print(f"   Kimi tokens: {result['conversion']['kimi_tokens']:,}")
    print()
    
    # Part 3: Register a New Agent
    print("👤 Part 3: Registering New Agent")
    print("-" * 40)
    
    success = horseclaw.registry.register(
        agent_id="trading_bot_01",
        name="Trading Bot Alpha",
        metadata={"type": "trading", "risk_level": "medium"}
    )
    print(f"✅ Agent registered: {success}")
    print(f"   Total agents: {horseclaw.registry.get_agent_count()}")
    print()
    
    # Part 4: Request Tokens
    print("🎫 Part 4: Requesting Tokens")
    print("-" * 40)
    
    # Normal priority request
    result1 = horseclaw.request_tokens(
        agent_id="trading_bot_01",
        requested_tokens=50000,
        model="claude",
        priority="normal"
    )
    print(f"📝 Normal Priority Request:")
    print(f"   Status: {result1.status}")
    print(f"   Tokens: {result1.tokens_allocated:,}")
    print(f"   Reason: {result1.reason}")
    print()
    
    # High priority request
    result2 = horseclaw.request_tokens(
        agent_id="trading_bot_01",
        requested_tokens=200000,
        model="kimi",
        priority="high"
    )
    print(f"📝 High Priority Request:")
    print(f"   Status: {result2.status}")
    print(f"   Tokens: {result2.tokens_allocated:,}")
    print(f"   Reason: {result2.reason}")
    print()
    
    # Unregistered agent request (should fail)
    result3 = horseclaw.request_tokens(
        agent_id="unknown_agent",
        requested_tokens=10000,
        model="claude"
    )
    print(f"📝 Unregistered Agent Request:")
    print(f"   Status: {result3.status}")
    print(f"   Reason: {result3.reason}")
    print()
    
    # Part 5: Show Final Status
    print("📈 Final Status")
    print("-" * 40)
    
    breakdown = horseclaw.get_pool_breakdown()
    print(f"Claude tokens: {breakdown['claude']['tokens']:,} (${breakdown['claude']['usd_value']})")
    print(f"Kimi tokens: {breakdown['kimi']['tokens']:,} (${breakdown['kimi']['usd_value']})")
    print(f"Reserve requirement: {breakdown['reserve_requirement']:,} tokens")
    print(f"Total USD value: ${breakdown['total_usd_value']}")
    print()
    
    # Show transaction log
    print("📝 Recent Transactions")
    print("-" * 40)
    stats = horseclaw.logger.get_stats()
    print(f"Total transactions: {stats['total_transactions']}")
    print(f"By type: {stats['by_type']}")
    print()
    
    print("=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
