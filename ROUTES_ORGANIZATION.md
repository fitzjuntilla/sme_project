# Routes Organization Guide

## Overview
The Flask application has been refactored to use **Blueprints**, separating routes by feature/module. This improves code organization, maintainability, and scalability.

## Project Structure

```
backend/
├── app.py                 # Main application entry point (simplified)
├── utils.py              # Utility functions (database, logging)
├── routes/               # All route blueprints
│   ├── __init__.py       # Blueprint registration
│   ├── auth.py          # Login/logout
│   ├── dashboard.py     # Dashboard
│   ├── computers.py     # Computer sessions
│   ├── customers.py     # Customer management
│   ├── transactions.py  # Transaction reports
│   ├── services.py      # Service management
│   ├── inventory.py     # Inventory management
│   ├── reports.py       # Reports and analytics
│   └── staff.py         # Staff management
├── models/              # Database models (ready for expansion)
├── services/            # Business logic (ready for expansion)
├── config/              # Configuration (ready for expansion)
└── __init__.py
```

## Key Features

### 1. **Modular Routes**
Each feature has its own blueprint file:
- **auth.py**: Login and logout functionality
- **dashboard.py**: Dashboard overview
- **computers.py**: Computer session management (start, extend, end, check-expired)
- **customers.py**: Customer CRUD operations
- **transactions.py**: Transaction history and sales summaries
- **services.py**: Service management
- **inventory.py**: Inventory item management
- **reports.py**: Advanced reporting with date filters
- **staff.py**: Staff/user management (owner only)

### 2. **Centralized Utilities**
**utils.py** contains shared functions:
- `get_db_connection()` - Database connection management
- `log_activity()` - Activity logging

### 3. **Blueprint Registration**
**routes/__init__.py** automatically registers all blueprints:
```python
from .auth import auth_bp
from .dashboard import dashboard_bp
# ... imports for all blueprints

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    # ... registers all blueprints
```

### 4. **Simplified Main App**
**app.py** is now clean and focused:
- Minimal configuration
- Blueprint registration
- No route definitions (all moved to blueprint files)

## URL Mapping

| Blueprint | Route | Function |
|-----------|-------|----------|
| auth | `/` | login() |
| auth | `/logout` | logout() |
| dashboard | `/dashboard` | dashboard() |
| computers | `/computers` | computers() |
| computers | `/computers/start` | start_session() |
| computers | `/computers/check-expired` | check_expired_sessions() |
| computers | `/computers/extend/<id>` | extend_session() |
| computers | `/computers/end/<id>` | end_session() |
| customers | `/customers` | customers() |
| customers | `/customers/add` | add_customer() |
| customers | `/customers/edit/<id>` | edit_customer() |
| customers | `/customers/delete/<id>` | delete_customer() |
| transactions | `/transactions` | transactions() |
| services | `/services` | services() |
| services | `/services/add` | add_service() |
| services | `/services/edit/<id>` | edit_service() |
| services | `/services/delete/<id>` | delete_service() |
| inventory | `/inventory` | inventory() |
| inventory | `/inventory/add` | add_inventory() |
| inventory | `/inventory/edit/<id>` | edit_inventory() |
| inventory | `/inventory/delete/<id>` | delete_inventory() |
| reports | `/reports` | reports() |
| staff | `/staff` | staff() |
| staff | `/staff/add` | add_staff() |
| staff | `/staff/deactivate/<id>` | deactivate_staff() |
| staff | `/staff/activate/<id>` | activate_staff() |

## Benefits of This Organization

✅ **Separation of Concerns** - Each feature is isolated  
✅ **Better Maintainability** - Easier to find and modify route logic  
✅ **Scalability** - Easy to add new features as new blueprints  
✅ **Reusability** - Shared utilities in utils.py  
✅ **Testability** - Blueprints can be tested independently  
✅ **Cleaner Code** - Main app.py is now only 20 lines!

## Adding New Features

To add a new feature:

1. Create a new file in `backend/routes/` (e.g., `backend/routes/reports_advanced.py`)
2. Define a Blueprint:
   ```python
   from flask import Blueprint
   reports_advanced_bp = Blueprint('reports_advanced', __name__)
   
   @reports_advanced_bp.route('/reports/advanced')
   def advanced_reports():
       # your code here
       pass
   ```
3. Import in `backend/routes/__init__.py`:
   ```python
   from .reports_advanced import reports_advanced_bp
   ```
4. Register in `register_blueprints()`:
   ```python
   app.register_blueprint(reports_advanced_bp)
   ```

## Migration Notes

All original functionality has been preserved. The refactoring is purely organizational.

- All routes work exactly as before
- No changes to templates or frontend
- Database queries are unchanged
- Error handling remains the same

## Future Improvements

The modular structure enables:
- **Models folder**: Add ORM (SQLAlchemy) for cleaner database interactions
- **Services folder**: Extract business logic into service classes
- **Config folder**: Environment-specific settings and database configs
- **Unit tests**: Test each blueprint independently
- **API versioning**: Easy to create `/api/v1/` routes alongside existing routes
