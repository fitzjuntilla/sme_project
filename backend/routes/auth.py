"""
Authentication routes - Login and Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection, log_activity
import mysql.connector

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM users
                WHERE username = %s
                AND password = %s
            """, (username, password))

            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                # Check account status
                if user["status"] == "Inactive":
                    error = "This account has been deactivated."
                    return render_template("login.html", error=error)

                # Create login session
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["full_name"] = user["full_name"]
                session["role"] = user["role"]

                # Log activity
                log_activity(
                    user["user_id"],
                    "LOGIN",
                    f"{user['full_name']} logged into the system."
                )

                return redirect(url_for("dashboard.dashboard"))

            error = "Invalid username or password."

        except mysql.connector.Error as error:
            return f"Database Error: {error}"

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    if "user_id" in session:
        user_id = session["user_id"]
        full_name = session["full_name"]

        # Record logout activity
        log_activity(
            user_id,
            "LOGOUT",
            f"{full_name} logged out of the system."
        )

    # Clear login session
    session.clear()
    return redirect(url_for("auth.login"))
