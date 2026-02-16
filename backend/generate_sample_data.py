#!/usr/bin/env python3
"""Script to generate sample usage data for testing the dashboard."""

import sys
import os
from datetime import datetime, timedelta
import random

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import Database
from app.cost_calculator import CostCalculator

DB_PATH = os.path.join(os.path.dirname(__file__), 'ai-usage.db')


def generate_sample_data():
    """Generate sample usage data for testing."""
    db = Database(DB_PATH)
    db.connect()
    db.init_schema()
    
    print("Generating sample usage data...")
    
    # Set a default budget
    db.set_budget(300.0, service=None, alert_threshold=0.8)
    print("✓ Set global monthly budget to $300.00")
    
    # Set service-specific budgets for pay-as-you-go services
    db.set_budget(100.0, service='anthropic', alert_threshold=0.8)
    db.set_budget(80.0, service='openai', alert_threshold=0.8)
    print("✓ Set service-specific budgets")
    
    # Configure subscriptions for Cursor and Copilot
    db.set_subscription('cursor', 'pro', monthly_cost=20.0, monthly_limit=500, limit_type='requests')
    db.set_subscription('copilot', 'individual', monthly_cost=10.0, monthly_limit=None, limit_type='requests')
    print("✓ Configured subscriptions for Cursor AI and GitHub Copilot")
    
    # Generate data for the past 15 days
    today = datetime.now()
    
    services_models = [
        ('anthropic', 'claude-sonnet-4'),
        ('anthropic', 'claude-opus-4'),
        ('openai', 'gpt-4'),
        ('openai', 'gpt-3.5-turbo'),
        ('synthetic', 'default'),
        ('cursor', 'default'),
        ('copilot', 'default')
    ]
    
    total_cost = 0.0
    
    for day_offset in range(15, 0, -1):
        date = today - timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')
        
        # Generate 2-5 usage records per day
        num_records = random.randint(2, 5)
        
        for _ in range(num_records):
            service, model = random.choice(services_models)
            
            # For subscription services (cursor, copilot), use minimal token counts
            # and fixed costs based on subscription
            if service in ['cursor', 'copilot']:
                input_tokens = random.randint(1000, 10000)
                output_tokens = random.randint(100, 1000)
                # Cost is 0 for subscription services (already paid monthly fee)
                cost = 0.0
            else:
                # Generate random token counts for pay-as-you-go services
                input_tokens = random.randint(50000, 2000000)
                output_tokens = random.randint(10000, 500000)
                # Calculate cost
                cost = CostCalculator.calculate_cost(service, model, input_tokens, output_tokens)
            
            # Add usage snapshot
            db.add_usage_snapshot(service, model, input_tokens, output_tokens, cost)
            
            # Update daily summary
            db.update_daily_summary(date_str, service, model, input_tokens, output_tokens, cost)
            
            total_cost += cost
    
    print(f"✓ Generated usage data for the past 15 days")
    print(f"✓ Total cost generated: ${total_cost:.2f}")
    
    # Add subscription costs to total
    subscription_cost = 20.0 + 10.0  # Cursor Pro + Copilot Individual
    total_with_subscriptions = total_cost + subscription_cost
    print(f"✓ Total with subscriptions: ${total_with_subscriptions:.2f}")
    
    # Generate some alerts
    db.add_alert(
        "budget_threshold",
        "warning",
        "Monthly spending has reached 82.5% of budget",
        f"Current: ${total_cost:.2f}, Budget: $300.00"
    )
    print("✓ Created sample alert")
    
    # Get summary
    current_month_cost = db.get_monthly_cost(today.year, today.month)
    service_breakdown = db.get_service_breakdown(today.year, today.month)
    
    print(f"\n{'='*60}")
    print(f"  Sample Data Summary")
    print(f"{'='*60}")
    print(f"\n  Current Month Cost: ${current_month_cost:.2f}")
    print(f"  Subscription Costs: ${subscription_cost:.2f}")
    print(f"  Total Monthly Cost: ${current_month_cost + subscription_cost:.2f}")
    print(f"\n  Service Breakdown:")
    for svc in service_breakdown:
        percentage = (svc['total_cost'] / current_month_cost * 100) if current_month_cost > 0 else 0
        usage_count = db.get_monthly_usage_count(today.year, today.month, svc['service'])
        print(f"    {svc['service']:20} ${svc['total_cost']:8.2f}  ({percentage:5.1f}%)  {usage_count:4d} requests")
    print(f"\n{'='*60}\n")
    
    db.close()
    print("✓ Sample data generation complete!")
    print("\nYou can now start the dashboard with:")
    print("  python3 cli.py dashboard")
    print("\nOr start the server directly with:")
    print("  python3 app/server.py")


if __name__ == '__main__':
    generate_sample_data()
