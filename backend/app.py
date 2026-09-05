from flask import Flask, render_template, request, redirect, url_for, session

from web3 import Web3

from werkzeug.security import generate_password_hash, check_password_hash

import json
import os
import hashlib
from datetime import datetime


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
    Web3.HTTPProvider(
        GANACHE_URL,
        request_kwargs={"timeout": 3}
    )
)


# ============================================================
# DEPLOYED VOTING CONTRACT
# ============================================================

CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x0539A968714bc20C2946e6dC9Ff88fbE2826e93e"
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

        with open(
            USERS_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_users(users):

    with open(
        USERS_FILE,
        "w"
    ) as file:

        json.dump(
            users,
            file,
            indent=4
        )


# ============================================================
# VOTING HISTORY FILE
# ============================================================

VOTING_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "voting_history.json"
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

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Invalid request."
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

    if user_type not in [
        "Student",
        "Faculty"
    ]:

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
    # CHECK PHONE
    # ========================================================

    if phone in users:

        return {
            "success": False,
            "message":
            "An account with this phone number already exists."
        }


    # ========================================================
    # CHECK DUPLICATE NAME
    # ========================================================

    normalized_name = name.lower()

    for existing_user in users.values():

        existing_name = existing_user.get(
            "name",
            ""
        ).strip().lower()

        if existing_name == normalized_name:

            return {
                "success": False,
                "message":
                "An account with this name already exists."
            }


    # ========================================================
    # CHECK DUPLICATE REGISTRATION NUMBER
    # ========================================================

    if registration_number:

        normalized_reg = (
            registration_number
            .strip()
            .lower()
        )

        for existing_user in users.values():

            existing_reg = existing_user.get(
                "registration_number",
                ""
            ).strip().lower()

            if (
                existing_reg
                and existing_reg == normalized_reg
            ):

                return {
                    "success": False,
                    "message":
                    "An account with this registration number already exists."
                }


    # ========================================================
    # HASH PASSWORD
    # ========================================================

    password_hash = generate_password_hash(
        password
    )


    # ========================================================
    # SAVE USER
    # ========================================================

    users[phone] = {

        "user_type":
        user_type,

        "name":
        name,

        "registration_number":
        registration_number,

        "department":
        department,

        "phone":
        phone,

        "password":
        password_hash
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

@app.route(
    "/login",
    methods=["POST"]
)
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

    stored_hash = users[phone].get(
        "password",
        ""
    )

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
# FORGOT PASSWORD PAGE
# ============================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "GET":

        return render_template(
            "forgot_password.html"
        )


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

    new_password = data.get(
        "new_password",
        ""
    )


    if not phone.isdigit() or len(phone) != 10:

        return {
            "success": False,
            "message":
            "Please enter a valid 10-digit phone number."
        }


    if len(new_password) < 8:

        return {
            "success": False,
            "message":
            "Password must contain at least 8 characters."
        }


    if not any(
        char.isupper()
        for char in new_password
    ):

        return {
            "success": False,
            "message":
            "Password must contain an uppercase letter."
        }


    if not any(
        char.islower()
        for char in new_password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a lowercase letter."
        }


    if not any(
        char.isdigit()
        for char in new_password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a number."
        }


    if not any(
        char in "@#$%^&*! "
        for char in new_password
    ):

        return {
            "success": False,
            "message":
            "Password must contain a special character."
        }


    users = load_users()


    if phone not in users:

        return {
            "success": False,
            "message":
            "No account found with this phone number."
        }


    users[phone]["password"] = (
        generate_password_hash(
            new_password
        )
    )

    save_users(users)


    return {
        "success": True,
        "message":
        "Password reset successfully."
    }


# ============================================================
# ADMIN LOGIN PAGE
# ============================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
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


    if username != ADMIN_USERNAME:

        return {
            "success": False,
            "message":
            "Invalid admin username or password."
        }


    if not check_password_hash(
        ADMIN_PASSWORD_HASH,
        password
    ):

        return {
            "success": False,
            "message":
            "Invalid admin username or password."
        }


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

@app.route(
    "/vote",
    methods=["GET"]
)
def vote():

    if not session.get("logged_in"):

        return redirect(
            url_for("index")
        )


    if session.get("is_admin"):

        return redirect(
            url_for("admin")
        )


    return render_template(
        "vote.html"
    )


# ============================================================
# BLOCKCHAIN TRANSACTION HELPER
# ============================================================

def get_admin_account():

    if not web3.is_connected():

        raise Exception(
            "Ganache is not connected."
        )

    accounts = web3.eth.accounts

    if not accounts:

        raise Exception(
            "No Ganache account available."
        )

    return accounts[0]


# ============================================================
# SUBMIT VOTE WITHOUT METAMASK
# ============================================================

@app.route(
    "/submit-vote",
    methods=["POST"]
)
def submit_vote():

    if not session.get("logged_in"):

        return {
            "success": False,
            "message":
            "Please login before voting."
        }, 401


    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message":
                "Invalid vote request."
            }, 400


        election_id = int(
            data.get(
                "election_id"
            )
        )

        candidate_id = int(
            data.get(
                "candidate_id"
            )
        )


        # ====================================================
        # GET LOGGED-IN USER
        # ====================================================

        phone = session.get(
            "phone"
        )

        if not phone:

            return {
                "success": False,
                "message":
                "User session not found."
            }, 401


        users = load_users()

        if phone not in users:

            return {
                "success": False,
                "message":
                "User account not found."
            }, 401


        user = users[phone]


        # ====================================================
        # USER IDENTITY
        # ====================================================

        registration_number = (
            user.get(
                "registration_number",
                ""
            ).strip()
        )


        if registration_number:

            voter_identity = registration_number

        else:

            voter_identity = phone


        # ====================================================
        # CREATE BLOCKCHAIN VOTER ID
        # ====================================================

        voter_id = Web3.keccak(
            text=voter_identity
        )


        # ====================================================
        # CHECK VOTING STATUS
        # ====================================================

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


        if not started:

            return {
                "success": False,
                "message":
                "Voting has not started yet."
            }


        if ended:

            return {
                "success": False,
                "message":
                "Voting has ended."
            }


        # ====================================================
        # CHECK WHETHER USER ALREADY VOTED
        # ====================================================

        already_voted = (
            contract.functions
            .hasVoted(
                election_id,
                voter_id
            )
            .call()
        )


        if already_voted:

            return {
                "success": False,
                "message":
                "You have already voted in this election."
            }


        # ====================================================
        # VALIDATE CANDIDATE
        # ====================================================

        candidates = (
            contract.functions
            .getAllCandidates(
                election_id
            )
            .call()
        )


        if (
            candidate_id < 1
            or candidate_id > len(candidates)
        ):

            return {
                "success": False,
                "message":
                "Invalid candidate."
            }, 400


        candidate_name = (
            candidates[candidate_id - 1][1]
        )


        # ====================================================
        # BLOCKCHAIN ACCOUNT
        # ====================================================

        account = get_admin_account()


        # ====================================================
        # SUBMIT BLOCKCHAIN VOTE
        # ====================================================

        transaction = (
            contract.functions
            .vote(
                election_id,
                candidate_id,
                voter_id
            )
            .transact({
                "from":
                account
            })
        )


        # ====================================================
        # WAIT FOR CONFIRMATION
        # ====================================================

        receipt = (
            web3.eth
            .wait_for_transaction_receipt(
                transaction
            )
        )


        transaction_hash = (
            receipt.transactionHash.hex()
        )


        # ====================================================
        # SAVE VOTING HISTORY
        # ====================================================

        history = []


        if os.path.exists(
            VOTING_HISTORY_FILE
        ):

            try:

                with open(
                    VOTING_HISTORY_FILE,
                    "r"
                ) as file:

                    history = json.load(
                        file
                    )

            except Exception:

                history = []


        history.append({

            "election_id":
            election_id,

            "candidate_id":
            candidate_id,

            "candidate_name":
            candidate_name,

            "transaction_hash":
            transaction_hash,

            "phone":
            phone,

            "timestamp":
            datetime.now().isoformat()
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


        # ====================================================
        # SUCCESS
        # ====================================================

        return {

            "success":
            True,

            "message":
            "Vote successfully recorded on blockchain.",

            "candidate_name":
            candidate_name,

            "transaction_hash":
            transaction_hash
        }


    except Exception as e:

        print(
            "Submit vote error:",
            e
        )


        return {

            "success":
            False,

            "message":
            str(e)

        }, 500


# ============================================================
# ADD CANDIDATE
# ============================================================

@app.route(
    "/admin/add-candidate",
    methods=["POST"]
)
def add_candidate():

    if not session.get("admin_logged_in"):

        return {
            "success": False,
            "message":
            "Admin login required."
        }, 401


    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message":
                "Invalid request."
            }, 400


        election_id = int(
            data.get(
                "election_id"
            )
        )

        candidate_name = data.get(
            "name",
            ""
        ).strip()

        candidate_symbol = data.get(
            "symbol",
            ""
        ).strip()


        if not candidate_name:

            return {
                "success": False,
                "message":
                "Candidate name is required."
            }, 400


        if not candidate_symbol:

            return {
                "success": False,
                "message":
                "Candidate symbol is required."
            }, 400


        account = get_admin_account()


        transaction = (
            contract.functions
            .addCandidate(
                election_id,
                candidate_name,
                candidate_symbol
            )
            .transact({
                "from":
                account
            })
        )


        receipt = (
            web3.eth
            .wait_for_transaction_receipt(
                transaction
            )
        )


        return {

            "success":
            True,

            "message":
            "Candidate added successfully.",

            "transaction_hash":
            receipt.transactionHash.hex()
        }


    except Exception as e:

        print(
            "Add candidate error:",
            e
        )


        return {

            "success":
            False,

            "message":
            str(e)

        }, 500


# ============================================================
# START VOTING
# ============================================================

@app.route(
    "/admin/start-voting",
    methods=["POST"]
)
def start_voting():

    if not session.get("admin_logged_in"):

        return {
            "success": False,
            "message":
            "Admin login required."
        }, 401


    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message":
                "Invalid request."
            }, 400


        election_id = int(
            data.get(
                "election_id"
            )
        )


        candidates = (
            contract.functions
            .getAllCandidates(
                election_id
            )
            .call()
        )


        if len(candidates) == 0:

            return {

                "success":
                False,

                "message":
                "Add candidates first."
            }, 400


        account = get_admin_account()


        transaction = (
            contract.functions
            .startVoting(
                election_id
            )
            .transact({
                "from":
                account
            })
        )


        receipt = (
            web3.eth
            .wait_for_transaction_receipt(
                transaction
            )
        )


        return {

            "success":
            True,

            "message":
            "Voting started successfully.",

            "transaction_hash":
            receipt.transactionHash.hex()
        }


    except Exception as e:

        print(
            "Start voting error:",
            e
        )


        return {

            "success":
            False,

            "message":
            str(e)

        }, 500


# ============================================================
# END VOTING
# ============================================================

@app.route(
    "/admin/end-voting",
    methods=["POST"]
)
def end_voting():

    if not session.get("admin_logged_in"):

        return {
            "success": False,
            "message":
            "Admin login required."
        }, 401


    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message":
                "Invalid request."
            }, 400


        election_id = int(
            data.get(
                "election_id"
            )
        )


        account = get_admin_account()


        transaction = (
            contract.functions
            .endVoting(
                election_id
            )
            .transact({
                "from":
                account
            })
        )


        receipt = (
            web3.eth
            .wait_for_transaction_receipt(
                transaction
            )
        )


        return {

            "success":
            True,

            "message":
            "Voting ended successfully.",

            "transaction_hash":
            receipt.transactionHash.hex()
        }


    except Exception as e:

        print(
            "End voting error:",
            e
        )


        return {

            "success":
            False,

            "message":
            str(e)

        }, 500


