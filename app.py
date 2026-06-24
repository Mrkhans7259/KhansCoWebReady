from flask import Flask, render_template, request, redirect, session, send_file, send_from_directory
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from database.dashboard_repository import DashboardRepository
from database.client_repository import ClientRepository
from database.fee_repository import FeeRepository
from database.client_ledger_repository import ClientLedgerRepository
from database.gst_repository import GSTRepository
from database.invoice_repository import InvoiceRepository
from database.user_repository import UserRepository
from database.report_repository import ReportRepository
from database.whatsapp_repository import WhatsAppRepository
from database.backup_repository import BackupRepository
from database.client_portal_repository import ClientPortalRepository
from database.ticket_repository import TicketRepository
from database.status_repository import StatusRepository
from database.file_center_repository import FileCenterRepository
from database.notification_repository import NotificationRepository
from database.profile_repository import ProfileRepository
from database.import_repository import ImportRepository
from database.password_reset_repository import PasswordResetRepository

app = Flask(__name__)
app.secret_key = "khansco_secret_key"

UPLOAD_FOLDER = "uploads"
CLIENT_FILES_FOLDER = "client_files"
PROFILE_PHOTOS_FOLDER = "uploads/profile_photos"
IMPORT_FOLDER = "uploads/imports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CLIENT_FILES_FOLDER"] = CLIENT_FILES_FOLDER
app.config["PROFILE_PHOTOS_FOLDER"] = PROFILE_PHOTOS_FOLDER
app.config["IMPORT_FOLDER"] = IMPORT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIENT_FILES_FOLDER, exist_ok=True)
os.makedirs(PROFILE_PHOTOS_FOLDER, exist_ok=True)
os.makedirs(IMPORT_FOLDER, exist_ok=True)


# ---------------- ACCESS CONTROL ---------------- #

def admin_or_user_required():
    return "user_id" in session


def admin_required():
    return "user_id" in session and session.get("role") == "Admin"


def client_required():
    return "client_id" in session


def access_denied():
    return "<h2>Access Denied</h2><a href='/dashboard'>Back to Dashboard</a>"


# ---------------- ADMIN LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():
    user_repo = UserRepository()

    if request.method == "POST":
        user = user_repo.verify_login(
            request.form.get("username"),
            request.form.get("password")
        )

        if user:
            session.clear()
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[2]
            return redirect("/dashboard")

        return "<h2>Invalid Login</h2><a href='/'>Try Again</a>"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():
    if not admin_or_user_required():
        return redirect("/")

    dashboard_repo = DashboardRepository()
    notification_repo = NotificationRepository()

    return render_template(
        "dashboard.html",
        total_clients=dashboard_repo.total_clients(),
        total_gst=dashboard_repo.total_gst_records(),
        pending_gstr1=dashboard_repo.pending_gstr1(),
        pending_gstr3b=dashboard_repo.pending_gstr3b(),
        unread_notifications=notification_repo.unread_notifications_count(),
        open_tickets=notification_repo.open_tickets_count(),
        uploaded_documents=notification_repo.uploaded_documents_count(),
        registered_clients=notification_repo.registered_clients_count(),
        role=session.get("role"),
        username=session.get("username")
    )


# ---------------- CLIENT MASTER ---------------- #

@app.route("/clients")
def clients():
    if not admin_or_user_required():
        return redirect("/")

    repo = ClientRepository()
    search = request.args.get("search", "")
    data = repo.search_clients(search) if search else repo.get_all_clients()

    return render_template("clients.html", clients=data, search=search)


@app.route("/add-client", methods=["GET", "POST"])
def add_client():
    if not admin_or_user_required():
        return redirect("/")

    repo = ClientRepository()

    if request.method == "POST":
        repo.add_client(
            request.form["client_code"],
            request.form["client_name"],
            request.form["gstin"],
            request.form["mobile"],
            request.form["email"],
            request.form["assigned_staff"]
        )
        return redirect("/clients")

    return render_template("add_client.html")


@app.route("/edit-client/<int:client_id>", methods=["GET", "POST"])
def edit_client(client_id):
    if not admin_or_user_required():
        return redirect("/")

    repo = ClientRepository()

    if request.method == "POST":
        repo.update_client(
            client_id,
            request.form["client_code"],
            request.form["client_name"],
            request.form["gstin"],
            request.form["mobile"],
            request.form["email"],
            request.form["assigned_staff"]
        )
        return redirect("/clients")

    return render_template("edit_client.html", client=repo.get_client_by_id(client_id))


@app.route("/delete-client/<int:client_id>")
def delete_client(client_id):
    if not admin_or_user_required():
        return redirect("/")

    ClientRepository().delete_client(client_id)
    return redirect("/clients")


