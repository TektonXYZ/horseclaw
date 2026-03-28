#!/usr/bin/env python3
"""
HorseClaw CLI
HorseClaw 命令行接口

Command-line interface for HorseClaw operations.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from horseclaw import HorseClaw


def cmd_init(args):
    """Initialize a new HorseClaw instance."""
    horse = HorseClaw(language=args.language, state_file=args.state_file)
    horse.save_state()
    print(f"✓ Initialized HorseClaw at {args.state_file}")


def cmd_status(args):
    """Show system status."""
    horse = HorseClaw(state_file=args.state_file)
    report = horse.get_full_report()
    
    print("\n" + "="*50)
    print(f"  {report['system']['name']} v{report['system']['version']}")
    print("="*50)
    print(f"\nLanguage: {report['system']['language']}")
    print(f"Active: {report['system']['is_active']}")
    print(f"\nAgents: {report['agents']['active']} active / {report['agents']['total']} total")
    print(f"Fees Collected: ${report['finance']['fees_collected']}")
    print(f"\nToken Pools:")
    print(f"  Claude: {report['finance']['token_pools']['claude']['available_tokens']:,} available")
    print(f"  Kimi: {report['finance']['token_pools']['kimi']['available_tokens']:,} available")
    print(f"\nAllocation Stats:")
    print(f"  Total Requests: {report['allocation']['total_requests']}")
    print(f"  Fulfillment Rate: {report['allocation']['fulfillment_rate']:.1%}")


def cmd_register(args):
    """Register a new agent."""
    horse = HorseClaw(state_file=args.state_file)
    result = horse.register_agent(args.agent_id, args.name, args.metadata)
    horse.save_state()
    
    if result['success']:
        print(f"✓ Registered agent: {args.name} ({args.agent_id})")
    else:
        print(f"✗ Failed: {result['message']}")


def cmd_agents(args):
    """List all agents."""
    horse = HorseClaw(state_file=args.state_file)
    agents = horse.list_agents(active_only=not args.all)
    
    print(f"\n{'ID':<20} {'Name':<25} {'Status':<10}")
    print("-" * 60)
    for agent in agents:
        status = "Active" if agent['is_active'] else "Inactive"
        print(f"{agent['agent_id']:<20} {agent['name']:<25} {status:<10}")


def cmd_collect(args):
    """Collect a fee."""
    horse = HorseClaw(state_file=args.state_file)
    result = horse.collect_fee(args.source, args.amount, args.currency)
    horse.save_state()
    
    if result['success']:
        print(f"✓ Collected ${args.amount} {args.currency} from {args.source}")
        print(f"  Payment ID: {result['payment_id']}")
        print(f"  New Balance: ${result['balance']}")
    else:
        print(f"✗ Failed: {result['message']}")


def cmd_convert(args):
    """Convert fees to tokens."""
    horse = HorseClaw(state_file=args.state_file)
    allocation = {"claude": args.claude_pct / 100, "kimi": args.kimi_pct / 100}
    result = horse.convert_fees_to_tokens(args.amount, allocation)
    horse.save_state()
    
    if result['success']:
        print(f"✓ Converted ${args.amount} to tokens:")
        print(f"  Claude: {result['tokens']['claude']:,} tokens")
        print(f"  Kimi: {result['tokens']['kimi']:,} tokens")
    else:
        print(f"✗ Failed: {result['message']}")


def cmd_request(args):
    """Request token allocation."""
    horse = HorseClaw(state_file=args.state_file)
    result = horse.request_tokens(args.agent_id, args.model, args.tokens, args.priority)
    horse.save_state()
    
    status_icon = "✓" if result['status'] == 'approved' else "~" if result['status'] == 'partial' else "✗"
    print(f"{status_icon} Request {result['status'].upper()}")
    print(f"  Granted: {result['tokens_granted']:,} / {result['tokens_requested']:,}")
    print(f"  Reason: {result['reason']}")


def cmd_pools(args):
    """Show token pools."""
    horse = HorseClaw(state_file=args.state_file)
    pools = horse.get_token_pools()
    
    print("\nToken Pools:")
    for model, pool in pools.items():
        print(f"\n  {model.upper()}:")
        print(f"    Total: {pool['total_tokens']:,}")
        print(f"    Available: {pool['available_tokens']:,}")
        print(f"    Allocated: {pool['allocated_tokens']:,}")


def cmd_report(args):
    """Show full report."""
    horse = HorseClaw(state_file=args.state_file)
    report = horse.get_full_report()
    
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("\n" + "="*60)
        print(json.dumps(report, indent=2, ensure_ascii=False))


def cmd_api(args):
    """Process JSON API request."""
    horse = HorseClaw(state_file=args.state_file)
    
    if args.file:
        with open(args.file) as f:
            request = f.read()
    else:
        request = args.request
    
    response = horse.process_json_request(request)
    print(response)


def main():
    parser = argparse.ArgumentParser(
        description='HorseClaw - AI Token Budget Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  horseclaw init --state-file /var/horseclaw/state.json
  horseclaw register my_bot "My Bot" --state-file state.json
  horseclaw collect my_bot 100.00 --state-file state.json
  horseclaw convert 80.00 --claude-pct 60 --kimi-pct 40
  horseclaw request my_bot claude 5000 high
        """
    )
    parser.add_argument('--state-file', default='horseclaw_state.json',
                       help='Path to state file')
    parser.add_argument('--language', default='en', choices=['en', 'zh'],
                       help='Language (en/zh)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init
    init_parser = subparsers.add_parser('init', help='Initialize HorseClaw')
    init_parser.set_defaults(func=cmd_init)
    
    # status
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=cmd_status)
    
    # register
    register_parser = subparsers.add_parser('register', help='Register an agent')
    register_parser.add_argument('agent_id', help='Unique agent ID')
    register_parser.add_argument('name', help='Agent name')
    register_parser.add_argument('--metadata', type=json.loads, default={},
                                help='JSON metadata')
    register_parser.set_defaults(func=cmd_register)
    
    # agents
    agents_parser = subparsers.add_parser('agents', help='List agents')
    agents_parser.add_argument('--all', action='store_true',
                              help='Show inactive agents too')
    agents_parser.set_defaults(func=cmd_agents)
    
    # collect
    collect_parser = subparsers.add_parser('collect', help='Collect a fee')
    collect_parser.add_argument('source', help='Fee source')
    collect_parser.add_argument('amount', type=float, help='Amount')
    collect_parser.add_argument('--currency', default='USD', help='Currency')
    collect_parser.set_defaults(func=cmd_collect)
    
    # convert
    convert_parser = subparsers.add_parser('convert', help='Convert fees to tokens')
    convert_parser.add_argument('amount', type=float, help='USD amount')
    convert_parser.add_argument('--claude-pct', type=float, default=50,
                               help='Percentage for Claude')
    convert_parser.add_argument('--kimi-pct', type=float, default=50,
                               help='Percentage for Kimi')
    convert_parser.set_defaults(func=cmd_convert)
    
    # request
    request_parser = subparsers.add_parser('request', help='Request tokens')
    request_parser.add_argument('agent_id', help='Agent ID')
    request_parser.add_argument('model', choices=['claude', 'kimi'], help='Model')
    request_parser.add_argument('tokens', type=int, help='Token amount')
    request_parser.add_argument('priority', choices=['low', 'normal', 'high', 'critical'],
                               default='normal', help='Priority')
    request_parser.set_defaults(func=cmd_request)
    
    # pools
    pools_parser = subparsers.add_parser('pools', help='Show token pools')
    pools_parser.set_defaults(func=cmd_pools)
    
    # report
    report_parser = subparsers.add_parser('report', help='Show full report')
    report_parser.add_argument('--json', action='store_true', help='Output as JSON')
    report_parser.set_defaults(func=cmd_report)
    
    # api
    api_parser = subparsers.add_parser('api', help='Process JSON API request')
    api_parser.add_argument('--request', help='JSON request string')
    api_parser.add_argument('--file', help='JSON request file')
    api_parser.set_defaults(func=cmd_api)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
