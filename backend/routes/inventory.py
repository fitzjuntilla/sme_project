"""
Inventory management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route("/inventory")
def inventory():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                inventory_id,
                item_name,
                description,
                quantity,
                unit,
                minimum_stock,
                status,
                created_at
            FROM inventory
            ORDER BY inventory_id DESC
        """)

        inventory_items = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(
            "inventory.html",
            inventory_items=inventory_items,
            full_name=session["full_name"],
            role=session["role"]
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@inventory_bp.route("/inventory/add", methods=["POST"])
def add_inventory():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    item_name = request.form["item_name"]
    description = request.form.get("description", "")
    quantity = request.form["quantity"]
    unit = request.form["unit"]
    minimum_stock = request.form["minimum_stock"]
    status = request.form["status"]

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO inventory
            (item_name, description, quantity, unit, minimum_stock, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (item_name, description, quantity, unit, minimum_stock, status))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("inventory.inventory"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@inventory_bp.route("/inventory/edit/<int:inventory_id>", methods=["POST"])
def edit_inventory(inventory_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    item_name = request.form["item_name"]
    description = request.form.get("description", "")
    quantity = request.form["quantity"]
    unit = request.form["unit"]
    minimum_stock = request.form["minimum_stock"]
    status = request.form["status"]

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE inventory
            SET
                item_name = %s,
                description = %s,
                quantity = %s,
                unit = %s,
                minimum_stock = %s,
                status = %s
            WHERE inventory_id = %s
        """, (item_name, description, quantity, unit, minimum_stock, status, inventory_id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("inventory.inventory"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@inventory_bp.route("/inventory/delete/<int:inventory_id>", methods=["POST"])
def delete_inventory(inventory_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE inventory
            SET
                quantity = 0,
                status = 'Out of Stock'
            WHERE inventory_id = %s
        """, (inventory_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("inventory.inventory"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