@app.route("/admin-profile/<int:client_id>", methods=["GET", "POST"])
def admin_profile(client_id):
    if not admin_or_user_required():
        return redirect("/")

    repo = ProfileRepository()

    if request.method == "POST":
        repo.update_client_profile(
            client_id,
            request.form["client_code"],
            request.form["client_name"],
            request.form["gstin"],
            request.form["mobile"],
            request.form["email"],
            request.form["assigned_staff"]
        )
        return redirect("/clients")

    return render_template("admin_profile.html", profile=repo.get_client_profile(client_id))


# ---------------- FEE TRACKER ---------------- #

@app.route("/fee-tracker", methods=["GET", "POST"])
def fee_tracker():
    if not admin_or_user_required():
        return redirect("/")

    repo = FeeRepository()

    if request.method == "POST":
        repo.add_fee(
            request.form["client_id"],
            request.form["financial_year"],
            request.form["month"],
            request.form["fee_amount"],
            request.form["received_amount"],
            request.form["payment_date"],
            request.form["remarks"]
        )
        return redirect("/fee-tracker")

    total_fee, total_received, total_balance = repo.totals()

    return render_template(
        "fee_tracker.html",
        clients=repo.get_clients(),
        fees=repo.get_all_fees(),
        total_fee=total_fee,
        total_received=total_received,
        total_balance=total_balance
    )


# ---------------- CLIENT LEDGER ---------------- #

@app.route("/client-ledger")
def client_ledger():
    if not admin_or_user_required():
        return redirect("/")

    repo = ClientLedgerRepository()
    selected_client_id = request.args.get("client_id", "")

    ledger = []
    total_fee = 0
    total_received = 0
    total_balance = 0

    if selected_client_id:
        ledger = repo.get_ledger(selected_client_id)
        total_fee, total_received, total_balance = repo.get_summary(selected_client_id)

    return render_template(
        "client_ledger.html",
        clients=repo.get_clients(),
        selected_client_id=selected_client_id,
        ledger=ledger,
        total_fee=total_fee,
        total_received=total_received,
        total_balance=total_balance
    )


# ---------------- GST ---------------- #

@app.route("/gst-status", methods=["GET", "POST"])
def gst_status():
    if not admin_or_user_required():
        return redirect("/")

    repo = GSTRepository()

    if request.method == "POST":
        repo.add_gst_status(
            request.form["client_id"],
            request.form["financial_year"],
            request.form["month"],
            request.form["gstr1_status"],
            request.form["gstr3b_status"],
            request.form["arn"],
            request.form["filing_date"]
        )
        return redirect("/gst-status")

    search = request.args.get("search", "")
    gst_rows = repo.search_gst_status(search) if search else repo.get_all_gst_status()

    return render_template(
        "gst_status.html",
        clients=repo.get_clients(),
        gst_rows=gst_rows,
        search=search
    )


@app.route("/delete-gst/<int:gst_id>")
def delete_gst(gst_id):
    if not admin_or_user_required():
        return redirect("/")

    GSTRepository().delete_gst_status(gst_id)
    return redirect("/gst-status")


# ---------------- INVOICE ---------------- #

@app.route("/invoice-generator", methods=["GET", "POST"])
def invoice_generator():
    if not admin_or_user_required():
        return redirect("/")

    repo = InvoiceRepository()

    if request.method == "POST":
        repo.add_invoice(
            request.form["invoice_no"],
            request.form["invoice_date"],
            request.form["client_id"],
            request.form["description"],
            request.form["amount"],
            request.form["gst_rate"]
        )
        return redirect("/invoice-generator")

    return render_template(
        "invoice_generator.html",
        clients=repo.get_clients(),
        invoices=repo.get_all_invoices(),
        invoice_no=repo.next_invoice_no(),
        today=datetime.now().strftime("%d-%m-%Y")
    )


# ---------------- USER MANAGEMENT ADMIN ONLY ---------------- #

@app.route("/users")
def users():
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    return render_template("users.html", users=UserRepository().get_all_users())


@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    repo = UserRepository()

    if request.method == "POST":
        repo.add_user(
            request.form["username"],
            request.form["password"],
            request.form["role"]
        )
        return redirect("/users")

    return render_template("add_user.html")


@app.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    repo = UserRepository()

    if request.method == "POST":
        repo.update_user(
            user_id,
            request.form["username"],
            request.form["password"],
            request.form["role"]
        )
        return redirect("/users")

    return render_template("edit_user.html", user=repo.get_user_by_id(user_id))


@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    UserRepository().delete_user(user_id)
    return redirect("/users")


# ---------------- REPORTS / ADMIN MODULES ---------------- #

@app.route("/reports")
def reports():
    if not admin_or_user_required():
        return redirect("/")

    repo = ReportRepository()

    return render_template(
        "reports.html",
        summary=repo.summary(),
        outstanding_fees=repo.outstanding_fees(),
        gst_pending=repo.gst_pending(),
        invoice_report=repo.invoice_report()
    )


