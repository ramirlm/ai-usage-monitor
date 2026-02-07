"""CLI extensions for the AI Usage Monitor.

New commands:
- sync: Sync usage data from APIs
- budget: Manage budget settings
- report: Generate usage reports
- export: Export data
- dashboard: Start the web dashboard
"""

import argparse
import sys
import os
from datetime import datetime
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import Database
from app.cost_calculator import CostCalculator
from app.alert_manager import AlertManager


DB_PATH = os.path.join(os.path.dirname(__file__), 'ai-usage.db')


def cmd_init(args):
    """Initialize the database."""
    db = Database(DB_PATH)
    db.connect()
    db.init_schema()
    db.close()
    print("✓ Database initialized successfully!")
    print(f"  Location: {DB_PATH}")


def cmd_sync(args):
    """Sync usage data from AI service APIs."""
    print("Syncing usage data from AI services...")
    
    # This would fetch real data from APIs
    # For now, we'll just print a message
    print("⚠ Note: API sync requires implementation of service-specific data fetchers")
    print("  Services to sync: Anthropic (Claude), OpenAI, Synthetic")
    print("  Use the API endpoints to manually add usage data for now")


def cmd_budget_set(args):
    """Set budget."""
    db = Database(DB_PATH)
    db.connect()
    
    service = args.service if hasattr(args, 'service') and args.service else None
    db.set_budget(args.amount, service=service, alert_threshold=args.threshold)
    
    db.close()
    
    service_name = service if service else "Global"
    print(f"✓ {service_name} budget set to ${args.amount:.2f}")
    print(f"  Alert threshold: {args.threshold*100:.0f}%")


def cmd_budget_status(args):
    """Show budget status."""
    db = Database(DB_PATH)
    db.connect()
    
    now = datetime.now()
    
    # Get global budget
    budget = db.get_budget()
    if budget:
        print(f"\n{'='*60}")
        print(f"  Budget Status - {now.strftime('%B %Y')}")
        print(f"{'='*60}")
        
        monthly_cost = db.get_monthly_cost(now.year, now.month)
        budget_amount = budget['monthly_budget']
        percentage = (monthly_cost / budget_amount * 100) if budget_amount > 0 else 0
        
        # Project monthly cost
        day_of_month = now.day
        days_in_month = 30
        projected = (monthly_cost / day_of_month * days_in_month) if day_of_month > 0 else 0
        
        print(f"\n  Global Budget:      ${budget_amount:.2f}")
        print(f"  Current Spend:      ${monthly_cost:.2f} ({percentage:.1f}%)")
        print(f"  Projected:          ${projected:.2f}")
        print(f"  Remaining:          ${max(0, budget_amount - monthly_cost):.2f}")
        
        if projected > budget_amount:
            print(f"  ⚠ Warning: Projected to exceed budget by ${projected - budget_amount:.2f}")
        
        # Service breakdown
        print(f"\n  Service Breakdown:")
        print(f"  {'-'*56}")
        
        services = db.get_service_breakdown(now.year, now.month)
        for service in services:
            svc_percentage = (service['total_cost'] / monthly_cost * 100) if monthly_cost > 0 else 0
            print(f"  {service['service']:20} ${service['total_cost']:8.2f}  ({svc_percentage:5.1f}%)")
        
        print(f"\n{'='*60}\n")
    else:
        print("No budget set. Use 'budget set' to configure a budget.")
    
    db.close()


def cmd_report(args):
    """Generate usage report."""
    db = Database(DB_PATH)
    db.connect()
    
    # Parse month (YYYY-MM format)
    if args.month:
        year, month = map(int, args.month.split('-'))
    else:
        now = datetime.now()
        year, month = now.year, now.month
    
    print(f"\n{'='*70}")
    print(f"  AI Usage Report - {year}-{month:02d}")
    print(f"{'='*70}")
    
    # Get monthly cost
    monthly_cost = db.get_monthly_cost(year, month)
    print(f"\n  Total Monthly Cost: ${monthly_cost:.2f}")
    
    # Service breakdown
    print(f"\n  Cost by Service:")
    print(f"  {'-'*66}")
    
    services = db.get_service_breakdown(year, month)
    for service in services:
        percentage = (service['total_cost'] / monthly_cost * 100) if monthly_cost > 0 else 0
        print(f"  {service['service']:20} ${service['total_cost']:8.2f}  " +
              f"({percentage:5.1f}%)  {service['total_tokens']:,} tokens")
    
    print(f"\n{'='*70}\n")
    
    db.close()


def cmd_export(args):
    """Export usage data."""
    print(f"Exporting data from {args.start} to {args.end} in {args.format} format...")
    print("⚠ Export functionality requires implementation")
    print("  Use SQLite tools to query ai-usage.db directly for now")


def cmd_dashboard(args):
    """Start the web dashboard."""
    print("Starting AI Usage Monitor Dashboard...")
    print("Dashboard will be available at: http://localhost:3000")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Import and run Flask server
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    from app.server import app, DB_PATH as server_db_path, Database as ServerDatabase
    
    # Initialize database
    db = ServerDatabase(server_db_path)
    db.connect()
    db.init_schema()
    db.close()
    
    # Start server
    app.run(host='0.0.0.0', port=3000, debug=False)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Usage Monitor - Extended CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize database')
    parser_init.set_defaults(func=cmd_init)
    
    # Sync command
    parser_sync = subparsers.add_parser('sync', help='Sync usage data from APIs')
    parser_sync.set_defaults(func=cmd_sync)
    
    # Budget commands
    parser_budget = subparsers.add_parser('budget', help='Manage budgets')
    budget_subparsers = parser_budget.add_subparsers(dest='budget_command')
    
    budget_set = budget_subparsers.add_parser('set', help='Set budget')
    budget_set.add_argument('amount', type=float, help='Budget amount in dollars')
    budget_set.add_argument('--service', help='Service name (optional, for service-specific budget)')
    budget_set.add_argument('--threshold', type=float, default=0.8, help='Alert threshold (0.0-1.0)')
    budget_set.set_defaults(func=cmd_budget_set)
    
    budget_status = budget_subparsers.add_parser('status', help='Show budget status')
    budget_status.set_defaults(func=cmd_budget_status)
    
    # Report command
    parser_report = subparsers.add_parser('report', help='Generate usage report')
    parser_report.add_argument('--month', help='Month in YYYY-MM format (default: current month)')
    parser_report.add_argument('--format', choices=['text', 'pdf'], default='text', help='Output format')
    parser_report.set_defaults(func=cmd_report)
    
    # Export command
    parser_export = subparsers.add_parser('export', help='Export usage data')
    parser_export.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser_export.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser_export.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')
    parser_export.set_defaults(func=cmd_export)
    
    # Dashboard command
    parser_dashboard = subparsers.add_parser('dashboard', help='Start web dashboard')
    parser_dashboard.set_defaults(func=cmd_dashboard)
    
    # Parse and execute
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
