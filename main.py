# ============================================================
# ZaRion Bank Management System
# ============================================================
#
# This is the Streamlit version of the original ZaRion
# Bank Management System.
#
# Main technologies:
#   - Python
#   - Streamlit
#   - SQLite
#   - Pandas
#
# Main features:
#   - Create bank account
#   - Login with account number and PIN
#   - Deposit money
#   - Withdraw money
#   - View account details
#   - Update account information
#   - View transaction history
#   - Delete account
#
# IMPORTANT:
# This is an educational portfolio project.
# It is NOT real production banking software.
# ============================================================


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

import hashlib
import hmac
import secrets
import sqlite3

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# 2. APPLICATION SETTINGS
# ============================================================
#
# Keeping important settings in one place makes the application
# easier to maintain.
# ============================================================

APP_NAME = "ZaRion Bank Management System"

# SQLite database file.
# SQLite will create this file automatically if it does not exist.
DB_PATH = Path("zarion_bank.db")

# Minimum age required to create an account.
MIN_AGE = 18

# Maximum amount allowed in one deposit transaction.
MAX_DEPOSIT = Decimal("50000.00")

# PIN must contain exactly four digits.
PIN_LENGTH = 4


# ============================================================
# 3. DATABASE CONNECTION
# ============================================================

@contextmanager
def get_connection():
    """
    Open a connection to the SQLite database.

    Why this function exists:
    Instead of opening and closing the database connection
    manually in every function, we use one common function.

    The connection is automatically closed after the database
    operation is finished.
    """

    # Open the SQLite database.
    connection = sqlite3.connect(DB_PATH)

    # sqlite3.Row allows us to access database columns by name.
    #
    # Example:
    # row["user_name"]
    #
    # instead of:
    # row[2]
    connection.row_factory = sqlite3.Row

    try:
        # Give the connection to the calling function.
        yield connection

        # Save successful changes.
        connection.commit()

    except Exception:
        # If something goes wrong, undo the unfinished changes.
        connection.rollback()

        # Send the original error back to the caller.
        raise

    finally:
        # Always close the database connection.
        connection.close()


# ============================================================
# 4. CREATE DATABASE TABLES
# ============================================================

