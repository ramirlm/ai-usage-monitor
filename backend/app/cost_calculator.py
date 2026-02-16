"""Cost calculator for different AI services."""

from typing import Dict, Optional


class CostCalculator:
    """Calculate costs for different AI services based on token usage."""
    
    # Pricing per million tokens (as of Feb 2026)
    PRICING = {
        'anthropic': {
            'claude-sonnet-4': {
                'input': 3.00,
                'output': 15.00
            },
            'claude-opus-4': {
                'input': 15.00,
                'output': 75.00
            },
            'claude-haiku': {
                'input': 0.80,
                'output': 4.00
            }
        },
        'openai': {
            'gpt-4': {
                'input': 30.00,
                'output': 60.00
            },
            'gpt-4-turbo': {
                'input': 10.00,
                'output': 30.00
            },
            'gpt-3.5-turbo': {
                'input': 0.50,
                'output': 1.50
            }
        },
        'synthetic': {
            'default': {
                'input': 1.00,
                'output': 2.00
            }
        },
        'cursor': {
            'default': {
                'input': 0.00,  # Subscription-based, not token-based
                'output': 0.00
            }
        },
        'copilot': {
            'default': {
                'input': 0.00,  # Subscription-based, not token-based
                'output': 0.00
            }
        }
    }
    
    # Subscription limits (monthly) - None means unlimited or not applicable
    # For services with usage limits, this tracks completions/requests rather than tokens
    SUBSCRIPTION_LIMITS = {
        'cursor': {
            'pro': {
                'monthly_cost': 20.00,
                'monthly_requests': 500,  # Premium requests per month
                'description': 'Cursor Pro Plan'
            },
            'business': {
                'monthly_cost': 40.00,
                'monthly_requests': None,  # Unlimited
                'description': 'Cursor Business Plan'
            }
        },
        'copilot': {
            'individual': {
                'monthly_cost': 10.00,
                'monthly_requests': None,  # Unlimited suggestions
                'description': 'GitHub Copilot Individual'
            },
            'business': {
                'monthly_cost': 19.00,
                'monthly_requests': None,  # Unlimited suggestions
                'description': 'GitHub Copilot Business'
            }
        },
        'anthropic': {
            'api': {
                'monthly_cost': None,  # Pay-as-you-go
                'monthly_requests': None,
                'description': 'Claude API (Pay-as-you-go)'
            }
        },
        'openai': {
            'api': {
                'monthly_cost': None,  # Pay-as-you-go
                'monthly_requests': None,
                'description': 'OpenAI API (Pay-as-you-go)'
            }
        },
        'synthetic': {
            'api': {
                'monthly_cost': None,  # Pay-as-you-go
                'monthly_requests': None,
                'description': 'Synthetic API (Pay-as-you-go)'
            }
        }
    }
    
    @classmethod
    def calculate_cost(cls, service: str, model: Optional[str], 
                      input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given usage.
        
        Args:
            service: Service name (anthropic, openai, synthetic)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in dollars
        """
        service = service.lower()
        
        # Get pricing for service and model
        if service not in cls.PRICING:
            # Default pricing if service not found
            return (input_tokens + output_tokens) / 1000000 * 2.0
        
        service_pricing = cls.PRICING[service]
        
        if model and model in service_pricing:
            pricing = service_pricing[model]
        elif 'default' in service_pricing:
            pricing = service_pricing['default']
        else:
            # Use first available model pricing
            pricing = next(iter(service_pricing.values()))
        
        input_cost = (input_tokens / 1000000) * pricing['input']
        output_cost = (output_tokens / 1000000) * pricing['output']
        
        return input_cost + output_cost
    
    @classmethod
    def get_model_pricing(cls, service: str, model: str) -> Optional[Dict[str, float]]:
        """Get pricing info for a specific model.
        
        Args:
            service: Service name
            model: Model name
            
        Returns:
            Dict with input/output pricing or None
        """
        service = service.lower()
        
        if service in cls.PRICING and model in cls.PRICING[service]:
            return cls.PRICING[service][model]
        
        return None
    
    @classmethod
    def get_subscription_info(cls, service: str, plan: str = None) -> Optional[Dict]:
        """Get subscription information for a service.
        
        Args:
            service: Service name
            plan: Optional plan name (e.g., 'pro', 'business')
            
        Returns:
            Dict with subscription info or None
        """
        service = service.lower()
        
        if service not in cls.SUBSCRIPTION_LIMITS:
            return None
        
        service_plans = cls.SUBSCRIPTION_LIMITS[service]
        
        if plan and plan in service_plans:
            return service_plans[plan]
        elif not plan and service_plans:
            # Return first available plan as default
            return next(iter(service_plans.values()))
        
        return None
    
    @classmethod
    def is_subscription_based(cls, service: str) -> bool:
        """Check if a service is subscription-based.
        
        Args:
            service: Service name
            
        Returns:
            True if subscription-based, False otherwise
        """
        service = service.lower()
        if service not in cls.SUBSCRIPTION_LIMITS:
            return False
        
        # Check if service has a fixed monthly cost
        plans = cls.SUBSCRIPTION_LIMITS[service]
        for plan_info in plans.values():
            if plan_info.get('monthly_cost') is not None:
                return True
        
        return False