# ============================================================
# ADMIN PAGE
# ============================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    voting_history = []


    if os.path.exists(
        VOTING_HISTORY_FILE
    ):

        try:

            with open(
                VOTING_HISTORY_FILE,
                "r"
            ) as file:

                voting_history = json.load(
                    file
                )

        except Exception as e:

            print(
                "Voting history error:",
                e
            )

            voting_history = []


    users = load_users()


    elections = [

        {
            "id": 1,
            "name":
            "Student Council President",
            "started": False,
            "ended": False,
            "candidates": []
        },

        {
            "id": 2,
            "name":
            "Sports Secretary",
            "started": False,
            "ended": False,
            "candidates": []
        },

        {
            "id": 3,
            "name":
            "Academic Secretary",
            "started": False,
            "ended": False,
            "candidates": []
        }
    ]


    blockchain_connected = False


    try:

        if web3.is_connected():

            blockchain_connected = True


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


                elections[
                    election_id - 1
                ] = {

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
                }


    except Exception as e:

        print(
            "Blockchain connection failed:",
            e
        )

        blockchain_connected = False


    return render_template(
        "admin.html",
        elections=elections,
        users=users,
        voting_history=voting_history,
        blockchain_connected=
        blockchain_connected
    )


# ============================================================
# RESULTS PAGE
# ============================================================