def init_database():
    """
    Create the required database tables if they do not exist.

    We use two tables:

    1. accounts
       Stores customer account information.

    2. transactions
       Stores deposit and withdrawal history.
    """

    with get_connection() as connection:

        # ----------------------------------------------------
        # ACCOUNTS TABLE
        # ----------------------------------------------------
        #
        # This table stores the main account information.
        # ----------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                account_number TEXT UNIQUE NOT NULL,

                user_name TEXT NOT NULL,

                email TEXT UNIQUE NOT NULL,

                pin_hash TEXT NOT NULL,

                pin_salt TEXT NOT NULL,

                age INTEGER NOT NULL CHECK(age >= 18),

                gender TEXT NOT NULL,

                balance_cents INTEGER NOT NULL DEFAULT 0
                    CHECK(balance_cents >= 0),

                created_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # TRANSACTIONS TABLE
        # ----------------------------------------------------
        #
        # Every deposit and withdrawal is saved here.
        # This gives us a simple transaction history.
        # ----------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                account_number TEXT NOT NULL,

                transaction_type TEXT NOT NULL,

                amount_cents INTEGER NOT NULL
                    CHECK(amount_cents > 0),

                balance_after_cents INTEGER NOT NULL
                    CHECK(balance_after_cents >= 0),

                created_at TEXT NOT NULL,

                FOREIGN KEY(account_number)
                    REFERENCES accounts(account_number)
            )
            """
        )


# ============================================================
# 5. PIN SECURITY
# ============================================================

def hash_pin(pin: str, salt_hex: str | None = None):
    """
    Convert a PIN into a secure hash.

    We should never store the original PIN directly
    inside the database.

    A random salt is added before hashing.

    If salt_hex is provided, it means we are checking
    an existing PIN and must use the original salt.
    """

    # Use an existing salt when verifying a PIN.
    #
    # Otherwise create a new random 16-byte salt.
    if salt_hex:
        salt = bytes.fromhex(salt_hex)
    else:
        salt = secrets.token_bytes(16)

    # PBKDF2 repeatedly processes the PIN.
    #
    # This makes guessing the original PIN more expensive
    # than using a simple hash function once.
    derived_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        120_000,
    )

    # Convert binary values into hexadecimal text.
    # This makes them easy to store in SQLite.
    return derived_hash.hex(), salt.hex()


def verify_pin(
    pin: str,
    stored_hash: str,
    stored_salt: str,
) -> bool:
    """
    Check whether the entered PIN matches the stored PIN hash.
    """

    # Create a hash from the entered PIN using the
    # original stored salt.
    candidate_hash, _ = hash_pin(
        pin,
        stored_salt,
    )

    # compare_digest is used instead of normal == comparison
    # for safer hash comparison.
    return hmac.compare_digest(
        candidate_hash,
        stored_hash,
    )


# ============================================================
# 6. ACCOUNT NUMBER GENERATOR
# ============================================================

def generate_account_number() -> str:
    """
    Generate a unique 10-digit account number.

    We use the secrets module because it is designed for
    security-sensitive random values.
    """

    while True:

        # Generate ten random digits.
        account_number = "".join(
            secrets.choice("0123456789")
            for _ in range(10)
        )

        # Check whether this number already exists.
        with get_connection() as connection:

            existing_account = connection.execute(
                """
                SELECT 1
                FROM accounts
                WHERE account_number = ?
                """,
                (account_number,),
            ).fetchone()

        # If the number does not exist, it is safe to use.
        if not existing_account:
            return account_number


# ============================================================
# 7. MONEY HELPER FUNCTIONS
# ============================================================

def money_to_cents(value) -> int:
    """
    Convert money into integer cents.

    Example:
        100.50 dollars
        becomes
        10050 cents

    Why:
    Storing money as floating-point numbers can cause
    precision problems.

    Integer cents are easier to calculate safely.
    """

    amount = Decimal(str(value)).quantize(
        Decimal("0.01")
    )

    return int(amount * 100)


def cents_to_money(cents: int) -> Decimal:
    """
    Convert integer cents back into money.

    Example:
        10050 cents
        becomes
        100.50
    """

    return Decimal(cents) / Decimal(100)


def format_money(cents: int) -> str:
    """
    Convert cents into a user-friendly money string.

    Example:
        150000 cents
        becomes
        $1,500.00
    """

    return f"${cents_to_money(cents):,.2f}"


# ============================================================
# 8. VALIDATION HELPERS
# ============================================================

def valid_email(email: str) -> bool:
    """
    Perform a simple email validation.

    This is intentionally simple because this is an
    educational project, not a production email system.
    """

    return (
        "@" in email
        and "." in email.rsplit("@", 1)[-1]
    )


def account_to_dict(row):
    """
    Convert a SQLite Row into a normal Python dictionary.

    This makes account information easier to use
    throughout the Streamlit application.
    """

    if row is None:
        return None

    return dict(row)


# ============================================================
# 9. LOGIN / AUTHENTICATION
# ============================================================

def authenticate(
    account_number: str,
    pin: str,
):
    """
    Check account number and PIN.

    Returns:
        Account dictionary if login is successful.
        None if login fails.
    """

    account_number = account_number.strip()
    pin = pin.strip()

    # Basic validation before accessing the database.
    if not account_number:
        return None

    if not pin.isdigit():
        return None

    # Find the account using its account number.
    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE account_number = ?
            """,
            (account_number,),
        ).fetchone()

    # Check the entered PIN against the stored hash.
    if row and verify_pin(
        pin,
        row["pin_hash"],
        row["pin_salt"],
    ):
        return account_to_dict(row)

    return None


# ============================================================
# 10. TRANSACTION HISTORY HELPER
# ============================================================

