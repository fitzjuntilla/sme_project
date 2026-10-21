"""
Routes package - Register all blueprints
"""
from .auth import auth_bp
from .dashboard import dashboard_bp
from .computers import computers_bp
from .customers import customers_bp
from .transactions import transactions_bp
from .services import services_bp
from .inventory import inventory_bp
from .reports import reports_bp
from .staff import staff_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(computers_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(staff_bp)
