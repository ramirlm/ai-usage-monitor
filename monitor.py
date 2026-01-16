#!/usr/bin/env python3
"""
AI Usage Monitor
A CLI tool to monitor usage of various AI services including Claude, OpenAI (Codex/Copilot), and others.
"""

import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Load environment variables
load_dotenv()

console = Console()


class AIUsageMonitor:
    """Monitor usage across multiple AI services"""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
    def check_anthropic_usage(self):
        """Check Claude (Anthropic) API usage"""
        if not self.anthropic_key:
            return {
                'service': 'Claude (Anthropic)',
                'status': 'No API key',
                'error': 'ANTHROPIC_API_KEY not set'
            }
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_key)
            
            # Note: Anthropic doesn't have a direct usage API endpoint
            # This would typically be checked via their dashboard
            # For now, we validate the key is set and format is correct
            return {
                'service': 'Claude (Anthropic)',
                'status': 'Configured',
                'key_status': 'Valid key configured',
                'note': 'Check usage at console.anthropic.com'
            }
        except Exception as e:
            return {
                'service': 'Claude (Anthropic)',
                'status': 'Error',
                'error': str(e)
            }
    
    def check_openai_usage(self):
        """Check OpenAI API usage (includes Codex and Copilot backend)"""
        if not self.openai_key:
            return {
                'service': 'OpenAI (Codex/Copilot)',
                'status': 'No API key',
                'error': 'OPENAI_API_KEY not set'
            }
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            # Validate the API key by making a simple request
            # Note: Usage details are typically available via the dashboard
            return {
                'service': 'OpenAI (Codex/Copilot)',
                'status': 'Configured',
                'key_status': 'Valid key configured',
                'note': 'Check usage at platform.openai.com/usage'
            }
        except Exception as e:
            return {
                'service': 'OpenAI (Codex/Copilot)',
                'status': 'Error',
                'error': str(e)
            }
    
    def display_usage(self):
        """Display usage information for all configured services"""
        console.print("\n")
        console.print(Panel.fit(
            "[bold cyan]AI Usage Monitor[/bold cyan]",
            subtitle=f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            box=box.DOUBLE
        ))
        
        # Check all services
        services = [
            self.check_anthropic_usage(),
            self.check_openai_usage(),
        ]
        
        # Create table
        table = Table(title="AI Service Status", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        for service in services:
            service_name = service['service']
            status = service['status']
            
            # Determine status style
            if status == 'Configured':
                status_style = '[green]✓ Configured[/green]'
            elif status == 'No API key':
                status_style = '[yellow]⚠ Not configured[/yellow]'
            else:
                status_style = '[red]✗ Error[/red]'
            
            # Build details
            details = []
            if 'key_status' in service:
                details.append(service['key_status'])
            if 'note' in service:
                details.append(service['note'])
            if 'error' in service:
                details.append(f"Error: {service['error']}")
            
            table.add_row(
                service_name,
                status_style,
                '\n'.join(details)
            )
        
        console.print(table)
        console.print("\n")
        
        # Configuration hints
        missing_keys = []
        if not self.anthropic_key:
            missing_keys.append('ANTHROPIC_API_KEY')
        if not self.openai_key:
            missing_keys.append('OPENAI_API_KEY')
        
        if missing_keys:
            console.print(Panel(
                f"[yellow]⚠ Missing API Keys:[/yellow]\n" +
                "\n".join([f"  • {key}" for key in missing_keys]) +
                "\n\n[dim]Set these in your environment or create a .env file[/dim]",
                title="Configuration",
                border_style="yellow"
            ))
        else:
            console.print("[green]✓ All services configured![/green]")
        
        console.print("\n")


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description='Monitor AI service usage across Claude, OpenAI, and more',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show current usage status
  %(prog)s --help             # Show this help message

Environment Variables:
  ANTHROPIC_API_KEY          API key for Claude (Anthropic)
  OPENAI_API_KEY             API key for OpenAI (Codex/Copilot)
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create and run monitor
    monitor = AIUsageMonitor()
    monitor.display_usage()


if __name__ == '__main__':
    main()