@app.route("/whatsapp-center")
def whatsapp_center():
    if not admin_or_user_required():
        return redirect("/")

    repo = WhatsAppRepository()

    return render_template(
        "whatsapp_center.html",
        gst_pending=repo.gst_pending_clients(),
        fee_pending=repo.fee_pending_clients()
    )


@app.route("/backup-center")
def backup_center():
    if not admin_or_user_required():
        return redirect("/")

    return render_template("backup_center.html")


@app.route("/download-db")
def download_db():
    if not admin_or_user_required():
        return redirect("/")

    db_path = "khansco.db"

    if not os.path.exists(db_path):
        return "<h2>Database file not found.</h2>"

    return send_file(
        db_path,
        as_attachment=True,
        download_name=f"khansco_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    )


@app.route("/export/<table_name>")
def export_table(table_name):
    if not admin_or_user_required():
        return redirect("/")

    allowed_tables = ["clients", "fee_tracker", "gst_status", "invoices", "users"]

    if table_name not in allowed_tables:
        return "<h2>Invalid export table.</h2>"

    os.makedirs("exports", exist_ok=True)

    file_path = os.path.join(
        "exports",
        f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    BackupRepository().export_table_to_csv(table_name, file_path)

    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))


@app.route("/import-clients", methods=["GET", "POST"])
def import_clients():
    if not admin_or_user_required():
        return redirect("/")

    message = ""

    if request.method == "POST":
        file = request.files["excel_file"]
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config["IMPORT_FOLDER"], filename)
        file.save(file_path)

        imported, updated = ImportRepository().import_clients_from_excel(file_path)
        message = f"Imported: {imported}, Updated: {updated}"

    return render_template("import_clients.html", message=message)


# ---------------- CLIENT AUTH ---------------- #

@app.route("/client-register", methods=["GET", "POST"])
def client_register():
    repo = ClientPortalRepository()

    if request.method == "POST":
        repo.register_client(
            request.form["client_name"],
            request.form["mobile"],
            request.form["email"],
            request.form["username"],
            request.form["password"],
            request.form.get("pan", "").upper(),
            request.form.get("gstin", "").upper()
        )
        return redirect("/client-login")

    return render_template("client_register.html")


@app.route("/client-login", methods=["GET", "POST"])
def client_login():
    repo = ClientPortalRepository()

    if request.method == "POST":
        client = repo.verify_client_login(
            request.form["username"],
            request.form["password"]
        )

        if client:
            session.clear()
            session["client_id"] = client[0]
            session["client_name"] = client[1]
            return redirect("/client-portal")

        return "<h2>Invalid Client Login</h2><a href='/client-login'>Try Again</a>"

    return render_template("client_login.html")



# ---------------- CLIENT FORGOT PASSWORD ---------------- #

@app.route("/client-forgot-password", methods=["GET", "POST"])
def client_forgot_password():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        PasswordResetRepository().create_request(username)
        message = "Password reset request submitted. Admin will reset your password."

    return render_template("client_forgot_password.html", message=message)






@app.route("/client-logout")
def client_logout():
    session.clear()
    return redirect("/client-login")


# ---------------- CLIENT PORTAL ONLY ---------------- #

@app.route("/client-portal")
def client_portal():
    if not client_required():
        return redirect("/client-login")

    portal_repo = ClientPortalRepository()
    status_repo = StatusRepository()

    return render_template(
        "client_portal.html",
        client_name=session["client_name"],
        documents=portal_repo.get_client_documents(session["client_id"]),
        progress=portal_repo.get_client_progress(session["client_id"]),
        status=status_repo.get_client_status(session["client_id"]),
        profile_photo=portal_repo.get_profile_photo(session["client_id"])
    )


@app.route("/client-profile")
def client_profile():
    if not client_required():
        return redirect("/client-login")

    profile_repo = ProfileRepository()
    portal_repo = ClientPortalRepository()

    return render_template(
        "client_profile.html",
        profile=profile_repo.get_client_profile(session["client_id"]),
        outstanding_fee=profile_repo.get_outstanding_fee(session["client_id"]),
        profile_photo=portal_repo.get_profile_photo(session["client_id"])
    )


@app.route("/client-profile-photo", methods=["GET", "POST"])
def client_profile_photo():
    if not client_required():
        return redirect("/client-login")

    repo = ClientPortalRepository()

    if request.method == "POST":
        file = request.files["profile_photo"]
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config["PROFILE_PHOTOS_FOLDER"], filename)
        file.save(file_path)

        repo.save_profile_photo(session["client_id"], filename)

        return redirect("/client-profile")

    return render_template("client_profile_photo.html")


@app.route("/profile-photos/<filename>")
def profile_photos(filename):
    return send_from_directory(app.config["PROFILE_PHOTOS_FOLDER"], filename)


