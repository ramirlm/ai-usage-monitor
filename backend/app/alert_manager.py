"""Alert management system."""

from typing import Optional
from datetime import datetime
from database import Database


class AlertManager:
    """Manages alerts for budget thresholds, anomalies, etc."""
    
    def __init__(self, db: Database):
        """Initialize alert manager.
        
        Args:
            db: Database instance
        """
        self.db = db
        
    def check_budget_threshold(self, service: Optional[str] = None):
        """Check if budget threshold has been exceeded.
        
        Args:
            service: Optional service name to check
        """
        now = datetime.now()
        
        # Get budget settings
        budget = self.db.get_budget(service=service)
        if not budget:
            return
        
        monthly_budget = budget['monthly_budget']
        alert_threshold = budget['alert_threshold']
        threshold_amount = monthly_budget * alert_threshold
        
        # Get current spending
        current_cost = self.db.get_monthly_cost(now.year, now.month, service=service)
        
        # Check if threshold exceeded
        if current_cost >= threshold_amount:
            percentage = (current_cost / monthly_budget) * 100
            service_name = service if service else "Total"
            
            message = f"{service_name} spending has reached {percentage:.1f}% of monthly budget"
            details = f"Current: ${current_cost:.2f}, Budget: ${monthly_budget:.2f}, Threshold: {alert_threshold*100}%"
            
            # Determine severity
            if current_cost >= monthly_budget:
                severity = "critical"
            elif current_cost >= monthly_budget * 0.9:
                severity = "error"
            else:
                severity = "warning"
            
            self.db.add_alert("budget_threshold", severity, message, details)
            
    def check_projection_overage(self, service: Optional[str] = None):
        """Check if projected monthly cost will exceed budget.
        
        Args:
            service: Optional service name to check
        """
        now = datetime.now()
        
        # Get budget settings
        budget = self.db.get_budget(service=service)
        if not budget:
            return
        
        monthly_budget = budget['monthly_budget']
        
        # Get current spending
        current_cost = self.db.get_monthly_cost(now.year, now.month, service=service)
        
        # Project monthly cost
        day_of_month = now.day
        days_in_month = 30  # Simplified
        
        if day_of_month > 0:
            projected_cost = (current_cost / day_of_month) * days_in_month
            
            # Check if projection exceeds budget
            if projected_cost > monthly_budget:
                overage = projected_cost - monthly_budget
                percentage = (projected_cost / monthly_budget) * 100
                service_name = service if service else "Total"
                
                message = f"{service_name} projected to exceed budget by ${overage:.2f}"
                details = f"Projected: ${projected_cost:.2f}, Budget: ${monthly_budget:.2f} ({percentage:.1f}%)"
                
                self.db.add_alert("projection_overage", "warning", message, details)
                
    def check_anomaly(self, service: Optional[str] = None):
        """Check for anomalous spending patterns.
        
        Args:
            service: Optional service name to check
        """
        # Get last 7 days of daily costs
        daily_costs = self.db.get_daily_costs(days=7)
        
        if len(daily_costs) < 3:
            return  # Not enough data
        
        # Calculate average (excluding today)
        costs = [day['total_cost'] for day in daily_costs[:-1]]
        avg_cost = sum(costs) / len(costs) if costs else 0
        
        # Check today's cost
        if daily_costs:
            today_cost = daily_costs[-1]['total_cost']
            
            # Alert if today is 2x the average
            if today_cost > avg_cost * 2 and avg_cost > 0:
                service_name = service if service else "Total"
                message = f"{service_name} spending is {today_cost/avg_cost:.1f}x the 7-day average"
                details = f"Today: ${today_cost:.2f}, Avg: ${avg_cost:.2f}"
                
                self.db.add_alert("anomaly_detection", "warning", message, details)
