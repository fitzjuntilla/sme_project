"""
Customer management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector

customers_bp = Blueprint('customers', __name__)


@customers_bp.route("/customers")
def customers():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                contact_number,
                created_at
            FROM customers
            ORDER BY customer_id DESC
        """)

        customers = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(
            "customers.html",
            customers=customers,
            full_name=session["full_name"],
            role=session["role"]
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@customers_bp.route("/customers/add", methods=["POST"])
def add_customer():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    customer_name = request.form["customer_name"].strip()
    contact_number = request.form["contact_number"].strip()

    if not customer_name or not contact_number:
        return redirect(url_for("customers.customers"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO customers
            (customer_name, contact_number)
            VALUES (%s, %s)
        """, (customer_name, contact_number))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("customers.customers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@customers_bp.route("/customers/edit/<int:customer_id>", methods=["POST"])
def edit_customer(customer_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    customer_name = request.form["customer_name"].strip()
    contact_number = request.form["contact_number"].strip()

    if not customer_name or not contact_number:
        return redirect(url_for("customers.customers"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE customers
            SET
                customer_name = %s,
                contact_number = %s
            WHERE customer_id = %s
        """, (customer_name, contact_number, customer_id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("customers.customers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@customers_bp.route("/customers/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if customer has existing computer sessions
        cursor.execute("""
            SELECT COUNT(*) AS session_count
            FROM computer_sessions
            WHERE customer_id = %s
        """, (customer_id,))

        result = cursor.fetchone()

        if result["session_count"] > 0:
            cursor.close()
            connection.close()
            return redirect(url_for("customers.customers"))

        # Delete customer
        cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("customers.customers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
