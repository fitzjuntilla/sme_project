"""
Computer session management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.utils import get_db_connection, log_activity
from datetime import datetime
import mysql.connector
import math

computers_bp = Blueprint('computers', __name__)


@computers_bp.route("/computers")
def computers():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Computer status + active session
        cursor.execute("""
            SELECT
                c.computer_id,
                c.computer_number,
                c.computer_name,
                c.status,
                c.hourly_rate,
                cs.session_id,
                cs.customer_id,
                cs.start_time,
                cs.allocated_minutes,
                cs.status AS session_status,
                CASE
                    WHEN cs.status = 'Active'
                    THEN DATE_ADD(
                        cs.start_time,
                        INTERVAL cs.allocated_minutes MINUTE
                    )
                    ELSE NULL
                END AS occupied_until,
                cu.customer_name
            FROM computers c
            LEFT JOIN computer_sessions cs
                ON c.computer_id = cs.computer_id
                AND cs.status = 'Active'
            LEFT JOIN customers cu
                ON cs.customer_id = cu.customer_id
            ORDER BY c.computer_id
        """)
        computers = cursor.fetchall()

        # Customers
        cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                contact_number
            FROM customers
            ORDER BY customer_name ASC
        """)
        customers = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "computers.html",
            computers=computers,
            customers=customers,
            full_name=session["full_name"],
            role=session["role"]
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@computers_bp.route("/computers/start", methods=["POST"])
def start_session():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    computer_id = request.form["computer_id"]
    customer_id = request.form["customer_id"]

    try:
        allocated_minutes = int(request.form["allocated_minutes"])
    except (ValueError, TypeError):
        return "Invalid session duration."

    # Check valid duration
    allowed_durations = [4, 10, 15, 30, 60, 120]
    if allocated_minutes not in allowed_durations:
        return "Invalid session duration."

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check computer status
        cursor.execute("""
            SELECT status
            FROM computers
            WHERE computer_id = %s
        """, (computer_id,))

        computer = cursor.fetchone()

        if not computer:
            cursor.close()
            connection.close()
            return "Computer not found."

        if computer[0] != "Available":
            cursor.close()
            connection.close()
            return "Computer is not available."

        # Create computer session
        cursor.execute("""
            INSERT INTO computer_sessions
            (computer_id, customer_id, start_time, allocated_minutes, status)
            VALUES (%s, %s, NOW(), %s, 'Active')
        """, (computer_id, customer_id, allocated_minutes))

        # Occupy computer
        cursor.execute("""
            UPDATE computers
            SET status = 'Occupied'
            WHERE computer_id = %s
        """, (computer_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("computers.computers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@computers_bp.route("/computers/check-expired")
def check_expired_sessions():
    if "user_id" not in session:
        return jsonify({"success": False})

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Find expired active sessions
        cursor.execute("""
            SELECT
                cs.session_id,
                cs.computer_id,
                cs.start_time,
                cs.allocated_minutes,
                c.hourly_rate
            FROM computer_sessions cs
            JOIN computers c
                ON cs.computer_id = c.computer_id
            WHERE cs.status = 'Active'
            AND NOW() >= DATE_ADD(
                cs.start_time,
                INTERVAL cs.allocated_minutes MINUTE
            )
        """)

        expired_sessions = cursor.fetchall()

        for current_session in expired_sessions:
            end_time = datetime.now()

            duration_seconds = (
                end_time - current_session["start_time"]
            ).total_seconds()

            duration_minutes = max(
                1,
                math.ceil(duration_seconds / 60)
            )

            # Charge based on allocated time
            total_amount = (
                current_session["allocated_minutes"] / 60
            ) * float(current_session["hourly_rate"])

            total_amount = round(total_amount, 2)

            # Complete session
            cursor.execute("""
                UPDATE computer_sessions
                SET
                    end_time = %s,
                    duration_minutes = %s,
                    total_amount = %s,
                    status = 'Completed'
                WHERE session_id = %s
            """, (
                end_time,
                duration_minutes,
                total_amount,
                current_session["session_id"]
            ))

            # Make computer available
            cursor.execute("""
                UPDATE computers
                SET status = 'Available'
                WHERE computer_id = %s
            """, (current_session["computer_id"],))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "expired": len(expired_sessions)
        })

    except mysql.connector.Error as error:
        return jsonify({
            "success": False,
            "error": str(error)
        })


@computers_bp.route("/computers/extend/<int:session_id>", methods=["POST"])
def extend_session(session_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        extra_minutes = int(request.form["extra_minutes"])

        if extra_minutes <= 0:
            cursor.close()
            connection.close()
            return "Invalid extension time."

        # Get current active session
        cursor.execute("""
            SELECT
                session_id,
                allocated_minutes
            FROM computer_sessions
            WHERE session_id = %s
            AND status = 'Active'
        """, (session_id,))

        session_data = cursor.fetchone()

        if not session_data:
            cursor.close()
            connection.close()
            return "Active session not found."

        # Add extra time
        new_allocated_minutes = (
            session_data["allocated_minutes"] + extra_minutes
        )

        cursor.execute("""
            UPDATE computer_sessions
            SET allocated_minutes = %s
            WHERE session_id = %s
            AND status = 'Active'
        """, (new_allocated_minutes, session_id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("computers.computers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
    except ValueError:
        return "Invalid extension time."


@computers_bp.route("/computers/end/<int:session_id>", methods=["POST"])
def end_session(session_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get active session
        cursor.execute("""
            SELECT
                cs.session_id,
                cs.computer_id,
                cs.start_time,
                c.hourly_rate
            FROM computer_sessions cs
            JOIN computers c
                ON cs.computer_id = c.computer_id
            WHERE cs.session_id = %s
            AND cs.status = 'Active'
        """, (session_id,))

        session_data = cursor.fetchone()

        if not session_data:
            cursor.close()
            connection.close()
            return "Active session not found."

        start_time = session_data["start_time"]
        end_time = datetime.now()

        duration_seconds = (end_time - start_time).total_seconds()
        duration_minutes = max(1, math.ceil(duration_seconds / 60))

        # Charge by the hour
        total_amount = (
            duration_minutes / 60
        ) * float(session_data["hourly_rate"])

        total_amount = round(total_amount, 2)

        # Update session
        cursor.execute("""
            UPDATE computer_sessions
            SET
                end_time = %s,
                duration_minutes = %s,
                total_amount = %s,
                status = 'Completed'
            WHERE session_id = %s
        """, (
            end_time,
            duration_minutes,
            total_amount,
            session_id
        ))

        # Make computer available again
        cursor.execute("""
            UPDATE computers
            SET status = 'Available'
            WHERE computer_id = %s
        """, (session_data["computer_id"],))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("computers.computers"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
