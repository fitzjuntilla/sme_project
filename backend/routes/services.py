"""
Service management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector


services_bp = Blueprint('services', __name__)


# ============================================================
# SERVICE LIST
# ============================================================

@services_bp.route("/services")
def services():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get services
        cursor.execute("""
            SELECT
                service_id,
                service_name,
                description,
                service_type,
                price,
                status,
                created_at
            FROM services
            ORDER BY service_id DESC
        """)

        services = cursor.fetchall()


        # Get customers for service sales
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
            "services.html",
            services=services,
            customers=customers,
            full_name=session["full_name"],
            role=session["role"]
        )


    except mysql.connector.Error as error:

        return f"Database Error: {error}"


# ============================================================
# ADD SERVICE
# ============================================================

@services_bp.route("/services/add", methods=["POST"])
def add_service():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    service_name = request.form["service_name"]

    description = request.form.get(
        "description",
        ""
    )

    service_type = request.form["service_type"]

    price = request.form["price"]

    status = request.form["status"]


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("""
            INSERT INTO services
            (
                service_name,
                description,
                service_type,
                price,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            service_name,
            description,
            service_type,
            price,
            status
        ))


        connection.commit()

        cursor.close()
        connection.close()


        return redirect(
            url_for("services.services")
        )


    except mysql.connector.Error as error:

        return f"Database Error: {error}"


# ============================================================
# EDIT SERVICE
# ============================================================

