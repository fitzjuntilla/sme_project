"""
Dashboard routes
"""
from flask import Blueprint, render_template, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Total computers
        cursor.execute("""
            SELECT COUNT(*) AS total_computers
            FROM computers
        """)
        total_computers = cursor.fetchone()["total_computers"]

        # Available computers
        cursor.execute("""
            SELECT COUNT(*) AS available_computers
            FROM computers
            WHERE status = 'Available'
        """)
        available_computers = cursor.fetchone()["available_computers"]

        # Occupied computers
        cursor.execute("""
            SELECT COUNT(*) AS occupied_computers
            FROM computers
            WHERE status = 'Occupied'
        """)
        occupied_computers = cursor.fetchone()["occupied_computers"]

        # Active sessions
        cursor.execute("""
            SELECT COUNT(*) AS active_sessions
            FROM computer_sessions
            WHERE status = 'Active'
        """)
        active_sessions = cursor.fetchone()["active_sessions"]

        # Today's sales
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS today_sales
            FROM computer_sessions
            WHERE status = 'Completed'
            AND DATE(end_time) = CURDATE()
        """)
        today_sales = cursor.fetchone()["today_sales"]

        # Low stock items
        cursor.execute("""
            SELECT
                inventory_id,
                item_name,
                quantity,
                unit,
                minimum_stock,
                status
            FROM inventory
            WHERE status IN ('Low Stock', 'Out of Stock')
            ORDER BY
                CASE
                    WHEN status = 'Out of Stock' THEN 1
                    WHEN status = 'Low Stock' THEN 2
                    ELSE 3
                END,
                quantity ASC
        """)
        low_stock_items = cursor.fetchall()

        # Computer status
        cursor.execute("""
            SELECT
                c.computer_id,
                c.computer_number,
                c.computer_name,
                c.status,
                CASE
                    WHEN c.status = 'Occupied'
                         AND cs.status = 'Active'
                    THEN DATE_ADD(
                        cs.start_time,
                        INTERVAL cs.allocated_minutes MINUTE
                    )
                    ELSE NULL
                END AS occupied_until
            FROM computers c
            LEFT JOIN computer_sessions cs
                ON c.computer_id = cs.computer_id
                AND cs.status = 'Active'
            ORDER BY c.computer_id
        """)
        computers = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "dashboard.html",
            username=session["username"],
            full_name=session["full_name"],
            role=session["role"],
            total_computers=total_computers,
            available_computers=available_computers,
            occupied_computers=occupied_computers,
            active_sessions=active_sessions,
            today_sales=today_sales,
            low_stock_items=low_stock_items,
            computers=computers
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
