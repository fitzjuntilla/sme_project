"""
Transaction routes
"""
from flask import Blueprint, render_template, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get completed transactions
        cursor.execute("""
            SELECT
                cs.session_id,
                cs.start_time,
                cs.end_time,
                cs.allocated_minutes,
                cs.duration_minutes,
                cs.total_amount,
                cs.status,
                c.computer_number,
                c.computer_name,
                cu.customer_name
            FROM computer_sessions cs
            LEFT JOIN computers c
                ON cs.computer_id = c.computer_id
            LEFT JOIN customers cu
                ON cs.customer_id = cu.customer_id
            WHERE cs.status = 'Completed'
            ORDER BY cs.end_time DESC
        """)

        transactions = cursor.fetchall()

        # Sales summary
        cursor.execute("""
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_sales,
                COUNT(*) AS total_transactions,
                COALESCE(AVG(total_amount), 0) AS average_sale
            FROM computer_sessions
            WHERE status = 'Completed'
            AND DATE(end_time) = CURDATE()
        """)

        sales_summary = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template(
            "transactions.html",
            transactions=transactions,
            sales_summary=sales_summary,
            full_name=session["full_name"],
            role=session["role"]
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