@services_bp.route(
    "/services/edit/<int:service_id>",
    methods=["POST"]
)
def edit_service(service_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    service_name = request.form["service_name"]

    description = request.form.get(
        "description",
        ""
    )

    service_type = request.form["service_type"]

    price = request.form["price"]

    status = request.form["status"]


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("""
            UPDATE services
            SET
                service_name = %s,
                description = %s,
                service_type = %s,
                price = %s,
                status = %s
            WHERE service_id = %s
        """, (
            service_name,
            description,
            service_type,
            price,
            status,
            service_id
        ))


        connection.commit()

        cursor.close()
        connection.close()


        return redirect(
            url_for("services.services")
        )


    except mysql.connector.Error as error:

        return f"Database Error: {error}"


# ============================================================
# DEACTIVATE SERVICE
# ============================================================

@services_bp.route(
    "/services/delete/<int:service_id>",
    methods=["POST"]
)
def delete_service(service_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("""
            UPDATE services
            SET status = 'Unavailable'
            WHERE service_id = %s
        """, (service_id,))


        connection.commit()

        cursor.close()
        connection.close()


        return redirect(
            url_for("services.services")
        )


    except mysql.connector.Error as error:

        return f"Database Error: {error}"


# ============================================================
# RECORD SERVICE SALE
# ============================================================

@services_bp.route(
    "/services/sell",
    methods=["POST"]
)
def sell_service():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    customer_id = request.form.get("customer_id")

    service_id = request.form.get("service_id")

    quantity = request.form.get("quantity")


    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    try:

        customer_id = int(customer_id)

        service_id = int(service_id)

        quantity = int(quantity)


        if quantity <= 0:

            return "Quantity must be greater than zero."


    except (TypeError, ValueError):

        return "Invalid service sale information."


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)


        # ====================================================
        # GET SERVICE
        # ====================================================

        cursor.execute("""
            SELECT
                service_id,
                service_name,
                price,
                status
            FROM services
            WHERE service_id = %s
        """, (service_id,))


        service = cursor.fetchone()


        if not service:

            return "Service not found."


        if service["status"] != "Available":

            return "This service is currently unavailable."


        # ====================================================
        # CHECK CUSTOMER
        # ====================================================

        cursor.execute("""
            SELECT
                customer_id,
                customer_name
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))


        customer = cursor.fetchone()


        if not customer:

            return "Customer not found."


        # ====================================================
        # CALCULATE SERVICE SELLING PRICE
        # ====================================================

        unit_price = float(
            service["price"]
        )


        subtotal = (
            unit_price * quantity
        )


        # ====================================================
        # CALCULATE MATERIAL COST
        # ====================================================

        cursor.execute("""
            SELECT
                sm.inventory_id,
                sm.quantity_required,
                i.item_name,
                i.quantity AS inventory_quantity,
                i.unit_cost
            FROM service_materials sm

            INNER JOIN inventory i
                ON sm.inventory_id = i.inventory_id

            WHERE sm.service_id = %s
        """, (service_id,))


        materials = cursor.fetchall()


        material_cost_per_unit = 0.00


        # Calculate material cost
        for material in materials:

            required_quantity = float(
                material["quantity_required"]
            )

            unit_cost = float(
                material["unit_cost"]
            )


            material_cost_per_unit += (
                required_quantity * unit_cost
            )


        total_material_cost = (
            material_cost_per_unit * quantity
        )


        # ====================================================
        # CHECK INVENTORY
        # ====================================================

        for material in materials:

            required_quantity = float(
                material["quantity_required"]
            )


            required_total = (
                required_quantity * quantity
            )


            available_quantity = float(
                material["inventory_quantity"]
            )


            if available_quantity < required_total:

                return (
                    "Insufficient inventory for "
                    + material["item_name"]
                    + ". Available: "
                    + str(available_quantity)
                    + ", Required: "
                    + str(required_total)
                )


        # ====================================================
        # CREATE TRANSACTION
        # ====================================================

        cursor.execute("""
            INSERT INTO transactions
            (
                customer_id,
                user_id,
                transaction_date,
                subtotal,
                total_amount,
                cash_received,
                change_amount,
                payment_status
            )
            VALUES
            (
                %s,
                %s,
                NOW(),
                %s,
                %s,
                %s,
                %s,
                'Paid'
            )
        """, (
            customer_id,
            session["user_id"],
            subtotal,
            subtotal,
            subtotal,
            0.00
        ))


        transaction_id = cursor.lastrowid


        # ====================================================
        # CREATE TRANSACTION ITEM
        # ====================================================

        cursor.execute("""
            INSERT INTO transaction_items
            (
                transaction_id,
                service_id,
                quantity,
                unit_price,
                subtotal,
                material_cost
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            transaction_id,
            service_id,
            quantity,
            unit_price,
            subtotal,
            total_material_cost
        ))


        # ====================================================
        # DEDUCT INVENTORY
        # ====================================================

        for material in materials:

            required_quantity = float(
                material["quantity_required"]
            )


            required_total = (
                required_quantity * quantity
            )


            cursor.execute("""
                UPDATE inventory

                SET
                    quantity =
                        quantity - %s,

                    status =
                        CASE

                            WHEN quantity - %s <= 0
                                THEN 'Out of Stock'

                            WHEN quantity - %s <= minimum_stock
                                THEN 'Low Stock'

                            ELSE 'Available'

                        END

                WHERE inventory_id = %s
            """, (
                required_total,
                required_total,
                required_total,
                material["inventory_id"]
            ))


            # =================================================
            # INVENTORY TRANSACTION LOG
            # =================================================

            cursor.execute("""
                INSERT INTO inventory_transactions
                (
                    inventory_id,
                    user_id,
                    transaction_type,
                    quantity,
                    transaction_date,
                    remarks
                )
                VALUES
                (
                    %s,
                    %s,
                    'Stock Out',
                    %s,
                    NOW(),
                    %s
                )
            """, (
                material["inventory_id"],
                session["user_id"],
                required_total,
                (
                    "Used for "
                    + service["service_name"]
                    + " - Transaction #"
                    + str(transaction_id)
                )
            ))


        # ====================================================
        # ACTIVITY LOG
        # ====================================================

        cursor.execute("""
            INSERT INTO activity_logs
            (
                user_id,
                action,
                description
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            session["user_id"],
            "Service Sale",
            (
                service["service_name"]
                + " x"
                + str(quantity)
                + " sold to "
                + customer["customer_name"]
                + " - Transaction #"
                + str(transaction_id)
            )
        ))


        # ====================================================
        # COMMIT EVERYTHING
        # ====================================================

        connection.commit()


        cursor.close()

        connection.close()


        return redirect(
            url_for("services.services")
        )


    except mysql.connector.Error as error:


        if connection:

            connection.rollback()


        if cursor:

            cursor.close()


        if connection:

            connection.close()


        return f"Database Error: {error}"