def add_transaction(
    connection,
    account_number,
    transaction_type,
    amount_cents,
    balance_after,
):
    """
    Save one transaction in the transactions table.

    This function does not create a new database connection.
    It receives the existing connection from the deposit or
    withdrawal function.

    This helps keep the account balance update and transaction
    record inside the same database operation.
    """

    connection.execute(
        """
        INSERT INTO transactions
        (
            account_number,
            transaction_type,
            amount_cents,
            balance_after_cents,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account_number,
            transaction_type,
            amount_cents,
            balance_after,
            datetime.now().isoformat(
                timespec="seconds"
            ),
        ),
    )


# ============================================================
# 11. REFRESH LOGGED-IN ACCOUNT
# ============================================================

def refresh_logged_in_account():
    """
    Load the latest account information from SQLite.

    This is important because the account balance can change
    after a deposit or withdrawal.

    Session State stores the current login information while
    the Streamlit session is active.
    """

    # If there is no account number in the session,
    # there is no logged-in account to refresh.
    if "account_number" not in st.session_state:
        return

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE account_number = ?
            """,
            (st.session_state.account_number,),
        ).fetchone()

    if row:
        st.session_state.account = account_to_dict(row)
    else:
        st.session_state.account = None


# ============================================================
# 12. CREATE ACCOUNT
# ============================================================

def create_account(
    name,
    email,
    pin,
    age,
    gender,
):
    """
    Create a new bank account.

    Returns:
        (True, success message, account number)

    or

        (False, error message, None)
    """

    # Clean user input.
    name = name.strip()
    email = email.strip().lower()
    pin = pin.strip()
    gender = gender.strip().capitalize()

    # ---------------- VALIDATION ----------------

    if not name:
        return False, "Name is required.", None

    if not valid_email(email):
        return False, "Please enter a valid email address.", None

    if not pin.isdigit() or len(pin) != PIN_LENGTH:
        return False, "PIN must be exactly 4 digits.", None

    if age < MIN_AGE:
        return False, "You must be at least 18 years old.", None

    if not gender:
        return False, "Gender is required.", None

    # Generate a unique account number.
    account_number = generate_account_number()

    # Never save the original PIN.
    # Save only its hash and salt.
    pin_hash, pin_salt = hash_pin(pin)

    try:

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO accounts
                (
                    account_number,
                    user_name,
                    email,
                    pin_hash,
                    pin_salt,
                    age,
                    gender,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_number,
                    name.upper(),
                    email,
                    pin_hash,
                    pin_salt,
                    age,
                    gender,
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),
                ),
            )

        return (
            True,
            "Account created successfully.",
            account_number,
        )

    except sqlite3.IntegrityError:

        # UNIQUE constraints can cause this error,
        # for example when the email already exists.
        return (
            False,
            "This email is already registered.",
            None,
        )


# ============================================================
# 13. DEPOSIT MONEY
# ============================================================