@app.route("/results")
def results():

    elections = []


    default_names = {

        1:
        "Student Council President",

        2:
        "Sports Secretary",

        3:
        "Academic Secretary"
    }


    try:

        if web3.is_connected():

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


                for candidate in candidates:

                    vote_count = int(
                        candidate[3]
                    )

                    total_votes += vote_count


                elections.append({

                    "id":
                    election_id,

                    "name":
                    election_name,

                    "candidates":
                    candidates,

                    "total_votes":
                    total_votes
                })


        else:

            raise Exception(
                "Ganache is not connected."
            )


    except Exception as e:

        print(
            "Results blockchain error:",
            e
        )


        elections = []


        for election_id in range(1, 4):

            elections.append({

                "id":
                election_id,

                "name":
                default_names[
                    election_id
                ],

                "candidates":
                [],

                "total_votes":
                0
            })


    return render_template(
        "result.html",
        elections=elections
    )


# ============================================================
# SAVE VOTING HISTORY
# ============================================================

@app.route(
    "/save-vote-history",
    methods=["POST"]
)
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

                    history = json.load(
                        file
                    )

            except Exception:

                history = []


        history.append({

            "election_id":
            data.get(
                "election_id"
            ),

            "candidate_id":
            data.get(
                "candidate_id"
            ),

            "candidate_name":
            data.get(
                "candidate_name"
            ),

            "transaction_hash":
            data.get(
                "transaction_hash"
            ),

            "timestamp":
            datetime.now().isoformat()
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

            "success":
            True,

            "message":
            "Voting history saved successfully."
        }


    except Exception as e:

        print(
            "Voting history error:",
            e
        )


        return {

            "success":
            False,

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

    try:

        if not web3.is_connected():

            print(
                "WARNING: Ganache connection failed!"
            )

        else:

            print(
                "Connected to Ganache successfully!"
            )

    except Exception as e:

        print(
            "Ganache check error:",
            e
        )


    print(
        "Voting Contract:",
        CONTRACT_ADDRESS
    )


    app.run(
        debug=True,
        port=5000
    )