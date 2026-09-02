from flask import Flask, render_template, request, redirect, url_for, session

from web3 import Web3

from werkzeug.security import generate_password_hash, check_password_hash

import json

import os


app = Flask(
    __name__,
    static_folder="../static",
    static_url_path="/static"
)

app.secret_key = "blockchain-voting-secret-key"


# ============================================================
# GANACHE CONNECTION
# ============================================================

GANACHE_URL = "http://127.0.0.1:7545"

web3 = Web3(
    Web3.HTTPProvider(GANACHE_URL)
)


# ============================================================
# DEPLOYED VOTING CONTRACT
# ============================================================

CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x9A9141aA574561eb6E0121a42E247D0b5e2A2f4d"
)


# ============================================================
# CONTRACT ABI
# ============================================================

ABI_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "artifacts",
    "contracts",
    "Voting.sol",
    "Voting.json"
)

with open(ABI_PATH, "r") as file:

    contract_data = json.load(file)

contract = web3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=contract_data["abi"]
)


# ============================================================
# USER DATA FILE
# ============================================================

USERS_FILE = os.path.join(
    os.path.dirname(__file__),
    "users.json"
)


def load_users():

    if not os.path.exists(USERS_FILE):
        return {}

    try:

        with open(USERS_FILE, "r") as file:
            return json.load(file)

    except Exception:

        return {}


def save_users(users):

    with open(USERS_FILE, "w") as file:

        json.dump(
            users,
            file,
            indent=4
        )


# ============================================================
# ADMIN LOGIN DETAILS
# ============================================================

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD_HASH = generate_password_hash(
    "Admin@123"
)


# ============================================================
# HOME / LOGIN PAGE
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# REGISTER PAGE
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message":
            "Invalid request."
        }

    # ========================================================
    # USER DETAILS
    # ========================================================

    user_type = data.get(
        "user_type",
        ""
    ).strip()

    name = data.get(
        "name",
        ""
    ).strip()

    registration_number = data.get(
        "registration_number",
        ""
    ).strip()

    department = data.get(
        "department",
        ""
    ).strip()

    phone = data.get(
        "phone",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    # ========================================================
    # USER TYPE VALIDATION
    # ========================================================

    if user_type not in ["Student", "Faculty"]:

        return {
            "success": False,
            "message":
            "Please select Student or Faculty."
        }

    # ========================================================
    # NAME VALIDATION
    # ========================================================

    if not name:

        return {
            "success": False,
            "message":
            "Please enter your name."
        }

    # ========================================================
    # DEPARTMENT VALIDATION
    # ========================================================

    if not department:

        return {
            "success": False,
            "message":
            "Please enter your department."
        }

    # ========================================================
    # REGISTRATION NUMBER
    # REQUIRED ONLY FOR STUDENT
    # ========================================================

    if user_type == "Student":

        if not registration_number:

            return {
                "success": False,
                "message":
                "Registration number is required for students."
            }

    else:

        registration_number = ""

    # ========================================================
    # PHONE VALIDATION
    # ========================================================

    if not phone.isdigit() or len(phone) != 10:

        return {
            "success": False,
            "message":
            "Please enter a valid 10-digit phone number."
        }

    # ========================================================
    # PASSWORD VALIDATION
    # ========================================================

    if len(password) < 8:

        return {
            "success": False,
            "message":
            "Password must contain at least 8 characters."
        }

    if not any(
        char.isupper()
        for char in password
    ):

        return {
            "success": False,
            "message":
            "Password must contain an uppercase letter."
        }

    if not any(
        char.islower()
        for char in password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a lowercase letter."
        }

    if not any(
        char.isdigit()
        for char in password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a number."
        }

    if not any(
        char in "@#$%^&*!"
        for char in password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a special character."
        }

    # ========================================================
    # LOAD USERS
    # ========================================================

    users = load_users()

    # ========================================================
    # CHECK EXISTING PHONE
    # ========================================================

    if phone in users:

        return {
            "success": False,
            "message":
            "An account with this phone number already exists."
        }

    # ========================================================
    # HASH PASSWORD
    # ========================================================

    password_hash = generate_password_hash(
        password
    )

    # ========================================================
    # SAVE USER DETAILS
    # ========================================================

    users[phone] = {

        "user_type": user_type,

        "name": name,

        "registration_number":
        registration_number,

        "department": department,

        "phone": phone,

        "password": password_hash
    }

    save_users(users)

    return {
        "success": True,
        "message":
        "Account created successfully."
    }


# ============================================================
# USER LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message":
            "Invalid request."
        }

    phone = data.get(
        "phone",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    # ========================================================
    # PHONE VALIDATION
    # ========================================================

    if not phone.isdigit() or len(phone) != 10:

        return {
            "success": False,
            "message":
            "Please enter a valid 10-digit phone number."
        }

    # ========================================================
    # LOAD USERS
    # ========================================================

    users = load_users()

    # ========================================================
    # CHECK USER
    # ========================================================

    if phone not in users:

        return {
            "success": False,
            "message":
            "Account not found. Please create an account first."
        }

    # ========================================================
    # CHECK PASSWORD
    # ========================================================

    stored_hash = users[phone]["password"]

    if not check_password_hash(
        stored_hash,
        password
    ):

        return {
            "success": False,
            "message":
            "Incorrect password."
        }

    # ========================================================
    # USER LOGIN SUCCESS
    # ========================================================

    session.clear()

    session["logged_in"] = True

    session["phone"] = phone

    session["is_admin"] = False

    return {
        "success": True,
        "message":
        "Login successful."
    }


# ============================================================
# ADMIN LOGIN PAGE
# ============================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":

        return render_template(
            "admin_login.html"
        )

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message":
            "Invalid request."
        }

    username = data.get(
        "username",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    # ========================================================
    # ADMIN USERNAME CHECK
    # ========================================================

    if username != ADMIN_USERNAME:

        return {
            "success": False,
            "message":
            "Invalid admin username or password."
        }

    # ========================================================
    # ADMIN PASSWORD CHECK
    # ========================================================

    if not check_password_hash(
        ADMIN_PASSWORD_HASH,
        password
    ):

        return {
            "success": False,
            "message":
            "Invalid admin username or password."
        }

    # ========================================================
    # ADMIN LOGIN SUCCESS
    # ========================================================

    session.clear()

    session["admin_logged_in"] = True

    session["is_admin"] = True

    return {
        "success": True,
        "message":
        "Admin login successful."
    }


# ============================================================
# VOTING PAGE
# ============================================================

@app.route("/vote", methods=["GET"])
def vote():

    # ========================================================
    # CHECK USER LOGIN
    # ========================================================

    if not session.get("logged_in"):

        return redirect(
            url_for("index")
        )

    # ========================================================
    # ADMIN SHOULD NOT USE USER VOTING PAGE
    # ========================================================

    if session.get("is_admin"):

        return redirect(
            url_for("admin")
        )

    # ========================================================
    # SHOW VOTING PAGE
    # ========================================================

    return render_template(
        "vote.html"
    )


# ============================================================
# ADMIN PAGE
# ============================================================

@app.route("/admin")
def admin():

    # ========================================================
    # ADMIN AUTHENTICATION
    # ========================================================

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )

    try:

        elections = []

        # ====================================================
        # LOAD VOTING HISTORY
        # ====================================================

        voting_history = []

        if os.path.exists(
            VOTING_HISTORY_FILE
        ):

            try:

                with open(
                    VOTING_HISTORY_FILE,
                    "r"
                ) as file:

                    voting_history = json.load(file)

            except Exception:

                voting_history = []

        # ====================================================
        # LOAD ELECTION DATA
        # ====================================================

        for election_id in range(1, 4):

            election_name = (
                contract.functions
                .getElectionName(
                    election_id
                )
                .call()
            )

            started = (
                contract.functions
                .isVotingStarted(
                    election_id
                )
                .call()
            )

            ended = (
                contract.functions
                .isVotingEnded(
                    election_id
                )
                .call()
            )

            candidates = (
                contract.functions
                .getAllCandidates(
                    election_id
                )
                .call()
            )

            elections.append({

                "id":
                election_id,

                "name":
                election_name,

                "started":
                started,

                "ended":
                ended,

                "candidates":
                candidates
            })

        # ====================================================
        # LOAD REGISTERED USERS
        # ====================================================

        users = load_users()

        return render_template(
            "admin.html",
            elections=elections,
            users=users,
            voting_history=voting_history
        )

    except Exception as e:

        return f"Blockchain connection error: {e}"