def deposit(
    account_number,
    amount,
):
    """
    Add money to an existing account.

    The function:
        1. Validates the amount.
        2. Finds the account.
        3. Calculates the new balance.
        4. Updates the account.
        5. Saves the transaction.
    """

    try:

        amount_decimal = Decimal(
            str(amount)
        ).quantize(
            Decimal("0.01")
        )

    except (InvalidOperation, ValueError):

        return False, "Invalid amount."

    # Deposit must be greater than zero.
    if amount_decimal <= 0:
        return (
            False,
            "Deposit amount must be greater than zero.",
        )

    # Prevent extremely large single deposits.
    if amount_decimal > MAX_DEPOSIT:
        return (
            False,
            (
                "Maximum deposit per transaction is "
                f"{format_money(money_to_cents(MAX_DEPOSIT))}."
            ),
        )

    amount_cents = money_to_cents(
        amount_decimal
    )

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT balance_cents
            FROM accounts
            WHERE account_number = ?
            """,
            (account_number,),
        ).fetchone()

        if not row:
            return False, "Account not found."

        # Add the deposit to the existing balance.
        new_balance = (
            row["balance_cents"]
            + amount_cents
        )

        # Update account balance.
        connection.execute(
            """
            UPDATE accounts
            SET balance_cents = ?
            WHERE account_number = ?
            """,
            (
                new_balance,
                account_number,
            ),
        )

        # Save the transaction history.
        add_transaction(
            connection,
            account_number,
            "DEPOSIT",
            amount_cents,
            new_balance,
        )

    return (
        True,
        (
            "Deposit successful. "
            f"New balance: {format_money(new_balance)}"
        ),
    )


# ============================================================
# 14. WITHDRAW MONEY
# ============================================================

def withdraw(
    account_number,
    amount,
):
    """
    Remove money from an existing account.

    Withdrawal is allowed only when the account has
    enough balance.
    """

    try:

        amount_decimal = Decimal(
            str(amount)
        ).quantize(
            Decimal("0.01")
        )

    except (InvalidOperation, ValueError):

        return False, "Invalid amount."

    if amount_decimal <= 0:
        return (
            False,
            "Withdrawal amount must be greater than zero.",
        )

    amount_cents = money_to_cents(
        amount_decimal
    )

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT balance_cents
            FROM accounts
            WHERE account_number = ?
            """,
            (account_number,),
        ).fetchone()

        if not row:
            return False, "Account not found."

        # Do not allow the balance to become negative.
        if amount_cents > row["balance_cents"]:
            return (
                False,
                (
                    "Insufficient balance. "
                    f"Current balance: "
                    f"{format_money(row['balance_cents'])}"
                ),
            )

        # Subtract the withdrawal amount.
        new_balance = (
            row["balance_cents"]
            - amount_cents
        )

        # Save the new balance.
        connection.execute(
            """
            UPDATE accounts
            SET balance_cents = ?
            WHERE account_number = ?
            """,
            (
                new_balance,
                account_number,
            ),
        )

        # Save the withdrawal in transaction history.
        add_transaction(
            connection,
            account_number,
            "WITHDRAW",
            amount_cents,
            new_balance,
        )

    return (
        True,
        (
            "Withdrawal successful. "
            f"New balance: {format_money(new_balance)}"
        ),
    )


# ============================================================
# 15. UPDATE ACCOUNT
# ============================================================

def update_account(
    account_number,
    new_name,
    new_email,
    new_pin,
):
    """
    Update account information.

    Empty fields are ignored.

    The user can update:
        - Name
        - Email
        - PIN
    """

    updates = []
    parameters = []

    # ---------------- NAME ----------------

    if new_name.strip():

        updates.append(
            "user_name = ?"
        )

        parameters.append(
            new_name.strip().upper()
        )

    # ---------------- EMAIL ----------------

    if new_email.strip():

        email = new_email.strip().lower()

        if not valid_email(email):
            return (
                False,
                "Please enter a valid email address.",
            )

        updates.append(
            "email = ?"
        )

        parameters.append(email)

    # ---------------- PIN ----------------

    if new_pin.strip():

        if (
            not new_pin.isdigit()
            or len(new_pin) != PIN_LENGTH
        ):
            return (
                False,
                "New PIN must be exactly 4 digits.",
            )

        # Hash the new PIN instead of storing it directly.
        pin_hash, pin_salt = hash_pin(
            new_pin.strip()
        )

        updates.extend(
            [
                "pin_hash = ?",
                "pin_salt = ?",
            ]
        )

        parameters.extend(
            [
                pin_hash,
                pin_salt,
            ]
        )

    # Nothing was changed.
    if not updates:
        return True, "No changes were made."

    # Account number is used to find the correct account.
    parameters.append(account_number)

    try:

        with get_connection() as connection:

            connection.execute(
                f"""
                UPDATE accounts
                SET {", ".join(updates)}
                WHERE account_number = ?
                """,
                parameters,
            )

        return (
            True,
            "Account details updated successfully.",
        )

    except sqlite3.IntegrityError:

        return (
            False,
            "That email is already registered.",
        )


# ============================================================
# 16. DELETE ACCOUNT
# ============================================================