@app.route("/upload-document", methods=["GET", "POST"])
def upload_document():
    if not client_required():
        return redirect("/client-login")

    repo = ClientPortalRepository()

    if request.method == "POST":
        file = request.files["document_file"]
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        repo.save_document(
            session["client_id"],
            request.form["document_name"],
            filename
        )

        return redirect("/client-portal")

    return render_template("upload_document.html")


@app.route("/client-tickets", methods=["GET", "POST"])
def client_tickets():
    if not client_required():
        return redirect("/client-login")

    repo = TicketRepository()

    if request.method == "POST":
        repo.create_ticket(
            session["client_id"],
            request.form["subject"],
            request.form["message"]
        )
        return redirect("/client-tickets")

    return render_template(
        "client_ticket.html",
        tickets=repo.get_client_tickets(session["client_id"])
    )


@app.route("/client-downloads")
def client_downloads():
    if not client_required():
        return redirect("/client-login")

    repo = FileCenterRepository()

    return render_template(
        "client_downloads.html",
        files=repo.get_client_files(session["client_id"])
    )


# ---------------- ADMIN DOCUMENTS / TICKETS / STATUS ---------------- #

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/admin-documents")
def admin_documents():
    if not admin_or_user_required():
        return redirect("/")

    return render_template(
        "admin_documents.html",
        documents=ClientPortalRepository().get_all_documents()
    )


@app.route("/work-progress", methods=["GET", "POST"])
def work_progress():
    if not admin_or_user_required():
        return redirect("/")

    repo = ClientPortalRepository()

    if request.method == "POST":
        repo.add_work_progress(
            request.form["client_id"],
            request.form["work_title"],
            request.form["status"],
            request.form["remarks"]
        )
        return redirect("/work-progress")

    return render_template("work_progress.html", clients=repo.get_clients())


@app.route("/notifications")
def notifications():
    if not admin_or_user_required():
        return redirect("/")

    return render_template(
        "notifications.html",
        notifications=ClientPortalRepository().get_notifications()
    )




# ---------------- ADMIN PASSWORD RESET REQUESTS ---------------- #
@app.route("/admin-password-requests")
def admin_password_requests():
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    return render_template(
        "admin_password_requests.html",
        requests=PasswordResetRepository().get_requests()
    )


@app.route("/approve-password-reset/<int:request_id>", methods=["POST"])
def approve_password_reset(request_id):
    if not admin_or_user_required():
        return redirect("/")

    if not admin_required():
        return access_denied()

    new_password = request.form["new_password"]
    PasswordResetRepository().approve_request(request_id, new_password)

    return redirect("/admin-password-requests")


@app.route("/mark-notification-read/<int:notification_id>")
def mark_notification_read(notification_id):
    if not admin_or_user_required():
        return redirect("/")

    ClientPortalRepository().mark_notification_read(notification_id)
    return redirect("/notifications")


@app.route("/admin-tickets")
def admin_tickets():
    if not admin_or_user_required():
        return redirect("/")

    return render_template(
        "admin_tickets.html",
        tickets=TicketRepository().get_all_tickets()
    )


@app.route("/update-ticket/<int:ticket_id>/<status>")
def update_ticket(ticket_id, status):
    if not admin_or_user_required():
        return redirect("/")

    TicketRepository().update_status(ticket_id, status)
    return redirect("/admin-tickets")


@app.route("/status-tracker", methods=["GET", "POST"])
def status_tracker():
    if not admin_or_user_required():
        return redirect("/")

    repo = StatusRepository()

    if request.method == "POST":
        repo.save_status(
            request.form["client_id"],
            request.form["gst_status"],
            request.form["income_tax_status"],
            request.form["tds_status"],
            request.form["audit_status"],
            request.form["roc_status"],
            request.form["remarks"]
        )

        return redirect("/status-tracker")

    return render_template(
        "status_tracker.html",
        clients=repo.get_clients(),
        status_rows=repo.get_all_status()
    )


@app.route("/file-center", methods=["GET", "POST"])
def file_center():
    if not admin_or_user_required():
        return redirect("/")

    repo = FileCenterRepository()

    if request.method == "POST":
        file = request.files["client_file"]
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config["CLIENT_FILES_FOLDER"], filename))

        repo.save_file(
            request.form["client_id"],
            request.form["file_title"],
            filename,
            request.form["file_type"]
        )

        return redirect("/file-center")

    return render_template(
        "file_center.html",
        clients=repo.get_clients(),
        files=repo.get_all_files()
    )


@app.route("/client-files/<filename>")
def client_files(filename):
    return send_from_directory(app.config["CLIENT_FILES_FOLDER"], filename)


# ---------------- START APP ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    app.run(debug=True, host="0.0.0.0", port=port)