"""
Reports routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.utils import get_db_connection
import mysql.connector


reports_bp = Blueprint('reports', __name__)


@reports_bp.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        # =====================================================
        # DATE FILTER
        # =====================================================

        date_filter = request.args.get("range", "today")

        start_date = None
        end_date = None

        report_title = "Today's Report"


        if date_filter == "today":

            report_title = "Today's Report"

            start_date = "CURDATE()"

            end_date = """
                DATE_ADD(CURDATE(), INTERVAL 1 DAY)
            """


        elif date_filter == "yesterday":

            report_title = "Yesterday's Report"

            start_date = """
                DATE_SUB(CURDATE(), INTERVAL 1 DAY)
            """

            end_date = "CURDATE()"


        elif date_filter == "week":

            report_title = "This Week"

            start_date = """
                DATE_SUB(
                    CURDATE(),
                    INTERVAL WEEKDAY(CURDATE()) DAY
                )
            """

            end_date = """
                DATE_ADD(
                    DATE_SUB(
                        CURDATE(),
                        INTERVAL WEEKDAY(CURDATE()) DAY
                    ),
                    INTERVAL 7 DAY
                )
            """


        elif date_filter == "month":

            report_title = "This Month"

            start_date = """
                DATE_FORMAT(
                    CURDATE(),
                    '%Y-%m-01'
                )
            """

            end_date = """
                DATE_ADD(
                    DATE_FORMAT(
                        CURDATE(),
                        '%Y-%m-01'
                    ),
                    INTERVAL 1 MONTH
                )
            """


        elif date_filter == "custom":

            custom_date = request.args.get("date", "")

            if custom_date:

                report_title = "Custom Date Report"

                start_date = f"'{custom_date}'"

                end_date = f"""
                    DATE_ADD(
                        '{custom_date}',
                        INTERVAL 1 DAY
                    )
                """

            else:

                date_filter = "today"

                report_title = "Today's Report"

                start_date = "CURDATE()"

                end_date = """
                    DATE_ADD(
                        CURDATE(),
                        INTERVAL 1 DAY
                    )
                """


        else:

            date_filter = "today"

            report_title = "Today's Report"

            start_date = "CURDATE()"

            end_date = """
                DATE_ADD(
                    CURDATE(),
                    INTERVAL 1 DAY
                )
            """


        # =====================================================
        # TOTAL SALES
        # =====================================================

        cursor.execute(f"""
            SELECT
                COALESCE(
                    SUM(total_amount),
                    0
                ) AS total_sales

            FROM transactions

            WHERE transaction_date >= {start_date}

            AND transaction_date < {end_date}

            AND payment_status = 'Paid'
        """)

        total_sales = cursor.fetchone()["total_sales"]


        # =====================================================
        # TRANSACTION COUNT
        # =====================================================

        cursor.execute(f"""
            SELECT
                COUNT(*) AS transaction_count

            FROM transactions

            WHERE transaction_date >= {start_date}

            AND transaction_date < {end_date}

            AND payment_status = 'Paid'
        """)

        transaction_count = cursor.fetchone()["transaction_count"]


        # =====================================================
        # AVERAGE SALE
        # =====================================================

        cursor.execute(f"""
            SELECT
                COALESCE(
                    AVG(total_amount),
                    0
                ) AS average_sale

            FROM transactions

            WHERE transaction_date >= {start_date}

            AND transaction_date < {end_date}

            AND payment_status = 'Paid'
        """)

        average_sale = cursor.fetchone()["average_sale"]


        # =====================================================
        # COMPUTER REVENUE
        # =====================================================

        cursor.execute(f"""
            SELECT
                COALESCE(
                    SUM(cs.total_amount),
                    0
                ) AS computer_revenue

            FROM computer_sessions cs

            INNER JOIN transactions t
                ON t.session_id = cs.session_id

            WHERE cs.status = 'Completed'

            AND t.payment_status = 'Paid'

            AND cs.end_time >= {start_date}

            AND cs.end_time < {end_date}
        """)

        computer_revenue = cursor.fetchone()["computer_revenue"]


        # =====================================================
        # COMPUTER OPERATING COST
        # =====================================================
        #
        # Cost is based on:
        #
        # actual duration in hours
        # × computer operating cost per hour
        #
        # Example:
        #
        # 2 hours × ₱5 operating cost
        # = ₱10 cost
        #
        # =====================================================

        cursor.execute(f"""
            SELECT
                COALESCE(
                    SUM(
                        (
                            cs.duration_minutes / 60
                        )
                        * c.operating_cost
                    ),
                    0
                ) AS computer_operating_cost

            FROM computer_sessions cs

            INNER JOIN computers c
                ON cs.computer_id = c.computer_id

            INNER JOIN transactions t
                ON t.session_id = cs.session_id

            WHERE cs.status = 'Completed'

            AND t.payment_status = 'Paid'

            AND cs.end_time >= {start_date}

            AND cs.end_time < {end_date}
        """)

        computer_operating_cost = cursor.fetchone()[
            "computer_operating_cost"
        ]


        # =====================================================
        # SERVICE SALES
        # =====================================================

        cursor.execute(f"""
            SELECT

                s.service_id,

                s.service_name,

                s.service_type,

                SUM(ti.quantity) AS total_quantity,

                SUM(ti.subtotal) AS total_sales,

                SUM(
                    ti.material_cost
                ) AS total_material_cost

            FROM transaction_items ti

            INNER JOIN services s
                ON ti.service_id = s.service_id

            INNER JOIN transactions t
                ON ti.transaction_id = t.transaction_id

            WHERE t.transaction_date >= {start_date}

            AND t.transaction_date < {end_date}

            AND t.payment_status = 'Paid'

            GROUP BY
                s.service_id,
                s.service_name,
                s.service_type

            ORDER BY total_sales DESC
        """)

        service_sales = cursor.fetchall()


        # =====================================================
        # TOTAL SERVICE REVENUE
        # =====================================================

        cursor.execute(f"""
            SELECT

                COALESCE(
                    SUM(ti.subtotal),
                    0
                ) AS service_revenue

            FROM transaction_items ti

            INNER JOIN transactions t
                ON ti.transaction_id = t.transaction_id

            WHERE t.transaction_date >= {start_date}

            AND t.transaction_date < {end_date}

            AND t.payment_status = 'Paid'
        """)

        service_revenue = cursor.fetchone()["service_revenue"]


        # =====================================================
        # TOTAL SERVICE MATERIAL COST
        # =====================================================

        cursor.execute(f"""
            SELECT

                COALESCE(
                    SUM(ti.material_cost),
                    0
                ) AS service_material_cost

            FROM transaction_items ti

            INNER JOIN transactions t
                ON ti.transaction_id = t.transaction_id

            WHERE t.transaction_date >= {start_date}

            AND t.transaction_date < {end_date}

            AND t.payment_status = 'Paid'
        """)

        service_material_cost = cursor.fetchone()[
            "service_material_cost"
        ]


        # =====================================================
        # TOTAL EXPENSES
        # =====================================================

        total_expenses = (
            float(computer_operating_cost or 0)
            +
            float(service_material_cost or 0)
        )


        # =====================================================
        # NET PROFIT
        # =====================================================

        net_profit = (
            float(total_sales or 0)
            -
            total_expenses
        )


        # =====================================================
        # LOW STOCK
        # =====================================================

        cursor.execute("""
            SELECT

                inventory_id,
                item_name,
                quantity,
                unit,
                minimum_stock,
                status

            FROM inventory

            WHERE status IN (
                'Low Stock',
                'Out of Stock'
            )

            ORDER BY

                CASE

                    WHEN status = 'Out of Stock'
                    THEN 1

                    WHEN status = 'Low Stock'
                    THEN 2

                    ELSE 3

                END,

                quantity ASC
        """)

        low_stock_items = cursor.fetchall()


        # =====================================================
        # RECENT TRANSACTIONS
        # =====================================================

        cursor.execute(f"""
            SELECT

                t.transaction_id,

                t.transaction_date,

                t.total_amount,

                t.payment_status,

                c.customer_name

            FROM transactions t

            LEFT JOIN customers c
                ON t.customer_id = c.customer_id

            WHERE t.transaction_date >= {start_date}

            AND t.transaction_date < {end_date}

            ORDER BY
                t.transaction_date DESC

            LIMIT 10
        """)

        recent_transactions = cursor.fetchall()


        # =====================================================
        # CLOSE DATABASE
        # =====================================================

        cursor.close()

        connection.close()


        # =====================================================
        # DISPLAY REPORT
        # =====================================================

        return render_template(
            "reports.html",

            total_sales=total_sales,

            transaction_count=transaction_count,

            average_sale=average_sale,

            computer_revenue=computer_revenue,

            computer_operating_cost=computer_operating_cost,

            service_revenue=service_revenue,

            service_material_cost=service_material_cost,

            total_expenses=total_expenses,

            net_profit=net_profit,

            service_sales=service_sales,

            low_stock_items=low_stock_items,

            recent_transactions=recent_transactions,

            date_filter=date_filter,

            report_title=report_title,

            full_name=session["full_name"],

            role=session["role"]
        )


    except mysql.connector.Error as error:

        return f"Database Error: {error}"