# ============================================================
# RESULTS PAGE
# ============================================================

@app.route("/results")
def results():

    try:

        elections = []

        for election_id in range(1, 4):

            election_name = (
                contract.functions
                .getElectionName(
                    election_id
                )
                .call()
            )

            candidates = (
                contract.functions
                .getAllCandidates(
                    election_id
                )
                .call()
            )

            total_votes = 0

            winner = None

            # =================================================
            # WINNER FIX
            # Winner remains None when all votes are 0.
            # =================================================

            highest_votes = 0

            for candidate in candidates:

                vote_count = int(
                    candidate[2]
                )

                total_votes += vote_count

                if vote_count > highest_votes:

                    highest_votes = vote_count

                    winner = candidate

            elections.append({

                "id":
                election_id,

                "name":
                election_name,

                "candidates":
                candidates,

                "total_votes":
                total_votes,

                "winner":
                winner
            })

        return render_template(
            "result.html",
            elections=elections
        )

    except Exception as e:

        return f"Blockchain connection error: {e}"


# ============================================================
# SAVE VOTING HISTORY
# ============================================================

VOTING_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "voting_history.json"
)


@app.route("/save-vote-history", methods=["POST"])
def save_vote_history():

    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message":
                "Invalid voting history data."
            }, 400

        history = []

        if os.path.exists(
            VOTING_HISTORY_FILE
        ):

            try:

                with open(
                    VOTING_HISTORY_FILE,
                    "r"
                ) as file:

                    history = json.load(file)

            except Exception:

                history = []

        history.append({

            "election_id":
            data.get("election_id"),

            "candidate_id":
            data.get("candidate_id"),

            "candidate_name":
            data.get("candidate_name"),

            "transaction_hash":
            data.get("transaction_hash"),

            "timestamp":
            __import__("datetime").datetime.now().isoformat()
        })

        with open(
            VOTING_HISTORY_FILE,
            "w"
        ) as file:

            json.dump(
                history,
                file,
                indent=4
            )

        return {
            "success": True,
            "message":
            "Voting history saved successfully."
        }

    except Exception as e:

        print(
            "Voting history error:",
            e
        )

        return {
            "success": False,
            "message":
            "Failed to save voting history."
        }, 500


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin-logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# USER LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    if not web3.is_connected():

        print(
            "WARNING: Ganache connection failed!"
        )

    else:

        print(
            "Connected to Ganache successfully!"
        )

    print(
        "Voting Contract:",
        CONTRACT_ADDRESS
    )

    app.run(
        debug=True,
        port=5000
    )