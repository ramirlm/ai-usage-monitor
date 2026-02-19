"""Usage monitoring and health status calculation."""

from typing import Dict, Optional
from datetime import datetime
import calendar
from app.database import Database
from app.cost_calculator import CostCalculator


class UsageMonitor:
    """Monitor usage and calculate health status for services."""
    
    def __init__(self, db: Database):
        """Initialize usage monitor.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def get_month_progress(self) -> Dict:
        """Get current progress through the month.
        
        Returns:
            Dict with day info and percentage progress
        """
        now = datetime.now()
        day_of_month = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        progress_percentage = (day_of_month / days_in_month) * 100
        
        return {
            'current_day': day_of_month,
            'total_days': days_in_month,
            'progress_percentage': progress_percentage
        }
    
    def calculate_usage_health(self, service: str, year: int = None, month: int = None) -> Dict:
        """Calculate usage health status for a service.
        
        This determines if the user is in "good shape", "warning", or "danger zone"
        based on how their usage compares to time progression through the month.
        
        Args:
            service: Service name
            year: Optional year (defaults to current)
            month: Optional month (defaults to current)
            
        Returns:
            Dict with health status information
        """
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        
        # Get month progress
        month_info = self.get_month_progress()
        time_progress = month_info['progress_percentage']
        
        # Get subscription info if available
        subscription = self.db.get_subscription(service)
        
        # Get budget info
        budget = self.db.get_budget(service=service)
        
        # Determine if service is subscription-based or pay-as-you-go
        is_subscription = CostCalculator.is_subscription_based(service)
        
        if is_subscription and subscription:
            # For subscription services with usage limits
            return self._calculate_subscription_health(
                service, subscription, month_info, year, month
            )
        elif budget:
            # For pay-as-you-go services with budgets
            return self._calculate_budget_health(
                service, budget, month_info, year, month
            )
        else:
            # No tracking configured
            return {
                'status': 'unknown',
                'status_label': 'Not Configured',
                'usage_percentage': 0,
                'time_percentage': time_progress,
                'message': 'No budget or subscription configured'
            }
    
    def _calculate_subscription_health(self, service: str, subscription: Dict,
                                      month_info: Dict, year: int, month: int) -> Dict:
        """Calculate health for subscription-based services.
        
        Args:
            service: Service name
            subscription: Subscription settings
            month_info: Month progress information
            year: Year
            month: Month
            
        Returns:
            Health status dict
        """
        time_progress = month_info['progress_percentage']
        monthly_limit = subscription.get('monthly_limit')
        
        if monthly_limit is None:
            # Unlimited plan
            usage_count = self.db.get_monthly_usage_count(year, month, service)
            return {
                'status': 'good',
                'status_label': 'Unlimited',
                'usage_percentage': 0,
                'time_percentage': time_progress,
                'usage_count': usage_count,
                'monthly_limit': None,
                'message': f'{usage_count} requests used (unlimited plan)'
            }
        
        # Calculate usage percentage
        usage_count = self.db.get_monthly_usage_count(year, month, service)
        usage_percentage = (usage_count / monthly_limit * 100) if monthly_limit > 0 else 0
        
        # Determine status based on usage vs time
        status = self._determine_status(usage_percentage, time_progress)
        
        return {
            'status': status,
            'status_label': self._get_status_label(status),
            'usage_percentage': usage_percentage,
            'time_percentage': time_progress,
            'usage_count': usage_count,
            'monthly_limit': monthly_limit,
            'message': self._get_health_message(status, usage_count, monthly_limit, time_progress)
        }
    
    def _calculate_budget_health(self, service: str, budget: Dict,
                                 month_info: Dict, year: int, month: int) -> Dict:
        """Calculate health for budget-based services.
        
        Args:
            service: Service name
            budget: Budget settings
            month_info: Month progress information
            year: Year
            month: Month
            
        Returns:
            Health status dict
        """
        time_progress = month_info['progress_percentage']
        monthly_budget = budget['monthly_budget']
        
        # Get current spending
        current_cost = self.db.get_monthly_cost(year, month, service=service)
        usage_percentage = (current_cost / monthly_budget * 100) if monthly_budget > 0 else 0
        
        # Determine status
        status = self._determine_status(usage_percentage, time_progress)
        
        return {
            'status': status,
            'status_label': self._get_status_label(status),
            'usage_percentage': usage_percentage,
            'time_percentage': time_progress,
            'current_cost': current_cost,
            'monthly_budget': monthly_budget,
            'message': self._get_budget_message(status, current_cost, monthly_budget, time_progress)
        }
    
    def _determine_status(self, usage_percentage: float, time_percentage: float) -> str:
        """Determine health status based on usage vs time.
        
        Logic:
        - Good: Usage is up to 10% ahead of time progress (e.g., 60% used at 50% time is still good)
               Being behind schedule is also considered good
        - Warning: Usage is 10-25% ahead of time progress
        - Danger: Usage is more than 25% ahead of time progress
        
        Args:
            usage_percentage: Current usage percentage
            time_percentage: Time progress percentage
            
        Returns:
            Status string: 'good', 'warning', or 'danger'
        """
        difference = usage_percentage - time_percentage
        
        # Being at or behind schedule is always good
        # Being up to 10% ahead is also acceptable
        if difference <= 10:
            return 'good'
        elif difference <= 25:
            return 'warning'
        else:
            return 'danger'
    
    def _get_status_label(self, status: str) -> str:
        """Get display label for status.
        
        Args:
            status: Status string
            
        Returns:
            Display label
        """
        labels = {
            'good': 'Good Shape ✓',
            'warning': 'Warning Zone ⚠️',
            'danger': 'Danger Zone 🚨',
            'unknown': 'Unknown'
        }
        return labels.get(status, 'Unknown')
    
    def _get_health_message(self, status: str, usage_count: int, monthly_limit: int,
                           time_progress: float) -> str:
        """Get health message for subscription services.
        
        Args:
            status: Health status
            usage_count: Current usage count
            monthly_limit: Monthly limit
            time_progress: Time progress percentage
            
        Returns:
            Message string
        """
        remaining = monthly_limit - usage_count
        usage_pct = (usage_count / monthly_limit * 100) if monthly_limit > 0 else 0
        
        if status == 'good':
            return f'{usage_count}/{monthly_limit} requests used ({usage_pct:.1f}%) - on track!'
        elif status == 'warning':
            return f'{usage_count}/{monthly_limit} requests used ({usage_pct:.1f}%) - usage ahead of schedule'
        else:
            return f'{usage_count}/{monthly_limit} requests used ({usage_pct:.1f}%) - usage significantly ahead!'
    
    def _get_budget_message(self, status: str, current_cost: float, monthly_budget: float,
                           time_progress: float) -> str:
        """Get health message for budget-based services.
        
        Args:
            status: Health status
            current_cost: Current spending
            monthly_budget: Monthly budget
            time_progress: Time progress percentage
            
        Returns:
            Message string
        """
        remaining = monthly_budget - current_cost
        usage_pct = (current_cost / monthly_budget * 100) if monthly_budget > 0 else 0
        
        if status == 'good':
            return f'${current_cost:.2f}/${monthly_budget:.2f} spent ({usage_pct:.1f}%) - on track!'
        elif status == 'warning':
            return f'${current_cost:.2f}/${monthly_budget:.2f} spent ({usage_pct:.1f}%) - spending ahead of schedule'
        else:
            return f'${current_cost:.2f}/${monthly_budget:.2f} spent ({usage_pct:.1f}%) - spending significantly ahead!'
    
    def get_all_services_health(self) -> Dict:
        """Get health status for all configured services.
        
        Returns:
            Dict with health info for each service
        """
        now = datetime.now()
        
        # Get all services with budgets or subscriptions
        cursor = self.db.conn.cursor()
        
        # Get services from budget_settings
        cursor.execute('SELECT DISTINCT service FROM budget_settings WHERE service IS NOT NULL')
        budget_services = [row['service'] for row in cursor.fetchall()]
        
        # Get services from subscription_settings
        cursor.execute('SELECT DISTINCT service FROM subscription_settings')
        subscription_services = [row['service'] for row in cursor.fetchall()]
        
        # Combine unique services
        all_services = list(set(budget_services + subscription_services))
        
        # Calculate health for each service
        services_health = {}
        for service in all_services:
            services_health[service] = self.calculate_usage_health(service, now.year, now.month)
        
        return {
            'month_info': self.get_month_progress(),
            'services': services_health
        }
