#!/usr/bin/env python3
"""Flask API server for AI Usage Monitor dashboard."""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import calendar
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database
from app.cost_calculator import CostCalculator
from app.alert_manager import AlertManager

app = Flask(__name__, static_folder='../../frontend/public')
CORS(app)  # Enable CORS for frontend

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai-usage.db')

def get_db():
    """Get database connection."""
    db = Database(DB_PATH)
    db.connect()
    return db


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard overview data."""
    try:
        db = get_db()
        now = datetime.now()
        
        # Get current month cost
        monthly_cost = db.get_monthly_cost(now.year, now.month)
        
        # Get service breakdown
        service_breakdown = db.get_service_breakdown(now.year, now.month)
        
        # Get budget info
        budget = db.get_budget()
        budget_amount = budget['monthly_budget'] if budget else 300.0
        budget_percentage = (monthly_cost / budget_amount * 100) if budget_amount > 0 else 0
        
        # Calculate projection (simple linear projection based on days elapsed)
        day_of_month = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        projected_cost = (monthly_cost / day_of_month) * days_in_month if day_of_month > 0 else 0
        
        # Get recent alerts
        alerts = db.get_recent_alerts(limit=5, unacknowledged_only=True)
        
        db.close()
        
        return jsonify({
            'monthly_cost': round(monthly_cost, 2),
            'budget': round(budget_amount, 2),
            'budget_used': round(budget_percentage, 1),
            'projected_cost': round(projected_cost, 2),
            'over_budget': projected_cost > budget_amount,
            'service_breakdown': service_breakdown,
            'alerts': alerts,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/costs/daily', methods=['GET'])
def get_daily_costs():
    """Get daily cost data."""
    try:
        days = int(request.args.get('days', 30))
        db = get_db()
        
        data = db.get_daily_costs(days=days)
        db.close()
        
        return jsonify({
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/costs/service/<service>', methods=['GET'])
def get_service_costs(service):
    """Get costs for a specific service."""
    try:
        db = get_db()
        now = datetime.now()
        
        cost = db.get_monthly_cost(now.year, now.month, service=service)
        db.close()
        
        return jsonify({
            'service': service,
            'monthly_cost': round(cost, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/budget', methods=['GET'])
def get_budget():
    """Get budget settings."""
    try:
        service = request.args.get('service')
        db = get_db()
        
        budget = db.get_budget(service=service)
        db.close()
        
        if budget:
            return jsonify(budget)
        else:
            return jsonify({'message': 'No budget set'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/budget', methods=['POST'])
def set_budget():
    """Set budget settings."""
    try:
        data = request.json
        monthly_budget = float(data.get('monthly_budget'))
        service = data.get('service')
        alert_threshold = float(data.get('alert_threshold', 0.8))
        
        db = get_db()
        db.set_budget(monthly_budget, service=service, alert_threshold=alert_threshold)
        db.close()
        
        return jsonify({'message': 'Budget set successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts."""
    try:
        limit = int(request.args.get('limit', 10))
        unacknowledged = request.args.get('unacknowledged', 'false').lower() == 'true'
        
        db = get_db()
        alerts = db.get_recent_alerts(limit=limit, unacknowledged_only=unacknowledged)
        db.close()
        
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    try:
        db = get_db()
        db.acknowledge_alert(alert_id)
        db.close()
        
        return jsonify({'message': 'Alert acknowledged'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/usage/add', methods=['POST'])
def add_usage():
    """Add usage data (for testing/manual entry)."""
    try:
        data = request.json
        service = data.get('service')
        model = data.get('model')
        input_tokens = int(data.get('input_tokens', 0))
        output_tokens = int(data.get('output_tokens', 0))
        cost = float(data.get('cost', 0))
        
        db = get_db()
        snapshot_id = db.add_usage_snapshot(service, model, input_tokens, output_tokens, cost)
        
        # Update daily summary
        today = datetime.now().strftime('%Y-%m-%d')
        db.update_daily_summary(today, service, model, input_tokens, output_tokens, cost)
        
        db.close()
        
        return jsonify({'message': 'Usage added', 'id': snapshot_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React app."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    # Initialize database
    db = Database(DB_PATH)
    db.connect()
    db.init_schema()
    db.close()
    print(f"Database initialized at: {DB_PATH}")
    
    # Start server
    print("Starting Flask server on http://localhost:3000")
    # Note: debug=False for security. Set DEBUG=1 environment variable for development
    debug_mode = os.environ.get('DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=3000, debug=debug_mode)