def delete_account(account_number):
    """
    Permanently delete an account and its transaction history.

    Transaction history is removed first because it references
    the account number.
    """

    with get_connection() as connection:

        # Delete transaction history first.
        connection.execute(
            """
            DELETE FROM transactions
            WHERE account_number = ?
            """,
            (account_number,),
        )

        # Then delete the account.
        result = connection.execute(
            """
            DELETE FROM accounts
            WHERE account_number = ?
            """,
            (account_number,),
        )

        # rowcount tells us whether an account was actually deleted.
        if result.rowcount == 0:
            return False

    return True


# ============================================================
# 17. GET TRANSACTION HISTORY
# ============================================================

def get_transactions(account_number):
    """
    Get all transactions for the logged-in account.

    The result is converted into a Pandas DataFrame
    so Streamlit can display it as a table.
    """

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                transaction_type,
                amount_cents,
                balance_after_cents,
                created_at
            FROM transactions
            WHERE account_number = ?
            ORDER BY id DESC
            """,
            (account_number,),
        ).fetchall()

    data = []

    for row in rows:

        data.append(
            {
                "Type": row["transaction_type"],
                "Amount": (
                    f"${cents_to_money(row['amount_cents']):,.2f}"
                ),
                "Balance After": (
                    f"${cents_to_money(row['balance_after_cents']):,.2f}"
                ),
                "Date & Time": row["created_at"],
            }
        )

    return pd.DataFrame(data)


# ============================================================
# 18. STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 19. START DATABASE
# ============================================================

# Create the required database tables when the application
# starts.
init_database()


# ============================================================
# 20. INITIALIZE SESSION STATE
# ============================================================
#
# Streamlit reruns the Python script when the user interacts
# with the application.
#
# Session State lets us keep login information between
# these reruns.
# ============================================================

if "account" not in st.session_state:
    st.session_state.account = None

if "account_number" not in st.session_state:
    st.session_state.account_number = None


# ============================================================
# 21. CUSTOM PAGE STYLE
# ============================================================

st.markdown(
    """
    <style>

        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
        }

        .sub-title {
            color: #777;
            margin-bottom: 1rem;
        }

        .account-card {
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid rgba(128,128,128,.25);
            margin-bottom: 1rem;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 22. APPLICATION HEADER
# ============================================================

st.markdown(
    f"""
    <div class="main-title">
        🏦 {APP_NAME}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        A cleaner, safer and database-backed version
        of the original CLI project.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 23. SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.header("ZaRion Menu")

    # --------------------------------------------------------
    # LOGGED-IN USER MENU
    # --------------------------------------------------------

    if st.session_state.account:

        st.success(
            "Logged in as\n"
            f"{st.session_state.account['user_name']}"
        )

        page = st.radio(
            "Choose an action",
            [
                "Dashboard",
                "Deposit Money",
                "Withdraw Money",
                "Account Details",
                "Update Account",
                "Transaction History",
                "Delete Account",
            ],
        )

        # Logout button.
        if st.button(
            "🔒 Logout",
            use_container_width=True,
        ):

            # Clear login information from Session State.
            st.session_state.account = None
            st.session_state.account_number = None

            # Refresh the page so the login menu appears.
            st.rerun()

    # --------------------------------------------------------
    # GUEST MENU
    # --------------------------------------------------------

    else:

        page = st.radio(
            "Choose an action",
            [
                "Home",
                "Create Account",
                "Login",
            ],
        )


# ============================================================
# 24. HOME PAGE
# ============================================================

if page == "Home":

    st.subheader("Welcome to ZaRion 👋")

    st.write(
        """
        This Streamlit version keeps the main features
        of the original Bank Management System while
        replacing terminal input/output with a web interface.
        """
    )

    # Display three important technologies/features.
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Database",
        "SQLite",
    )

    col2.metric(
        "Authentication",
        "PIN + Hash",
    )

    col3.metric(
        "Interface",
        "Streamlit",
    )

    st.info(
        """
        Educational project only.

        This application is not production banking software.
        Real financial systems require stronger authentication,
        encryption, audit controls, compliance and professional
        security testing.
        """
    )


# ============================================================
# 25. CREATE ACCOUNT PAGE
# ============================================================

elif page == "Create Account":

    st.subheader("🆕 Create a New Account")

    # A Streamlit form groups related inputs together.
    #
    # The account is created only after the user presses
    # the submit button.
    with st.form("create_account_form"):

        col1, col2 = st.columns(2)

        # ---------------- LEFT COLUMN ----------------

        with col1:

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name",
            )

            email = st.text_input(
                "Email Address",
                placeholder="example@email.com",
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=18,
                step=1,
            )

        # ---------------- RIGHT COLUMN ----------------

        with col2:

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other",
                ],
            )

            pin = st.text_input(
                "4-Digit PIN",
                type="password",
                max_chars=PIN_LENGTH,
            )

            pin_confirm = st.text_input(
                "Confirm 4-Digit PIN",
                type="password",
                max_chars=PIN_LENGTH,
            )

        submitted = st.form_submit_button(
            "🚀 Create Account",
            use_container_width=True,
        )

    # Process the form only after submission.
    if submitted:

        # First compare both PIN fields.
        if pin != pin_confirm:

            st.error(
                "PIN and confirmation PIN do not match."
            )

        else:

            success, message, account_number = create_account(
                name,
                email,
                pin,
                age,
                gender,
            )

            if success:

                st.success(message)

                st.warning(
                    """
                    Save your account number safely.
                    You will need it to log in.
                    """
                )

                # st.code makes the account number easy to copy.
                st.code(account_number)

            else:

                st.error(message)


# ============================================================
# 26. LOGIN PAGE
# ============================================================

elif page == "Login":

    st.subheader("🔐 Account Login")

    with st.form("login_form"):

        account_number = st.text_input(
            "Account Number",
            placeholder="Enter your 10-digit account number",
        )

        pin = st.text_input(
            "4-Digit PIN",
            type="password",
            max_chars=PIN_LENGTH,
        )

        submitted = st.form_submit_button(
            "🔑 Login",
            use_container_width=True,
        )

    if submitted:

        account = authenticate(
            account_number,
            pin,
        )

        if account:

            # Store login information in Session State.
            #
            # This allows the app to remember the logged-in
            # account while the current Streamlit session is active.
            st.session_state.account = account
            st.session_state.account_number = (
                account["account_number"]
            )

            st.success(
                "Login successful."
            )

            # Reload the page and show the logged-in menu.
            st.rerun()

        else:

            st.error(
                "Invalid account number or PIN."
            )


# ============================================================
# 27. LOGGED-IN APPLICATION
# ============================================================

elif st.session_state.account:

    # Always load the latest account information from SQLite.
    #
    # This makes sure the displayed balance is updated after
    # deposits and withdrawals.
    refresh_logged_in_account()

    account = st.session_state.account

    # If the account no longer exists, clear the session.
    if not account:

        st.error(
            "Your session is no longer valid. Please log in again."
        )

        st.session_state.account_number = None

        st.rerun()


    # ========================================================
    # 27.1 DASHBOARD
    # ========================================================

    if page == "Dashboard":

        st.subheader(
            f"Welcome back, {account['user_name']} 👋"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Current Balance",
            format_money(
                account["balance_cents"]
            ),
        )

        col2.metric(
            "Account Number",
            account["account_number"],
        )

        col3.metric(
            "Age",
            f"{account['age']} years",
        )

        st.markdown("### Quick Actions")

        q1, q2, q3 = st.columns(3)

        q1.info(
            "💰 Use the sidebar to deposit money."
        )

        q2.info(
            "🏧 Use the sidebar to withdraw money."
        )

        q3.info(
            "📊 Use the sidebar to view transactions."
        )


    # ========================================================
    # 27.2 DEPOSIT PAGE
    # ========================================================

    elif page == "Deposit Money":

        st.subheader("💰 Deposit Money")

        st.write(
            "Current balance: "
            f"**{format_money(account['balance_cents'])}**"
        )

        with st.form("deposit_form"):

            amount = st.number_input(
                "Amount",
                min_value=0.01,
                max_value=float(MAX_DEPOSIT),
                value=100.00,
                step=10.00,
                format="%.2f",
            )

            submitted = st.form_submit_button(
                "💰 Deposit",
                use_container_width=True,
            )

        if submitted:

            success, message = deposit(
                account["account_number"],
                amount,
            )

            if success:

                st.success(message)

                # Reload the latest balance.
                refresh_logged_in_account()

            else:

                st.error(message)


    # ========================================================
    # 27.3 WITHDRAW PAGE
    # ========================================================

    elif page == "Withdraw Money":

        st.subheader("🏧 Withdraw Money")

        st.write(
            "Available balance: "
            f"**{format_money(account['balance_cents'])}**"
        )

        with st.form("withdraw_form"):

            amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=100.00,
                step=10.00,
                format="%.2f",
            )

            submitted = st.form_submit_button(
                "🏧 Withdraw",
                use_container_width=True,
            )

        if submitted:

            success, message = withdraw(
                account["account_number"],
                amount,
            )

            if success:

                st.success(message)

                refresh_logged_in_account()

            else:

                st.error(message)


    # ========================================================
    # 27.4 ACCOUNT DETAILS
    # ========================================================

    elif page == "Account Details":

        st.subheader("👤 Account Details")

        left, right = st.columns(2)

        with left:

            st.write(
                f"**Name:** {account['user_name']}"
            )

            st.write(
                f"**Email:** {account['email']}"
            )

            st.write(
                f"**Age:** {account['age']}"
            )

            st.write(
                f"**Gender:** {account['gender']}"
            )

        with right:

            st.write(
                f"**Account Number:** "
                f"{account['account_number']}"
            )

            st.write(
                f"**Balance:** "
                f"{format_money(account['balance_cents'])}"
            )

            st.write(
                f"**Created:** "
                f"{account['created_at']}"
            )


    # ========================================================
    # 27.5 UPDATE ACCOUNT
    # ========================================================

    elif page == "Update Account":

        st.subheader("✏️ Update Account")

        with st.form("update_account_form"):

            new_name = st.text_input(
                "New Name",
                value=account["user_name"],
            )

            new_email = st.text_input(
                "New Email",
                value=account["email"],
            )

            new_pin = st.text_input(
                "New 4-Digit PIN "
                "(leave empty to keep current)",
                type="password",
                max_chars=PIN_LENGTH,
            )

            submitted = st.form_submit_button(
                "💾 Save Changes",
                use_container_width=True,
            )

        if submitted:

            success, message = update_account(
                account["account_number"],
                new_name,
                new_email,
                new_pin,
            )

            if success:

                st.success(message)

                # Reload updated account information.
                refresh_logged_in_account()

            else:

                st.error(message)


    # ========================================================
    # 27.6 TRANSACTION HISTORY
    # ========================================================

    elif page == "Transaction History":

        st.subheader("📊 Transaction History")

        df = get_transactions(
            account["account_number"]
        )

        if df.empty:

            st.info(
                "No transactions found yet."
            )

        else:

            # Display transaction history as a clean table.
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )


    # ========================================================
    # 27.7 DELETE ACCOUNT
    # ========================================================

    elif page == "Delete Account":

        st.subheader("⚠️ Delete Account")

        st.error(
            """
            This action permanently deletes the account
            and its transaction history.
            """
        )

        with st.form("delete_account_form"):

            confirmation = st.text_input(
                "Type DELETE to permanently confirm",
                placeholder="DELETE",
            )

            submitted = st.form_submit_button(
                "🗑️ Permanently Delete Account",
                use_container_width=True,
            )

        if submitted:

            # Require an exact confirmation word.
            if confirmation == "DELETE":

                deleted = delete_account(
                    account["account_number"]
                )

                if deleted:

                    # Remove login information from Session State.
                    st.session_state.account = None
                    st.session_state.account_number = None

                    st.success(
                        "Your account has been permanently deleted."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Account could not be deleted."
                    )

            else:

                st.warning(
                    "Deletion cancelled. "
                    "Type DELETE exactly to confirm."
                )


# ============================================================
# 28. FALLBACK MESSAGE
# ============================================================

else:

    st.warning(
        "Please log in to access this section."
    )
