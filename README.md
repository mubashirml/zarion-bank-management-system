# 🏦 ZaRion Bank Management System

A Python-based **Bank Management System** that evolved from a console-based application into an interactive **Streamlit web application** with SQLite database persistence, secure PIN hashing, account management, deposits, withdrawals, and transaction history.

> 🚀 **Project Evolution:** CLI + JSON → Streamlit + SQLite

---

## 📌 Project Overview

**ZaRion Bank Management System** is an educational Python project created to practice real-world programming concepts by building a functional banking application.

The project was initially developed as a **console-based application** using Python, Object-Oriented Programming, and JSON file handling.

The project was later improved into an interactive **Streamlit web application** with a structured SQLite database and additional features for better usability, data management, and security.

### Project Evolution

```text
Version 1
Python CLI Application
        ↓
JSON File Persistence
        ↓
Basic Banking Operations
        ↓
        ↓
Version 2
Streamlit Web Interface
        ↓
SQLite Database
        ↓
PIN Hashing
        ↓
Transaction History
        ↓
Improved Account Management
```

---

## ✨ Features

### 👤 Account Management

* Create a new bank account
* Generate a unique account number
* Login using account number and PIN
* View account details
* Update account information
* Delete account with confirmation
* Logout functionality

### 💰 Banking Operations

* Deposit money
* Withdraw money
* Balance validation
* Prevent withdrawal beyond available balance
* Transaction history
* Display current account balance

### 🔐 Security Improvements

* PINs are not stored as plain text
* PIN hashing using PBKDF2-HMAC-SHA256
* Random salt generation for PIN hashing
* Secure hash comparison
* `.env` and Streamlit secrets protection through `.gitignore`

### 🗄️ Data Management

* SQLite database
* Persistent account data
* Persistent transaction history
* Separate account and transaction tables
* Integer-cents approach for money calculations

### 🖥️ User Interface

* Interactive Streamlit web interface
* Sidebar navigation
* Login interface
* Account creation form
* Dashboard
* Deposit and withdrawal forms
* Account details page
* Transaction history table
* Account update interface
* Account deletion confirmation

---

## 🛠️ Technologies Used

* **Python**
* **Streamlit**
* **SQLite**
* **Pandas**
* **Hashlib**
* **HMAC**
* **Secrets**
* **Decimal**
* **Context Managers**
* **Git & GitHub**

---

## 🧠 Python Concepts Practiced

This project helped me practice and strengthen the following concepts:

### Core Python

* Variables
* Data Types
* Conditional Statements
* Loops
* Functions
* Exception Handling
* String Handling
* Lists and Dictionaries

### Object-Oriented Programming

* Classes
* Objects
* Methods
* Encapsulation
* Reusable program structure

### File & Data Handling

* JSON data handling
* SQLite database operations
* SQL queries
* Database transactions
* Data persistence

### Security Concepts

* Password/PIN hashing
* Salt generation
* PBKDF2-HMAC
* Secure hash comparison
* Sensitive data protection

### Application Development

* Streamlit widgets
* Streamlit forms
* Session State
* Sidebar navigation
* Interactive UI
* DataFrame display

---

## 📂 Project Structure

```text
zarion-bank-management-system/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── screenshots/
│   ├── home.png
│   ├── create-account.png
│   ├── login.png
│   ├── dashboard.png
│   ├── deposit.png
│   ├── withdrawal.png
│   └── transactions.png
│
└── zarion_bank.db
```

> **Note:** The SQLite database file may be generated locally when the application runs. Database files containing user data should generally not be committed to a public repository.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mubashirml/zarion-bank-management-system.git
```

### 2. Open the Project Folder

```bash
cd zarion-bank-management-system
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser through the local Streamlit server.

---

## 📦 Requirements

The main dependency for the web application is:

```text
streamlit
```

Additional dependencies are defined in:

```text
requirements.txt
```

---

## 🏦 Application Workflow

```text
Start Application
       │
       ▼
    Home Page
       │
       ├───────────────┐
       ▼               ▼
Create Account       Login
       │               │
       ▼               ▼
Generate Account    Verify PIN
       │               │
       └───────┬───────┘
               ▼
          Dashboard
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    Deposit Withdraw  Details
       │       │        │
       └───────┼────────┘
               ▼
       Transaction History
               │
               ▼
       Update / Delete
               │
               ▼
             Logout
```

---

## 💾 Database Design

The improved version uses **SQLite** instead of JSON for persistent data storage.

### Accounts Table

Stores information such as:

* Account number
* User name
* Email
* PIN hash
* PIN salt
* Age
* Gender
* Account balance
* Account creation date

### Transactions Table

Stores:

* Account number
* Transaction type
* Transaction amount
* Balance after transaction
* Transaction date and time

---

## 💵 Money Handling

The application stores monetary values as **integer cents** instead of relying directly on floating-point values.

For example:

```text
$100.50
   ↓
10050 cents
```

This approach helps avoid common floating-point precision problems when performing money calculations.

---

## 🔐 Security Note

This project implements basic educational security practices such as PIN hashing and salt generation.

However, this application should **not be used for real banking or financial transactions**.

Production banking systems require significantly stronger security controls, authentication systems, encryption, auditing, monitoring, compliance requirements, and professional security testing.

---

## 🖥️ Screenshots

### Home Page

![Home Page](screenshots/home.png)

### Create Account

![Create Account](screenshots/create-account.png)

### Login

![Login](screenshots/login.png)

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Deposit / Withdrawal

![Banking Operations](screenshots/deposit.png)

### Transaction History

![Transaction History](screenshots/transactions.png)

---

## 🚀 Future Improvements

Possible future improvements include:

* Firebase or PostgreSQL integration
* Admin dashboard
* Email verification
* Password/PIN reset functionality
* Two-factor authentication
* Better transaction filtering
* PDF bank statements
* Data visualization
* Automated testing
* Role-based access control
* Cloud deployment
* Improved production-level security

---

## 📚 Learning Outcome

Through this project, I practiced how to transform a basic Python console application into a more interactive application with a graphical web interface and persistent database.

The project helped me understand the transition from:

```text
Basic Python Script
        ↓
Object-Oriented Application
        ↓
Persistent Data Storage
        ↓
Database-Based Application
        ↓
Interactive Web Application
```

---

## ⚠️ Disclaimer

**ZaRion Bank Management System is an educational portfolio project.**

It is designed for learning Python, database management, Streamlit application development, and basic security concepts.

It is **not intended for real-world banking or financial use.**

---

## 👨‍💻 Author

**Muhammad Mubashir**

Aspiring AI Engineer | Python Learner | Software Engineering Student

---

## ⭐ Project Status

**Current Version:** Streamlit + SQLite

**Status:** Actively Improving 🚀

This project will continue to evolve as I learn new Python, software engineering, database, AI, and application development concepts.

---

## 📄 License

This project is licensed under the terms included in the repository's `LICENSE` file.

```
```
