"""
Staff management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection, log_activity
import mysql.connector

staff_bp = Blueprint('staff', __name__)


@staff_bp.route("/staff")
def staff():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # OWNER ONLY
    if session.get("role") != "Owner":
        return redirect(url_for("dashboard.dashboard"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                user_id,
                username,
                full_name,
                role,
                status,
                created_at
            FROM users
            ORDER BY user_id DESC
        """)

        staff_members = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(
            "staff.html",
            staff_members=staff_members,
            full_name=session["full_name"],
            role=session["role"]
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@staff_bp.route("/staff/add", methods=["POST"])
def add_staff():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # OWNER ONLY
    if session.get("role") != "Owner":
        return redirect(url_for("dashboard.dashboard"))

    full_name = request.form["full_name"].strip()
    username = request.form["username"].strip()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Check password confirmation
    if password != confirm_password:
        return "Passwords do not match."

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if username already exists
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE username = %s
        """, (username,))

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            connection.close()
            return "Username already exists."

        # Create attendant account
        cursor.execute("""
            INSERT INTO users
            (username, password, full_name, role)
            VALUES (%s, %s, %s, 'Attendant')
        """, (username, password, full_name))

        connection.commit()

        log_activity(
            session["user_id"],
            "ADD_ATTENDANT",
            f"Added attendant: {full_name}"
        )

        cursor.close()
        connection.close()

        return redirect(url_for("staff.staff"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@staff_bp.route("/staff/deactivate/<int:user_id>", methods=["POST"])
def deactivate_staff(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # OWNER ONLY
    if session.get("role") != "Owner":
        return redirect(url_for("dashboard.dashboard"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get staff account
        cursor.execute("""
            SELECT
                user_id,
                full_name,
                role,
                status
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            cursor.close()
            connection.close()
            return "Staff account not found."

        # Protect owner account
        if user["role"] == "Owner":
            cursor.close()
            connection.close()
            return "Owner account cannot be deactivated."

        # Deactivate attendant
        cursor.execute("""
            UPDATE users
            SET status = 'Inactive'
            WHERE user_id = %s
            AND role = 'Attendant'
        """, (user_id,))

        connection.commit()

        # Log activity
        log_activity(
            session["user_id"],
            "DEACTIVATE_STAFF",
            f"Deactivated attendant: {user['full_name']}"
        )

        cursor.close()
        connection.close()

        return redirect(url_for("staff.staff"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@staff_bp.route("/staff/activate/<int:user_id>", methods=["POST"])
def activate_staff(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # OWNER ONLY
    if session.get("role") != "Owner":
        return redirect(url_for("dashboard.dashboard"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get staff account
        cursor.execute("""
            SELECT
                user_id,
                full_name,
                role,
                status
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            cursor.close()
            connection.close()
            return "Staff account not found."

        # Only attendants can be activated
        if user["role"] != "Attendant":
            cursor.close()
            connection.close()
            return "Only attendant accounts can be activated."

        # Activate attendant
        cursor.execute("""
            UPDATE users
            SET status = 'Active'
            WHERE user_id = %s
            AND role = 'Attendant'
        """, (user_id,))

        connection.commit()

        # Log activity
        log_activity(
            session["user_id"],
            "ACTIVATE_STAFF",
            f"Activated attendant: {user['full_name']}"
        )

        cursor.close()
        connection.close()

        return redirect(url_for("staff.staff"))

    except mysql.connector.Error as error:
        return f"Database Error: {error}"
