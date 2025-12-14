import logging
from datetime import date, datetime, time, timedelta
from functools import wraps
import mysql.connector
from mysql.connector import IntegrityError
import stripe
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from apscheduler.schedulers.background import BackgroundScheduler
import config
import os


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


#logging to track requests and errors in terminal info level
logging.basicConfig(level=getattr(logging, config.LOGGING_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


#logs API requests in terminal 
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")


#expire offers that exceed time
def expire_offers():
    try:
        cursor.execute("""
            UPDATE Offers
            SET OfferStatus = 'Expired'
            WHERE OfferStatus = 'Pending'
              AND ValidUntil IS NOT NULL
              AND ValidUntil <= NOW()
        """)
        pending_expired = cursor.rowcount

        cursor.execute("""
            UPDATE Offers
            SET OfferStatus = 'Expired'
            WHERE OfferStatus = 'Accepted'
              AND ValidUntil IS NOT NULL
              AND ValidUntil <= NOW()
              AND OfferID NOT IN (
                  SELECT DISTINCT OfferID 
                  FROM Payment 
                  WHERE Status = 'Completed'
              )
        """)
        accepted_expired = cursor.rowcount

        db.commit()
        if pending_expired > 0 or accepted_expired > 0:
            print(f"expire_offers: {pending_expired} pending offers expired, {accepted_expired} accepted offers expired")        
    except Exception as e:
        print("expire_offers error:", e)
        db.rollback()


# Stripe payment configuration
stripe.api_key = config.STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY = config.STRIPE_PUBLIC_KEY

# Db connection 
db = mysql.connector.connect(
    host=config.DATABASE['host'],
    user=config.DATABASE['user'],        
    password=config.DATABASE['password'],     
    database=config.DATABASE['database']
)
cursor = db.cursor(dictionary=True)


# Decorator to check if user is logged in and has required role
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied!", "danger")
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# Search for service providers by name, category, or location
@app.route("/search")
@login_required()
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("index"))

    cursor.execute("""
        SELECT sp.ServiceProviderID, sp.Name, sp.Email, sp.PhoneNo, sp.Address, sp.ServiceCategory,
               ROUND(AVG(f.Rating), 1) AS AvgRating,
               COUNT(DISTINCT b.BookingID) AS CompletedJobs
        FROM ServiceProvider sp
        LEFT JOIN Feedback f ON f.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Booking b ON b.ServiceProviderID = sp.ServiceProviderID AND b.Status = 'Completed'
        WHERE sp.ValidationStatus = 'Approved'
          AND (sp.Name LIKE %s OR sp.ServiceCategory LIKE %s OR sp.Address LIKE %s)
        GROUP BY sp.ServiceProviderID
        ORDER BY sp.Name ASC
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))

    providers = cursor.fetchall()
    return render_template("view_providers.html", providers=providers, categories=[], selected_category=None, search_query=query)


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# role based login for customers, providers, and admins
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        user = None

        if role == "customer":
            cursor.execute("SELECT * FROM Customer WHERE Email=%s", (email,))
            user = cursor.fetchone()
        elif role == "provider":
            cursor.execute("SELECT * FROM ServiceProvider WHERE Email=%s", (email,))
            user = cursor.fetchone()
        elif role == "admin":
            cursor.execute("SELECT * FROM Admin WHERE Email=%s", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user["Password"], password):
            if role == "provider":
                if user["ValidationStatus"] == "Pending":
                    flash("Your account is pending verification by the Admin. Please wait.", "warning")
                    return redirect(url_for("login"))
                elif user["ValidationStatus"] == "Rejected":
                    flash("Your account was rejected by the Admin. Contact support.", "danger")
                    return redirect(url_for("login"))
                elif user["ValidationStatus"] != "Approved":
                    flash("Invalid provider status!", "danger")
                    return redirect(url_for("login"))

            session["user_id"] = (
                user.get("CustomerID") or user.get("ServiceProviderID") or user.get("AdminID")
            )
            session["role"] = role
            session["name"] = user["Name"]
            if role == "provider":
                session["service_category"] = user["ServiceCategory"]
                session["service_logo"] = f"images/{user['ServiceCategory'].lower().replace(' ', '_')}_logo.jpg"
            flash(f"{role.capitalize()} login successful!", "success")

            if role == "customer":
                return redirect(url_for("customer_home"))
            elif role == "provider":
                return redirect(url_for("provider_home"))
            elif role == "admin":
                return redirect(url_for("admin_home"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")


# Customer registration
@app.route("/register/customer", methods=["GET", "POST"])
def register_customer():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = generate_password_hash(request.form["password"])

        try:
            cursor.execute(
                "INSERT INTO Customer (Name, Email, PhoneNo, Address, Password) VALUES (%s, %s, %s, %s, %s)",
                (name, email, phone, address, password)
            )
            db.commit()
            flash("Customer registered successfully!", "success")
            return redirect(url_for("login"))
        except IntegrityError as e:
            if e.errno == 1062:
                flash("This email is already registered. Please use a different one.","danger")
            else:
                flash(f"Database error: {e}","danger")
        return redirect(url_for("register_customer"))
    
    return render_template("register_customer.html")


# Service provider registration
@app.route("/register/provider", methods=["GET", "POST"])
def register_provider():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        cnic = request.form["cnic"]
        address = request.form["address"]
        service_category = request.form["service_category"]  
        password = generate_password_hash(request.form["password"])
        
        try:
            cursor.execute(
                "INSERT INTO ServiceProvider (Name, Email, PhoneNo, CNIC, Address, ServiceCategory, Password, ValidationStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (name, email, phone, cnic, address, service_category, password, "Pending")
            ) 
            db.commit()
            flash("Service Provider registered successfully! Please wait for admin approval.", "success")
            return redirect(url_for("login"))
        except IntegrityError as e:
            if e.errno == 1062:
                flash("This email or cnic is already registered. Please use a different one.","danger")
            else:
                flash(f"Database error: {e}","danger")
        return redirect(url_for("register_provider"))

    cursor.execute("SELECT Name FROM Service")
    services = cursor.fetchall()
    return render_template("register_provider.html", services=services)


# Dashboard routes for different user types
@app.route("/customer/home")
@login_required(role="customer")
def customer_home():
    return render_template("customer_homepage.html")

@app.route("/provider/home")
@login_required(role="provider")
def provider_home():
    return render_template("provider_homepage.html")

@app.route("/admin/home")
@login_required(role="admin")
def admin_home():
    return render_template("admin_homepage.html")


# User logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# Admin panel to manage service providers only display 
@app.route("/admin/providers")
@login_required(role="admin")
def manage_providers():
    cursor.execute("SELECT * FROM ServiceProvider WHERE ValidationStatus = 'Pending'")
    pending_providers = cursor.fetchall()

    cursor.execute("SELECT * FROM ServiceProvider WHERE ValidationStatus = 'Approved'")
    approved_providers = cursor.fetchall()

    cursor.execute("SELECT * FROM ServiceProvider WHERE ValidationStatus = 'Rejected'")
    rejected_providers = cursor.fetchall()

    return render_template(
        "manage_providers.html",
        pending_providers=pending_providers,
        approved_providers=approved_providers,
        rejected_providers=rejected_providers
    )

# Update provider status (approve/reject)
@app.route("/admin/providers/update/<int:provider_id>/<string:action>")
@login_required(role="admin")
def update_provider_status(provider_id, action):
    if action == "approve":
        cursor.execute("UPDATE ServiceProvider SET ValidationStatus = 'Approved' WHERE ServiceProviderID = %s", (provider_id,))
        flash("Provider approved successfully!", "success")
    elif action == "reject":
        cursor.execute("UPDATE ServiceProvider SET ValidationStatus = 'Rejected' WHERE ServiceProviderID = %s", (provider_id,))
        flash("Provider rejected successfully!", "danger")

    db.commit()
    return redirect(url_for("manage_providers"))


# Admin management of services (add, edit, delete)
@app.route("/admin/services", methods=["GET", "POST"])
@login_required(role="admin")
def manage_services():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        suggested_price = request.form.get("suggested_price") or None
        
        cursor.execute("INSERT INTO Service (Name, Description, SuggestedPrice) VALUES (%s, %s, %s)", (name, description, suggested_price))
        db.commit()
        flash("Service added successfully!", "success")
        return redirect(url_for("manage_services"))

    cursor.execute("SELECT * FROM Service")
    services = cursor.fetchall()
    return render_template("manage_services.html", services=services)


# Delete a service
@app.route("/admin/services/delete/<int:service_id>")
@login_required(role="admin")
def delete_service(service_id):
    cursor.execute("DELETE FROM Service WHERE ServiceID = %s", (service_id,))
    db.commit()
    flash("Service deleted successfully!", "danger")
    return redirect(url_for("manage_services"))


# Update service details
@app.route("/admin/services/update/<int:service_id>", methods=["POST"])
@login_required(role="admin")
def update_service(service_id):
    name = request.form["name"]
    description = request.form["description"]
    suggested_price = request.form.get("suggested_price") or None

    cursor.execute("""
        UPDATE Service
        SET Name = %s, Description = %s, SuggestedPrice = %s
        WHERE ServiceID = %s
    """, (name, description, suggested_price, service_id))
    db.commit()
    flash("Service updated successfully!", "info")
    return redirect(url_for("manage_services"))



# Commission reports for admin 
@app.route("/admin/commissions")
@login_required(role="admin")
def commission_reports():

    #for Filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    service_filter = request.args.get('service')

    cursor.execute("SELECT ServiceID, Name FROM Service ORDER BY Name")
    services = cursor.fetchall()

# fetch commission data with filters
    query = """
        SELECT
            B.BookingID,
            B.BookingDate,
            C.Name AS CustomerName,
            SP.Name AS ProviderName,
            S.Name AS ServiceName,
            B.FinalAmount AS TotalAmount,
            (B.FinalAmount * 0.20) AS AdminCommission,
            (B.FinalAmount * 0.80) AS ProviderAmount,
            B.ProviderPaymentStatus
        FROM Booking B
        JOIN Customer C ON B.CustomerID = C.CustomerID
        JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
        JOIN Service S ON B.ServiceID = S.ServiceID
        WHERE B.Status = 'Completed'
    """
    params = []

    if start_date:
        query += " AND B.BookingDate >= %s"
        params.append(start_date)
    if end_date:
        query += " AND B.BookingDate <= %s"
        params.append(end_date)
    if service_filter:
        query += " AND B.ServiceID = %s"
        params.append(service_filter)

    query += " ORDER BY B.BookingDate DESC"
    cursor.execute(query, params)
    commissions = cursor.fetchall()


# check total amount paid shouldnt be zero cz commission cant be 20%
    for comm in commissions:
        if comm['TotalAmount'] > 0:
            comm['CommissionPercentage'] = (comm['AdminCommission'] / comm['TotalAmount']) * 100
        else:
            comm['CommissionPercentage'] = 0


# total calculations
    total_revenue = sum(float(c['TotalAmount']) for c in commissions) if commissions else 0
    total_commission = sum(float(c['AdminCommission']) for c in commissions) if commissions else 0
    total_provider_share = sum(float(c['ProviderAmount']) for c in commissions) if commissions else 0


# monthly statistics (group by month, total commission and revenue, create lists for charts)
    from collections import defaultdict
    monthly_data = defaultdict(lambda: {'commission': 0, 'revenue': 0})
    for c in commissions:
        if c['BookingDate']:
            month_key = c['BookingDate'].strftime('%Y-%m')
            monthly_data[month_key]['commission'] += float(c['AdminCommission'])
            monthly_data[month_key]['revenue'] += float(c['TotalAmount'])

    monthly_labels = sorted(monthly_data.keys())
    monthly_commission = [monthly_data[m]['commission'] for m in monthly_labels]
    monthly_revenue = [monthly_data[m]['revenue'] for m in monthly_labels]


# which services generate most commission
    service_data = defaultdict(float)
    for c in commissions:
        service_data[c['ServiceName']] += float(c['AdminCommission'])

    service_names = list(service_data.keys())
    service_commissions = list(service_data.values())

# top 10 providers by revenue
    provider_data = defaultdict(float)
    for c in commissions:
        provider_data[c['ProviderName']] += float(c['TotalAmount'])

    top_providers = sorted(provider_data.items(), key=lambda x: x[1], reverse=True)[:10]
    top_provider_names = [p[0] for p in top_providers]
    top_provider_revenues = [p[1] for p in top_providers]


# daily commission for last 30 days
    daily_data = defaultdict(float)
    for c in commissions:
        if c['BookingDate']:
            day_key = c['BookingDate'].strftime('%Y-%m-%d')
            daily_data[day_key] += float(c['AdminCommission'])

    daily_labels = sorted(daily_data.keys())[-30:]
    daily_commissions = [daily_data[d] for d in daily_labels]

    return render_template(
        "commission_reports.html",
        commissions=commissions,
        total_commission=total_commission,
        total_revenue=total_revenue,
        total_provider_share=total_provider_share,
        services=services,
        monthly_labels=monthly_labels,
        monthly_commission=monthly_commission,
        monthly_revenue=monthly_revenue,
        service_names=service_names,
        service_commissions=service_commissions,
        top_provider_names=top_provider_names,
        top_provider_revenues=top_provider_revenues,
        daily_labels=daily_labels,
        daily_commissions=daily_commissions
    )



# Admin payment display table
@app.route("/admin/payments")
@login_required(role="admin")
def manage_payments():
    # completed bookings where the provider has not yet been paid
    cursor.execute("""
        SELECT 
            B.BookingID,
            B.FinalAmount AS TotalAmount,
            SP.Name AS ProviderName,
            SP.ServiceProviderID AS ProviderID,
            (B.FinalAmount * 0.80) AS ProviderAmount,
            (B.FinalAmount * 0.20) AS AdminCommission,
            B.BookingDate,
            C.Name AS CustomerName
        FROM Booking B
        JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
        JOIN Customer C ON B.CustomerID = C.CustomerID
        WHERE B.Status = 'Completed'
        AND B.ProviderPaymentStatus = 'Pending'
        ORDER BY B.BookingID DESC
    """)
    pending = cursor.fetchall()

# completed provider payouts 
    cursor.execute("""
        SELECT PP.*, SP.Name AS ProviderName
        FROM ProviderPayouts PP
        JOIN ServiceProvider SP ON PP.ProviderID = SP.ServiceProviderID
        ORDER BY PP.PaidAt DESC
    """)
    paid = cursor.fetchall()


# pending refunds
    cursor.execute("""
        SELECT 
            B.BookingID,
            C.Name AS CustomerName,
            SP.Name AS ProviderName,
            P.Amount AS PaidAmount,
            B.BookingDate
        FROM Booking B
        JOIN Customer C ON B.CustomerID = C.CustomerID
        JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
        JOIN Payment P ON B.OfferID = P.OfferID
        WHERE B.RefundStatus = 'Pending'
        ORDER BY B.BookingID DESC
    """)
    pending_refunds = cursor.fetchall()

# completed refunds
    cursor.execute("""
        SELECT 
            B.BookingID,
            C.Name AS CustomerName,
            SP.Name AS ProviderName,
            P.Amount AS PaidAmount,
            B.BookingDate
        FROM Booking B
        JOIN Customer C ON B.CustomerID = C.CustomerID
        JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
        JOIN Payment P ON B.OfferID = P.OfferID
        WHERE B.RefundStatus = 'Approved'
        ORDER BY B.BookingID DESC
    """)
    refunded = cursor.fetchall()

    return render_template(
        "manage_payments.html",
        pending=pending,
        paid=paid,
        pending_refunds=pending_refunds,
        refunded=refunded
    )


# Payment confirmation page to provider from admin display info
@app.route("/admin/payment-confirmation/<payment_type>/<int:booking_id>")
@login_required(role="admin")
def payment_confirmation(payment_type, booking_id):
    if payment_type not in ["provider", "refund"]:
        flash("Invalid payment type.", "danger")
        return redirect(url_for("manage_payments"))

    provider_amount = None

    if payment_type == "provider":
        cursor.execute("""
            SELECT B.FinalAmount AS TotalAmount, B.ServiceProviderID,
                   SP.Name AS ProviderName, C.Name AS CustomerName
            FROM Booking B
            JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
            JOIN Customer C ON B.CustomerID = C.CustomerID
            WHERE B.BookingID=%s
        """, (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for("manage_payments"))

        total = float(booking["TotalAmount"])
        provider_amount = round(total * 0.80, 2)
        commission = round(total * 0.20, 2)

        return render_template(
            "admin_payment_confirmation.html",
            booking=booking,
            booking_id=booking_id,
            total=total,
            provider_amount=provider_amount,
            commission=commission,
            type="provider"
        )

    elif payment_type == "refund":
        cursor.execute("""
            SELECT P.Amount AS PaidAmount,
                   C.Name AS CustomerName, SP.Name AS ProviderName
            FROM Booking B
            JOIN Customer C ON B.CustomerID = C.CustomerID
            JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
            JOIN Payment P ON B.OfferID = P.OfferID
            WHERE B.BookingID=%s
        """, (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            flash("Refund not found.", "danger")
            return redirect(url_for("manage_payments"))

        return render_template(
            "admin_payment_confirmation.html",
            booking=booking,
            booking_id=booking_id,
            total=float(booking["PaidAmount"]),
            provider_amount=provider_amount,
            type="refund"
        )


# Create provider transfer payout (button)
@app.route("/admin/create-transfer-session/<int:booking_id>", methods=["POST"])
@login_required(role="admin")
def create_transfer_session(booking_id):
    try:
        cursor.execute("""
            SELECT B.FinalAmount AS TotalAmount, B.ServiceProviderID, SP.Name AS ProviderName
            FROM Booking B
            JOIN ServiceProvider SP ON B.ServiceProviderID = SP.ServiceProviderID
            WHERE B.BookingID=%s
        """, (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        total = float(booking["TotalAmount"])
        provider_amount = round(total * 0.80, 2)
        commission = round(total * 0.20, 2)

        cursor.execute("""
            INSERT INTO ProviderPayouts 
            (BookingID, ProviderID, TotalAmount, ProviderAmount, AdminCommission, Status, PaidAt)
            VALUES (%s, %s, %s, %s, %s, 'Paid', NOW())
        """, (
            booking_id,
            booking["ServiceProviderID"],
            total,
            provider_amount,
            commission
        ))
        db.commit()

        cursor.execute("UPDATE Booking SET ProviderPaymentStatus='Paid' WHERE BookingID=%s", (booking_id,))
        db.commit()

# tells frontend the transfer was successful
        return jsonify({
            "success": True,
            "message": f"Successfully transferred PKR {provider_amount:.2f} to {booking['ProviderName']}"
        })

    except Exception as e:
        db.rollback()
        print("TRANSFER ERROR:", e)
        return jsonify({"error": f"Transfer failed: {str(e)}"}), 500


# Create refund for customer (button)
@app.route("/admin/create-refund-session/<int:booking_id>", methods=["POST"])
@login_required(role="admin")
def create_refund_session(booking_id):
    try:
        cursor.execute("""
            SELECT P.PaymentID, P.Amount
            FROM Payment P
            JOIN Booking B ON P.OfferID = B.OfferID
            WHERE B.BookingID=%s
        """, (booking_id,))
        payment = cursor.fetchone()
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        cursor.execute("UPDATE Payment SET Status='Refunded' WHERE PaymentID=%s", (payment['PaymentID'],))
        cursor.execute("UPDATE Booking SET RefundStatus='Approved' WHERE BookingID=%s", (booking_id,))
        db.commit()

#tells frontend the refund was successful
        return jsonify({
            "success": True,
            "message": f"Refund of PKR {payment['Amount']:.2f} processed successfully."
        })

    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Refund failed: {str(e)}"}), 500



# Customer booking service with offer creation
@app.route("/customer/book", methods=["GET", "POST"])
@login_required(role="customer")
def book_service():
    if request.method == "POST":
        service_id = request.form.get("service_id")
        date_str = request.form.get("offer_date")
        time_str = request.form.get("offer_time")
        offer_price_raw = request.form.get("offer_price")
        issue = request.form.get("issue")
        location = request.form.get("location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        if not service_id:
            flash("Please select a service.", "warning")
            return redirect(url_for("book_service"))

        if not offer_price_raw:
            flash("Please enter your offer price.", "warning")
            return redirect(url_for("book_service"))

        if not date_str or not time_str:
            flash("Please select date and time.", "warning")
            return redirect(url_for("book_service"))

        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            flash("Invalid date format.", "danger")
            return redirect(url_for("book_service"))

        if booking_date < date.today():
            flash("Booking date cannot be before today!", "danger")
            return redirect(url_for("book_service"))

        current_time = datetime.now().strftime("%H:%M")
        if booking_date == date.today() and time_str < current_time:
            flash("Booking time cannot be in the past!", "danger")
            return redirect(url_for("book_service"))

        try:
            offer_price = float(offer_price_raw)
            if offer_price <= 0:
                raise ValueError("Non-positive")
        except Exception:
            flash("Invalid offer price.", "warning")
            return redirect(url_for("book_service"))

        try:
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT SuggestedPrice FROM Service WHERE ServiceID=%s", (service_id,))
            svc = cur.fetchone()
            cur.close()
        except Exception:
            pass

        try:
            valid_until = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except Exception:
            flash("Invalid date/time for offer.", "danger")
            return redirect(url_for("book_service"))

        try:
            cur = db.cursor()
            cur.execute("""
                INSERT INTO Offers (
                    CustomerID, ServiceID, OfferedPrice, OfferDate, OfferTime,
                    ValidUntil, Location, Latitude, Longitude, IssueDescription, OfferStatus
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (
                session["user_id"], service_id, offer_price, date_str, time_str,
                valid_until, location, latitude, longitude, issue
            ))
            db.commit()
            cur.close()
        except Exception as e:
            print("insert offer error:", e)
            flash("Unable to save offer. Try again.", "danger")
            return redirect(url_for("book_service"))

        flash("Your offer has been sent to providers!", "success")
        return redirect(url_for("customer_home"))

    cursor.execute("SELECT ServiceID, Name, SuggestedPrice FROM Service")
    services = cursor.fetchall()
    return render_template("book_service.html", services=services, today=date.today())

# Get suggested price for a service 
@app.route("/get_suggested_price/<int:service_id>")
def get_suggested_price(service_id):
    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT SuggestedPrice FROM Service WHERE ServiceID = %s", (service_id,))
        row = cur.fetchone()
        cur.close()

        if row and row.get("SuggestedPrice") is not None:
            return jsonify({"suggested_price": float(row["SuggestedPrice"])})
        else:
            return jsonify({"suggested_price": None})
    except Exception as e:
        print("get_suggested_price error:", e)
        return jsonify({"suggested_price": None})
    

# Customer view of their bookings and offers
@app.route("/customer/bookings")
@login_required(role="customer")
def my_bookings():
    expire_offers()
    customer_id = session["user_id"]

# Fetch bookings
    cursor.execute("""
        SELECT 
            b.BookingID,
            b.OfferID,
            s.Name AS ServiceName,
            sp.Email AS ProviderEmail,
            b.BookingDate,
            b.BookingTime,
            b.FinalAmount,
            b.Status,
            b.RefundStatus,
            p.Status AS PaymentStatus
        FROM Booking b
        JOIN Service s ON b.ServiceID = s.ServiceID
        JOIN ServiceProvider sp ON b.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Payment p ON b.OfferID = p.OfferID AND p.PaymentType = 'Customer_Advance'
        WHERE b.CustomerID = %s
        ORDER BY b.BookingDate DESC, b.BookingTime DESC
    """, (customer_id,))
    bookings = cursor.fetchall()

    for booking in bookings:
        if booking['Status'] in ['Incomplete', 'Cancelled'] and booking['PaymentStatus'] == 'Completed':
            booking['PaymentStatus'] = 'Refund_Pending'

    for b in bookings:
        t = b.get("BookingTime")
        if not t:
            continue
        try:
            dt = datetime.strptime(str(t), "%H:%M:%S")
            b["BookingTime"] = dt.strftime("%I:%M %p")
        except ValueError:
            try:
                dt = datetime.strptime(str(t), "%H:%M")
                b["BookingTime"] = dt.strftime("%I:%M %p")
            except:
                pass

# Fetch offers
    cursor.execute("""
        SELECT 
            Offers.OfferID,
            Service.Name AS ServiceName,
            Offers.OfferDate,
            Offers.OfferedPrice,
            Offers.ChatActive,
            Offers.OfferStatus,
            Offers.OfferTime
        FROM Offers
        JOIN Service ON Offers.ServiceID = Service.ServiceID
        WHERE Offers.CustomerID = %s
        AND Offers.OfferStatus IN ('Pending', 'Accepted', 'Rejected', 'Expired')
        ORDER BY OfferDate DESC
    """, (customer_id,))
    offers = cursor.fetchall()

    for offer in offers:
        t = offer.get("OfferTime")
        if not t:
            continue
        if isinstance(t, (datetime, time)):
            offer["OfferTime"] = t.strftime("%I:%M %p")
        elif isinstance(t, timedelta):
            total_seconds = int(t.total_seconds())
            hours = (total_seconds//3600)%24
            minutes = (total_seconds%3600)//60
            offer["OfferTime"] = f"{hours % 12 or 12}:{minutes:02d} {'AM' if hours < 12 else 'PM'}"
        else:
            try:
                offer["OfferTime"] = datetime.strptime(t, "%H:%M:%S").strftime("%I:%M %p")
            except ValueError:
                try:
                    offer["OfferTime"] = datetime.strptime(t, "%H:%M").strftime("%I:%M %p")
                except:
                    pass

    return render_template("my_bookings.html", bookings=bookings, offers=offers)


# Mark booking as complete or incomplete
@app.route("/booking/complete/<int:booking_id>", methods=["POST"])
@login_required()
def mark_booking_complete(booking_id):
    user_id = session.get("user_id")
    user_role = session.get("role")
    action = request.form.get("action", "complete")

# Fetch booking details
    try:
        cursor.execute("""
            SELECT b.BookingID, b.CustomerID, b.ServiceProviderID, b.Status,
                   b.CustomerConfirmedComplete, b.ProviderConfirmedComplete,
                   p.PaymentID, p.Amount, b.FinalAmount,
                   (b.FinalAmount * 0.20) AS AdminCommission,
                   b.OfferID
            FROM Booking b
            LEFT JOIN Payment p 
                ON b.OfferID = p.OfferID 
                AND p.PaymentType = 'Customer_Advance'
            WHERE b.BookingID = %s
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for("my_bookings"))

        if user_id not in (booking["CustomerID"], booking["ServiceProviderID"]):
            flash("You are not authorized to modify this booking.", "danger")
            return redirect(url_for("my_bookings"))

        if user_role == "customer":
            if action == "incomplete":
                if booking['Status'] in ['Completed', 'Incomplete', 'Cancelled']:
                    flash("You cannot mark this as incomplete.", "warning")
                    return redirect(url_for("my_bookings"))

                cursor.execute("""
                    UPDATE Booking
                    SET Status = 'Incomplete',
                        RefundStatus = 'Pending'
                    WHERE BookingID = %s
                """, (booking_id,))

                cursor.execute("""
                    UPDATE Payment
                    SET Status = 'Refund_Pending'
                    WHERE OfferID = %s
                    AND PaymentType = 'Customer_Advance'
                """, (booking["OfferID"],))

                flash("Job marked as incomplete. Refund request submitted.", "success")
            else:
                cursor.execute("""
                    UPDATE Booking
                    SET CustomerConfirmedComplete = 1,
                        Status = CASE 
                            WHEN ProviderConfirmedComplete = 1 THEN 'Completed'
                            ELSE Status
                        END
                    WHERE BookingID = %s
                """, (booking_id,))
                flash("You confirmed completion. Waiting for provider.", "success")

        elif user_role == "provider":
            cursor.execute("""
                UPDATE Booking
                SET ProviderConfirmedComplete = 1,
                    Status = CASE 
                        WHEN CustomerConfirmedComplete = 1 THEN 'Completed'
                        ELSE Status
                    END
                WHERE BookingID = %s
            """, (booking_id,))
            flash("You confirmed completion. Waiting for customer.", "success")

# Check if both parties have confirmed completion
        cursor.execute("""
            SELECT CustomerConfirmedComplete, ProviderConfirmedComplete
            FROM Booking
            WHERE BookingID = %s
        """, (booking_id,))
        flags = cursor.fetchone()

        if flags["CustomerConfirmedComplete"] and flags["ProviderConfirmedComplete"]:
            cursor.execute("""
                UPDATE Booking
                SET Status = 'Completed',
                    ProviderPaymentStatus = 'Pending'
                WHERE BookingID = %s
            """, (booking_id,))

            provider_amount = booking["Amount"] - booking["AdminCommission"]

            cursor.execute("""
                INSERT INTO Payment (CustomerID, ServiceProviderID, OfferID, Amount, Status, PaymentType)
                VALUES (%s, %s, %s, %s, 'Pending', 'Provider_Payout')
            """, (
                booking["CustomerID"],
                booking["ServiceProviderID"],
                booking["OfferID"],
                provider_amount
            ))

            flash("Both confirmed! Job completed. Provider payout pending admin approval.", "success")

        db.commit()

    except Exception as e:
        db.rollback()
        print("mark_booking_complete error:", e)
        flash("Unable to complete booking.", "danger")

    return redirect(url_for("provider_jobs" if user_role == "provider" else "my_bookings"))

# Customer view of service providers with filtering
@app.route("/customer/view_providers")
@login_required(role="customer")
def view_providers():
    category = request.args.get("category")

    cursor.execute("""
        SELECT DISTINCT ServiceCategory 
        FROM ServiceProvider 
        WHERE ValidationStatus='Approved'
    """)
    categories = [row["ServiceCategory"] for row in cursor.fetchall()]

    query = """
        SELECT sp.*, 
               ROUND(AVG(f.Rating), 1) AS AvgRating, 
               COUNT(DISTINCT b.BookingID) AS CompletedJobs
        FROM ServiceProvider sp
        LEFT JOIN Feedback f ON f.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Booking b ON b.ServiceProviderID = sp.ServiceProviderID AND b.Status = 'Completed'
        WHERE sp.ValidationStatus = 'Approved'
    """
    params = ()

    if category:
        query += " AND sp.ServiceCategory = %s"
        params = (category,)

    query += " GROUP BY sp.ServiceProviderID ORDER BY sp.Name ASC"
    cursor.execute(query, params)
    providers = cursor.fetchall()

    return render_template("view_providers.html", providers=providers, categories=categories, selected_category=category)

# View individual provider profile
@app.route("/provider/<int:provider_id>")
@login_required(role="customer")
def view_provider_profile(provider_id):
    cursor.execute("""
        SELECT sp.ServiceProviderID, sp.Name, sp.Email, sp.PhoneNo, sp.Address, sp.ServiceCategory,
               ROUND(AVG(f.Rating), 1) AS AvgRating,
               COUNT(DISTINCT b.BookingID) AS CompletedJobs
        FROM ServiceProvider sp
        LEFT JOIN Feedback f ON f.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Booking b ON b.ServiceProviderID = sp.ServiceProviderID AND b.Status = 'Completed'
        WHERE sp.ServiceProviderID = %s
        GROUP BY sp.ServiceProviderID
    """, (provider_id,))
    provider = cursor.fetchone()

    if not provider:
        flash("Provider not found.", "danger")
        return redirect(url_for("view_providers"))

    cursor.execute("""
        SELECT c.Name AS CustomerName, f.Rating, f.Text, f.FeedbackDate
        FROM Feedback f
        JOIN Customer c ON f.CustomerID = c.CustomerID
        WHERE f.ServiceProviderID = %s
        ORDER BY f.FeedbackDate DESC
    """, (provider_id,))
    feedbacks = cursor.fetchall()

    db.commit()
    return render_template("view_provider_profile.html", provider=provider, feedbacks=feedbacks)


# Customer feedback submission
@app.route("/customer/feedback", methods=["GET", "POST"])
@login_required("customer")
def customer_feedback():
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        provider_id = request.form.get("provider_id")
        booking_id = request.form.get("booking_id")
        rating = request.form.get("rating")
        feedback_text = request.form.get("feedback")
        customer_id = session["user_id"]

        if not all([provider_id, booking_id, rating, feedback_text]):
            flash("All fields are required.", "warning")
            return redirect(url_for("customer_feedback"))
        
# Check if feedback already exists for this booking 
        cursor.execute("""
            SELECT FeedbackID FROM Feedback
            WHERE BookingID = %s AND CustomerID = %s
        """, (booking_id, customer_id))
        existing_feedback = cursor.fetchone()

        if existing_feedback:
            flash("You have already submitted feedback for this service.", "info")
            return redirect(url_for("customer_feedback"))

        cursor.execute("""
            INSERT INTO Feedback (ServiceProviderID, CustomerID, BookingID, Rating, Text)
            VALUES (%s, %s, %s, %s, %s)
        """, (provider_id, customer_id, booking_id, rating, feedback_text))

        db.commit()
        flash("Thank you! Your feedback has been submitted.", "success")
        return redirect(url_for("customer_feedback"))


# Fetch completed jobs for feedback
    cursor.execute("""
        SELECT 
            b.BookingID,
            s.Name AS ServiceName,
            sp.ServiceProviderID,
            sp.Name AS ProviderName,
            b.BookingDate,
            b.BookingTime,
            b.FinalAmount AS OfferedPrice,
            CASE 
                WHEN f.FeedbackID IS NOT NULL THEN TRUE 
                ELSE FALSE 
            END AS FeedbackGiven
        FROM Booking b
        JOIN Service s ON b.ServiceID = s.ServiceID
        JOIN ServiceProvider sp ON b.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Feedback f 
            ON f.BookingID = b.BookingID 
            AND f.CustomerID = b.CustomerID
        WHERE b.CustomerID = %s AND b.Status = 'Completed'
        ORDER BY b.BookingDate DESC
    """, (session["user_id"],))

    completed_jobs = cursor.fetchall()

    for job in completed_jobs:
        t = job.get("BookingTime")
        if t:
            from datetime import datetime, time, timedelta
            if isinstance(t, timedelta):
                total_seconds = int(t.total_seconds())
                hours = (total_seconds // 3600) % 24
                minutes = (total_seconds % 3600) // 60
                job["FormattedTime"] = f"{hours % 12 or 12}:{minutes:02d} {'AM' if hours < 12 else 'PM'}"
            elif isinstance(t, (datetime, time)):
                job["FormattedTime"] = t.strftime("%I:%M %p")
            else:
                try:
                    job["FormattedTime"] = datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p")
                except:
                    job["FormattedTime"] = str(t)
        else:
            job["FormattedTime"] = None

    return render_template("customer_feedback.html", completed_jobs=completed_jobs)


# Provider profile 
@app.route("/provider/profile", methods=["GET", "POST"])
@login_required(role="provider")
def provider_profile():
    provider_id = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        base_price = request.form.get("base_price")

        cursor.execute("""
            UPDATE ServiceProvider 
            SET Name=%s, Email=%s, PhoneNo=%s, Address=%s, BasePrice=%s
            WHERE ServiceProviderID=%s
        """, (name, email, phone, address, base_price, provider_id))
        db.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("provider_profile"))

    cursor.execute("""
        SELECT sp.*,
               ROUND(AVG(f.Rating), 1) AS AvgRating,
               COUNT(DISTINCT b.BookingID) AS CompletedJobs
        FROM ServiceProvider sp
        LEFT JOIN Feedback f ON f.ServiceProviderID = sp.ServiceProviderID
        LEFT JOIN Booking b ON b.ServiceProviderID = sp.ServiceProviderID AND b.Status='Completed'
        WHERE sp.ServiceProviderID = %s
        GROUP BY sp.ServiceProviderID
    """, (provider_id,))
    provider = cursor.fetchone()

    cursor.execute("""
        SELECT f.Rating, f.Text, c.Name AS CustomerName, f.FeedbackDate
        FROM Feedback f
        JOIN Customer c ON f.CustomerID = c.CustomerID
        WHERE f.ServiceProviderID = %s
        ORDER BY f.FeedbackDate DESC
    """, (provider_id,))
    feedbacks = cursor.fetchall()

    service_logo = session.get("service_logo")
    db.commit()
    return render_template("provider_profile.html", provider=provider, feedbacks=feedbacks, service_logo=service_logo)


# Real-time chat 
socketio = SocketIO(app, async_mode='eventlet')

# Join chat room
@socketio.on('join_room_event')
def handle_join_room(data):
    offer_id = data.get('offer_id')
    sender_id = data.get('sender_id')
    sender_role = data.get('sender_role')

    if not all([offer_id, sender_id, sender_role]):
        return

    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT ChatInitiatorID, AcceptedProviderID, ChatActive, CustomerID
            FROM Offers WHERE OfferID=%s
        """, (offer_id,))
        offer = cur.fetchone()

        if not offer:
            emit('error', {'msg': 'Offer not found'})
            return

        if sender_role == 'provider':
            room = f"offer_{offer_id}provider{sender_id}"

            if not offer['ChatActive'] or not offer['ChatInitiatorID']:
                cur.execute("""
                    UPDATE Offers
                    SET ChatInitiatorID=%s, ChatActive=1, ChatStarted=1
                    WHERE OfferID=%s
                """, (sender_id, offer_id))
                db.commit()
        else:
            if offer['ChatInitiatorID']:
                room = f"offer_{offer_id}provider{offer['ChatInitiatorID']}"
            else:
                emit('error', {'msg': 'No provider has started chat yet'})
                return

        join_room(room)
        print(f"User {sender_id} ({sender_role}) joined room: {room}")

        if 'active_chat_rooms' not in session:
            session['active_chat_rooms'] = {}
        session['active_chat_rooms'][offer_id] = room
        session.modified = True

    except Exception as e:
        print(f"Join room error: {e}")
        emit('error', {'msg': 'Failed to join chat'})
    finally:
        cur.close()

# Send message in chat
@socketio.on('send_message')
def handle_message(data):
    offer_id = data.get('offer_id')
    sender_id = data.get('sender_id')
    sender_role = data.get('sender_role')
    msg = data.get('msg').strip()

    if not all([offer_id, sender_id, sender_role, msg]):
        return

    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT ChatInitiatorID, AcceptedProviderID, CustomerID
            FROM Offers WHERE OfferID=%s
        """, (offer_id,))
        offer = cur.fetchone()

        if not offer:
            emit('error', {'msg': 'Offer not found'})
            return

        if sender_role == 'provider':
            room = f"offer_{offer_id}provider{sender_id}"
        else:
            if offer['ChatInitiatorID']:
                room = f"offer_{offer_id}provider{offer['ChatInitiatorID']}"
            else:
                emit('error', {'msg': 'No active chat room'})
                return

        cur.execute("""
            INSERT INTO Messages (OfferID, SenderID, SenderRole, Message)
            VALUES (%s, %s, %s, %s)
        """, (offer_id, sender_id, sender_role, msg))
        db.commit()

        emit('receive_message', {
            'sender_role': sender_role,
            'sender_id': sender_id,
            'message': msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, room=room)

        print(f"Message sent to room: {room}")

    except Exception as e:
        db.rollback()
        print(f"Send message error: {e}")
        emit('error', {'msg': 'Failed to send message'})
    finally:
        cur.close()

# Leave chat room
@socketio.on('leave_room_event')
def handle_leave_room(data):
    offer_id = data.get('offer_id')
    sender_id = data.get('sender_id')
    sender_role = data.get('sender_role')

    if not all([offer_id, sender_id, sender_role]):
        return

    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT ChatInitiatorID, AcceptedProviderID FROM Offers WHERE OfferID=%s", (offer_id,))
        offer = cur.fetchone()

        if offer:
            if sender_role == 'provider':
                room = f"offer_{offer_id}provider{sender_id}"

                if offer['ChatInitiatorID'] == sender_id:
                    cur.execute("""
                        UPDATE Offers
                        SET ChatActive = 0
                        WHERE OfferID = %s AND ChatInitiatorID = %s
                    """, (offer_id, sender_id))
                    db.commit()

                cur.execute("""
                    INSERT INTO Messages (OfferID, SenderID, SenderRole, Message)
                    VALUES (%s, %s, 'system', %s)
                """, (offer_id, sender_id, f"Provider has left the chat. Waiting for another provider to join..."))
                db.commit()
            else:
                if offer['ChatInitiatorID']:
                    room = f"offer_{offer_id}provider{offer['ChatInitiatorID']}"
                    cur.execute("""
                        INSERT INTO Messages (OfferID, SenderID, SenderRole, Message)
                        VALUES (%s, %s, 'system', %s)
                    """, (offer_id, sender_id, "Customer has left the chat."))
                    db.commit()
                else:
                    return

            leave_room(room)

            emit('receive_message', {
                'sender_role': 'system',
                'message': f"{sender_role.capitalize()} has left the chat.",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, room=room)

            print(f"User {sender_id} left room: {room}")

    except Exception as e:
        print(f"Leave room error: {e}")
    finally:
        cur.close()

# Chat interface for offers
@app.route('/offer/<int:offer_id>/chat')
@login_required()
def offer_chat(offer_id):
    user_role = session['role']      
    user_id = session['user_id']

    cursor.execute("""
        SELECT
            o.*,
            c.Email AS CustomerEmail,
            c.CustomerID,
            sp.Email AS ProviderEmail,
            sp.ServiceProviderID
        FROM Offers o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        LEFT JOIN ServiceProvider sp ON o.ChatInitiatorID = sp.ServiceProviderID
        WHERE o.OfferID = %s
    """, (offer_id,))
    offer = cursor.fetchone()

    if not offer:
        flash("Offer not found.", "danger")
        return redirect(url_for("my_bookings"))

    if user_role == 'customer':
        if user_id != offer['CustomerID']:
            flash("Access denied.", "danger")
            return redirect(url_for("my_bookings"))
        
        if not offer['ChatInitiatorID']:
            flash("Chat is not available until a provider initiates it.", "warning")
            return redirect(url_for("my_bookings"))
    else:
        can_access = False
        is_new_initiator = False
        
        if not offer['ChatInitiatorID']:
            can_access = True
            is_new_initiator = True
        elif user_id == offer['ChatInitiatorID']:
            can_access = True
        elif user_id == offer['AcceptedProviderID']:
            can_access = True
        elif not offer['ChatActive']:
            can_access = True
            is_new_initiator = True
            cursor.execute("""
                UPDATE Offers 
                SET ChatInitiatorID=%s, ChatActive=1 
                WHERE OfferID=%s
            """, (user_id, offer_id))
            db.commit()
        
        if not can_access:
            flash("Another provider is currently chatting with this customer.", "warning")
            return redirect(url_for("provider_home"))

    current_chat_initiator = offer['ChatInitiatorID']
    
    if user_role == 'customer':
        if current_chat_initiator:
            cursor.execute("""
                SELECT MIN(Timestamp) as session_start 
                FROM Messages 
                WHERE OfferID = %s AND SenderID = %s AND SenderRole = 'provider'
                ORDER BY Timestamp ASC 
                LIMIT 1
            """, (offer_id, current_chat_initiator))
            session_data = cursor.fetchone()
            
            if session_data and session_data['session_start']:
                cursor.execute("""
                    SELECT SenderRole, SenderID, Message, Timestamp
                    FROM Messages
                    WHERE OfferID = %s AND Timestamp >= %s
                    ORDER BY Timestamp ASC
                """, (offer_id, session_data['session_start']))
                messages = cursor.fetchall()
                
                cursor.execute("""
                    SELECT COUNT(*) as prev_sessions 
                    FROM Messages 
                    WHERE OfferID = %s AND Timestamp < %s
                """, (offer_id, session_data['session_start']))
                prev_sessions = cursor.fetchone()['prev_sessions']
                
                if prev_sessions > 0:
                    system_msg = {
                        'SenderRole': 'system',
                        'Message': 'New provider joined the chat. Previous conversation history is not visible.',
                        'Timestamp': datetime.now()
                    }
                    messages.insert(0, system_msg)
            else:
                cursor.execute("""
                    SELECT SenderRole, SenderID, Message, Timestamp
                    FROM Messages
                    WHERE OfferID = %s
                    ORDER BY Timestamp ASC
                """, (offer_id,))
                messages = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT SenderRole, SenderID, Message, Timestamp
                FROM Messages
                WHERE OfferID = %s
                ORDER BY Timestamp ASC
            """, (offer_id,))
            messages = cursor.fetchall()
    else:
        current_provider_id = user_id
        
        if current_chat_initiator == current_provider_id:
            cursor.execute("""
                SELECT MIN(Timestamp) as session_start 
                FROM Messages 
                WHERE OfferID = %s AND SenderID = %s AND SenderRole = 'provider'
                ORDER BY Timestamp ASC 
                LIMIT 1
            """, (offer_id, current_provider_id))
            session_data = cursor.fetchone()
            
            if session_data and session_data['session_start']:
                cursor.execute("""
                    SELECT SenderRole, SenderID, Message, Timestamp
                    FROM Messages
                    WHERE OfferID = %s AND Timestamp >= %s
                    ORDER BY Timestamp ASC
                """, (offer_id, session_data['session_start']))
                messages = cursor.fetchall()
            else:
                cursor.execute("""
                    SELECT SenderRole, SenderID, Message, Timestamp
                    FROM Messages
                    WHERE OfferID = %s
                    ORDER BY Timestamp ASC
                """, (offer_id,))
                messages = cursor.fetchall()
        else:
            join_time = datetime.now() - timedelta(seconds=30)
            cursor.execute("""
                SELECT SenderRole, SenderID, Message, Timestamp
                FROM Messages
                WHERE OfferID = %s AND Timestamp >= %s
                ORDER BY Timestamp ASC
            """, (offer_id, join_time))
            messages = cursor.fetchall()
            
            system_msg = {
                'SenderRole': 'system',
                'Message': 'You have joined this chat. Only recent messages are visible.',
                'Timestamp': datetime.now()
            }
            messages.append(system_msg)

    return render_template('chat.html', 
                         messages=messages, 
                         offer_id=offer_id, 
                         user_role=user_role, 
                         user_id=user_id,
                         other_party_email=offer['CustomerEmail'] if user_role == 'provider' else offer['ProviderEmail'],
                         your_email=offer['CustomerEmail'] if user_role == 'customer' else offer['ProviderEmail'] or "You",
                         chat_initiator_id=current_chat_initiator or user_id)


# Provider view of available offers in their category
@app.route("/provider/offers")
@login_required(role="provider")
def provider_offers():
    expire_offers()
    
    provider_id = session["user_id"]

    # Get provider's service category
    cursor.execute("""
        SELECT ServiceCategory 
        FROM ServiceProvider 
        WHERE ServiceProviderID = %s
    """, (provider_id,))
    provider = cursor.fetchone()

    if not provider or not provider.get("ServiceCategory"):
        flash("No service category assigned to your profile.", "warning")
        return redirect(url_for("provider_home"))

    category = provider["ServiceCategory"]

    # Fetch available offers in that category
    cursor.execute("""
        SELECT 
            Offers.OfferID,
            Customer.Name AS CustomerName,
            Service.Name AS ServiceName,
            Offers.OfferedPrice,
            Offers.OfferDate,
            Offers.OfferTime,
            Offers.Location,
            Offers.IssueDescription,
            Offers.OfferStatus,
            Offers.ChatStarted
        FROM Offers
        JOIN Customer ON Offers.CustomerID = Customer.CustomerID
        JOIN Service ON Offers.ServiceID = Service.ServiceID
        WHERE Service.Name = %s
          AND Offers.OfferStatus = 'Pending'
          AND Offers.ValidUntil > NOW()
        ORDER BY Offers.OfferDate DESC
    """, (category,))
    
    offers = cursor.fetchall()

    # Time formatting
    for offer in offers:
        t = offer.get("OfferTime")
        if not t:
            continue

        if isinstance(t, (datetime, time)):
            offer["OfferTime"] = t.strftime("%I:%M %p")
        elif isinstance(t, timedelta):
            total_seconds = int(t.total_seconds())
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds % 3600) // 60
            offer["OfferTime"] = f"{hours % 12 or 12}:{minutes:02d} {'AM' if hours < 12 else 'PM'}"
        else:
            try:
                offer["OfferTime"] = datetime.strptime(t, "%H:%M:%S").strftime("%I:%M %p")
            except ValueError:
                try:
                    offer["OfferTime"] = datetime.strptime(t, "%H:%M").strftime("%I:%M %p")
                except:
                    pass

    return render_template(
        "provider_offers.html",
        offers=offers,
        current_time=datetime.now().strftime("%I:%M %p")
    )


# Provider response to offers can accept
@app.route("/provider/respond_offer/<int:offer_id>", methods=["POST"])
@login_required(role="provider")
def respond_offer(offer_id):
    provider_id = session["user_id"]
    action = request.form.get("action")

    if action != "accept":
        flash("Only accepting offers is allowed.", "danger")
        return redirect(url_for("provider_offers"))

    try:
        cursor.execute("""
            UPDATE Offers
            SET OfferStatus='Accepted', AcceptedProviderID=%s
            WHERE OfferID=%s
              AND OfferStatus='Pending'
              AND (ValidUntil IS NULL OR ValidUntil >= NOW())
        """, (provider_id, offer_id))

        if cursor.rowcount == 0:
            db.commit()
            flash("Offer was taken/changed by someone else.", "danger")
            return redirect(url_for("provider_offers"))

        db.commit()
        flash("Offer accepted successfully!", "success")

    except Exception as e:
        db.rollback()
        print("respond_offer error:", e)
        flash("An error occurred. Try again.", "danger")

    return redirect(url_for("provider_offers"))

# Customer payment page for accepted offers
@app.route("/customer/pay/<int:offer_id>", methods=["GET"])
@login_required(role="customer")
def pay_offer(offer_id):
    customer_id = session["user_id"]

# Fetch offer details
    cursor.execute("""
        SELECT Offers.*, Service.Name AS ServiceName
         FROM Offers
        JOIN Service ON Offers.ServiceID = Service.ServiceID
        WHERE Offers.OfferID=%s AND Offers.CustomerID=%s AND Offers.OfferStatus='Accepted'
    """, (offer_id, customer_id))
    offer = cursor.fetchone()
    if not offer:
        flash("Offer not available for payment.", "danger")
        return redirect(url_for("my_bookings"))

    return render_template("customer_payments.html", offer=offer, stripe_pub_key=STRIPE_PUBLIC_KEY)

# Create Stripe checkout session for payment
@app.route("/create-checkout-session/<int:offer_id>", methods=["POST"])
@login_required(role="customer")
def create_checkout_session(offer_id):
    customer_id = session["user_id"]

# Fetch offer details
    cursor.execute("""
        SELECT Offers.*, Service.Name AS ServiceName
        FROM Offers
        JOIN Service ON Offers.ServiceID = Service.ServiceID
        WHERE Offers.OfferID=%s AND Offers.CustomerID=%s AND Offers.OfferStatus='Accepted'
    """, (offer_id, customer_id))
    offer = cursor.fetchone()
    if not offer:
        return jsonify({"error": "Offer not found"}), 404

    try:
        checkout_session = stripe.checkout.Session.create (
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': f'Service Payment for Offer #{offer_id}',
                    },
                    'unit_amount': int(offer['OfferedPrice'] * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment_success', offer_id=offer_id, _external=True),
            cancel_url=url_for('pay_offer', offer_id=offer_id, _external=True),
            metadata={'offer_id': offer_id}
        )
        return jsonify({"id": checkout_session.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Payment success handler
@app.route("/payment-success/<int:offer_id>")
@login_required(role="customer")
def payment_success(offer_id):
    customer_id = session["user_id"]
    
    # Verify offer details
    cursor.execute("SELECT * FROM Offers WHERE OfferID=%s AND CustomerID=%s AND OfferStatus='Accepted'",
                   (offer_id, customer_id))
    offer = cursor.fetchone()
    if not offer:
        flash("Offer not found.", "danger")
        return redirect(url_for("my_bookings"))

    try:
        # Record payment with PaymentType
        cursor.execute("""
            INSERT INTO Payment (CustomerID, ServiceProviderID, OfferID, Amount, Status, PaymentType)
            VALUES (%s, %s, %s, %s, 'Completed', 'Customer_Advance')
        """, (customer_id, offer['AcceptedProviderID'], offer_id, offer['OfferedPrice']))
        
        # Create booking
        cursor.execute("""
            INSERT INTO Booking (OfferID, CustomerID, ServiceProviderID, ServiceID,
                                 BookingDate, BookingTime, FinalAmount, Status)
            SELECT OfferID, CustomerID, AcceptedProviderID, ServiceID,
                   OfferDate, OfferTime, OfferedPrice, 'Scheduled'
            FROM Offers
            WHERE OfferID=%s
        """, (offer_id,))
        
        # Update offer status
        cursor.execute("UPDATE Offers SET OfferStatus='Paid' WHERE OfferID=%s", (offer_id,))
        
        db.commit()
        flash("Payment successful! Booking confirmed.", "success")
        
    except Exception as e:
        db.rollback()
        print(f"Payment success error: {e}")
        flash("Error processing payment. Please contact support.", "danger")
    
    return redirect(url_for("my_bookings"))


# Stripe webhook to tell app of payment success
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = config.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Payment received for session:", session['id'])
       
    return '', 200


# Provider view of their assigned jobs
@app.route("/provider/jobs")
@login_required(role="provider")
def provider_jobs():
    provider_id = session["user_id"]

    cursor.execute("""
        SELECT 
            B.BookingID,
            B.OfferID,
            S.Name AS ServiceName,
            C.Name AS CustomerName,
            B.BookingDate,
            B.BookingTime,
            O.IssueDescription,
            O.Location,
            B.Status AS BookingStatus,
            B.ProviderPaymentStatus,
            B.ProviderConfirmedComplete,
            B.CustomerConfirmedComplete,
            (SELECT P.Status FROM Payment P 
             WHERE P.OfferID = B.OfferID 
             ORDER BY P.PaymentDate DESC 
             LIMIT 1) AS PaymentStatus
        FROM Booking B
        JOIN Service S ON B.ServiceID = S.ServiceID
        JOIN Customer C ON B.CustomerID = C.CustomerID
        JOIN Offers O ON B.OfferID = O.OfferID
        WHERE B.ServiceProviderID = %s
        ORDER BY B.BookingDate DESC, B.BookingTime DESC
    """, (provider_id,))
    
    jobs = cursor.fetchall()

    for job in jobs:
        t = job.get("BookingTime")
        if t:
            try:
                if isinstance(t, (datetime, time)):
                    job["BookingTime"] = t.strftime("%I:%M %p")
                else:
                    job["BookingTime"] = datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p")
            except:
                pass

    return render_template("provider_jobs.html", jobs=jobs)

# Provider payment history
@app.route("/provider/payments")
@login_required(role="provider")
def provider_payments():
    provider_id = session["user_id"]

    cursor.execute("""
        SELECT 
            PP.PayoutID AS PaymentID,
            C.Email AS CustomerEmail,
            B.BookingDate,
            PP.ProviderAmount AS Amount,
            PP.Status AS PaymentStatus
        FROM ProviderPayouts PP
        JOIN Booking B ON PP.BookingID = B.BookingID
        JOIN Customer C ON B.CustomerID = C.CustomerID
        WHERE PP.ProviderID = %s
        ORDER BY PP.PaidAt DESC
    """, (provider_id,))
    
    payments = cursor.fetchall()

    for p in payments:
        if p.get("BookingDate"):
            if isinstance(p["BookingDate"], (datetime,)):
                p["BookingDateFormatted"] = p["BookingDate"].strftime("%d-%m-%Y")
            else:
                try:
                    dt = datetime.strptime(str(p["BookingDate"]), "%Y-%m-%d")
                    p["BookingDateFormatted"] = dt.strftime("%d-%m-%Y")
                except:
                    p["BookingDateFormatted"] = str(p["BookingDate"])
        else:
            p["BookingDateFormatted"] = "N/A"

        if p.get("Amount") is not None:
            p["AmountFormatted"] = f"PKR {float(p['Amount']):,.2f}"
        else:
            p["AmountFormatted"] = "N/A"

    return render_template("provider_payments.html", payments=payments)


# Update job status (complete/cancel)
@app.route("/provider/jobs/update/<int:booking_id>/<string:action>")
@login_required(role="provider")
def update_job_status(booking_id, action):
    provider_id = session.get("user_id")
    VALID_ACTIONS = {"complete", "cancelled"}

    if action not in VALID_ACTIONS:
        flash("Invalid action.", "danger")
        return redirect(url_for("provider_jobs"))

    try:
        cursor.execute("""
            SELECT BookingID, ServiceProviderID, Status, OfferID,
                   ProviderConfirmedComplete, CustomerConfirmedComplete
            FROM Booking
            WHERE BookingID = %s
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for("provider_jobs"))

        if booking['ServiceProviderID'] != provider_id:
            flash("You don't have permission to update this booking.", "danger")
            return redirect(url_for("provider_jobs"))

        if booking['Status'] in ['Completed', 'Incomplete', 'Cancelled']:
            flash("Cannot update a completed, incomplete, or cancelled job.", "warning")
            return redirect(url_for("provider_jobs"))

        if action == "complete":
            new_status = 'Completed' if booking.get("CustomerConfirmedComplete") else booking['Status']

            cursor.execute("""
                UPDATE Booking
                SET ProviderConfirmedComplete = 1,
                    Status = %s,
                    ProviderPaymentStatus = CASE
                        WHEN %s = 1 THEN 'Pending'
                        ELSE ProviderPaymentStatus
                    END
                WHERE BookingID = %s
            """, (new_status, booking.get("CustomerConfirmedComplete"), booking_id))

            if booking.get("CustomerConfirmedComplete"):
                flash("Both parties confirmed! Job completed. Provider payout pending admin approval.", "success")
            else:
                flash("You confirmed completion. Waiting for customer confirmation.", "success")

        elif action == "cancelled":
            cursor.execute("""
                UPDATE Booking
                SET Status = 'Cancelled',
                    RefundStatus = 'Pending'
                WHERE BookingID = %s
            """, (booking_id,))

            offer_id = booking.get("OfferID")
            if offer_id:
                cursor.execute("""
                    UPDATE Payment
                    SET Status = 'Refund_Pending'
                    WHERE OfferID = %s
                      AND PaymentType = 'Customer_Advance'
                      AND Status = 'Completed'
                """, (offer_id,))

            flash("Job cancelled. Refund request submitted to admin.", "warning")

        db.commit()

    except Exception as e:
        db.rollback()
        print("update_job_status error:", e)
        import traceback
        traceback.print_exc()
        flash("Error updating job status. Please try again.", "danger")

    return redirect(url_for("provider_jobs"))

# Background scheduler to expire offers automatically
scheduler = BackgroundScheduler()
scheduler.add_job(expire_offers, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
