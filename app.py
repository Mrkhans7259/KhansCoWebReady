from flask import Flask, render_template, request, redirect

from database.dashboard_repository import DashboardRepository
from database.client_repository import ClientRepository

app = Flask(__name__)
app.secret_key = "khansco_secret_key"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            return redirect("/dashboard")

        return "<h2>Invalid Login</h2><a href='/'>Try Again</a>"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    repo = DashboardRepository()

    return render_template(
        "dashboard.html",
        total_clients=repo.total_clients(),
        total_gst=repo.total_gst_records(),
        pending_gstr1=repo.pending_gstr1(),
        pending_gstr3b=repo.pending_gstr3b()
    )


@app.route("/clients")
def clients():

    repo = ClientRepository()

    search = request.args.get("search", "")

    if search:
        data = repo.search_clients(search)
    else:
        data = repo.get_all_clients()

    return render_template(
        "clients.html",
        clients=data,
        search=search
    )


@app.route("/add-client", methods=["GET", "POST"])
def add_client():
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

    client = repo.get_client_by_id(client_id)

    return render_template(
        "edit_client.html",
        client=client
    )


@app.route("/delete-client/<int:client_id>")
def delete_client(client_id):
    repo = ClientRepository()
    repo.delete_client(client_id)

    return redirect("/clients")


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5003
    )