#!/usr/bin/env python3
"""Fix url_for calls in HTML templates to use blueprint-qualified endpoint names"""

import os

# Mapping of old endpoint names to new blueprint-qualified names
replacements = {
    "url_for('dashboard')": "url_for('dashboard.dashboard')",
    "url_for('computers')": "url_for('computers.computers')",
    "url_for('customers')": "url_for('customers.customers')",
    "url_for('services')": "url_for('services.services')",
    "url_for('inventory')": "url_for('inventory.inventory')",
    "url_for('transactions')": "url_for('transactions.transactions')",
    "url_for('reports')": "url_for('reports.reports')",
    "url_for('staff')": "url_for('staff.staff')",
    "url_for('logout')": "url_for('auth.logout')",
    "url_for('start_session')": "url_for('computers.start_session')",
    "url_for('add_customer')": "url_for('customers.add_customer')",
    "url_for('edit_customer')": "url_for('customers.edit_customer')",
    "url_for('delete_customer')": "url_for('customers.delete_customer')",
    "url_for('add_inventory')": "url_for('inventory.add_inventory')",
    "url_for('edit_inventory')": "url_for('inventory.edit_inventory')",
    "url_for('delete_inventory')": "url_for('inventory.delete_inventory')",
    "url_for('add_service')": "url_for('services.add_service')",
    "url_for('edit_service')": "url_for('services.edit_service')",
    "url_for('delete_service')": "url_for('services.delete_service')",
    "url_for('extend_session')": "url_for('computers.extend_session')",
    "url_for('end_session')": "url_for('computers.end_session')",
    "url_for('check_expired_sessions')": "url_for('computers.check_expired_sessions')",
    "url_for('add_staff')": "url_for('staff.add_staff')",
    "url_for('deactivate_staff')": "url_for('staff.deactivate_staff')",
    "url_for('activate_staff')": "url_for('staff.activate_staff')",
}

# Get current directory
template_dir = r'F:\sme project\mila_cafe\frontend'

print(f"Processing templates in: {template_dir}")

for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ Updated {filename}')
        else:
            print(f'  No changes needed for {filename}')

print('Done!')
