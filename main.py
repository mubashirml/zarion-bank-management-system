# ============================================================================
# ============================================================================
# -----------------------------   ZaRion's BANK MANAGEMENT SYSTEM   ----------------------------
# ============================================================================
# ============================================================================

# IMPORT LIBRARIES 
import json      # To read and write data in JSON format
import random    # To generate random numbers and characters
import string    # To get lists of alphabets and digits
from pathlib import Path  # To check if a file exists on the computer

class Bank:
    # ---------------------------------------------------------
    # CLASS VARIABLES
    # These belong to the whole class, shared by all users.
    # ---------------------------------------------------------
    database = 'data.json'  # File where user data is saved
    data = []               # List to hold all user accounts

    def __init__(self):
        """
        Constructor: Runs automatically when the program starts.
        """
        self.load_data()  # Load saved data immediately
        self.name = ""    # Placeholder for the user's name

    # ---------------------------------------------------------
    # CLASS METHODS
    # These methods handle class-level data (like the database file).
    # ---------------------------------------------------------
    @classmethod
    def load_data(cls):
        """Loads user accounts from the JSON file."""
        try:
            # Check if the file exists before opening it
            if Path(cls.database).exists():
                with open(cls.database, 'r') as fs:
                    content = fs.read()
                    # Convert JSON string to Python list. Use empty list if file is empty.
                    cls.data = json.loads(content) if content else []
            else:
                print("\n[INFO] No existing database found. A new one will be created upon first entry.")
        except Exception as err:
            print(f"\n[ERROR] Failed to load database: {err}")

    @classmethod
    def update_info(cls):
        """Saves the current user accounts back into the JSON file."""
        try:
            # Open in write mode to update the file
            with open(cls.database, 'w') as fs:
                fs.write(json.dumps(cls.data, indent=4))
        except Exception as err:
            print(f"\n[ERROR] Failed to update database: {err}")

    @classmethod
    def generate_account_id(cls):
        """Creates a random 7-character account ID."""
        alpha = random.choices(string.ascii_letters, k=3)
        number = random.choices(string.digits, k=3)
        special_char = random.choices("~!@#$%^&*", k=1)
        
        # Combine and shuffle characters for security
        account_id = alpha + number + special_char
        random.shuffle(account_id)
        
        return "".join(account_id)

    # ---------------------------------------------------------
    # UI METHODS (User Interface)
    # These methods only display menus and messages.
    # ---------------------------------------------------------
    def user_welcome(self):
        """Shows the main welcome screen and asks for the user's name."""
        print("\n" + "=" * 60)
        print(f"{'ZaRion BANK MANAGEMENT SYSTEM':^60}")
        print("=" * 60 + "\n")
        
        self.name = input("Please enter your name to proceed: ").strip()
        
        print("\n" + "=" * 60)
        print(f"{' DEAR ' + self.name.upper() + '! WELCOME TO ZaRion BANKING SYSTEM ':^60}")
        print("=" * 60 + "\n")
        print("Are you worried about handling your transactions?")
        print("No need to be stressful anymore.\n")
        print("Here at ZaRion, we have solutions for all your transaction-related problems!")

    def screen_welcome(self):
        """Shows the menu header."""
        print("\n" + "=" * 60)
        print(f"{'WELCOME TO ZaRion MAIN MENU':^60}")
        print("=" * 60 + "\n")

    def user_instruct(self):
        """Shows all available options to the user."""
        print("Please choose an option from the menu below:\n")
        print("  [1] CREATE an Account    (New Users)")
        print("  [2] DEPOSIT Money        (Valid Users)")
        print("  [3] WITHDRAW Money       (Existing Users)")
        print("  [4] VIEW Account Details (Current Users)")
        print("  [5] UPDATE Account       (Active Users)")
        print("  [6] DELETE Account       (Leaving Users)")
        print("  [7] EXIT System          (Close Application)")
        print("\n" + "-" * 60)

    def transaction_closing(self):
        """Pauses the screen until the user presses ENTER."""
        print("-" * 60)
        input("\n[ZaRion SYSTEM] Press ENTER to return to the Main Menu...")
        print("\n" * 3)  # Clear space for the next menu

    def closing(self):
        """Shows a goodbye message before closing the app."""
        print("\n" + "=" * 60)
        print(f"{'ZaRion SYSTEM EXITED SUCCESSFULLY':^60}")
        print("=" * 60)
        print(f"{'Nice to see you here, ' + self.name.upper() + '!':^60}")
        print(f"{'Thank you for your precious time with ZaRion.':^60}")
        print("=" * 60 + "\n")

    # ---------------------------------------------------------
    # CORE LOGIC (HELPER METHODS)
    # ---------------------------------------------------------
    def get_user_account(self):
        """Asks for ID and PIN, then searches for the matching account."""
        account_number = input("Enter Your Account Number: ").strip()
        
        # Ensure PIN is a number
        try:
            pin = int(input("Enter Your Account PIN: ").strip())
        except ValueError:
            print("\n[ERROR] PIN must be a numeric value.")
            return None

        # Search the database for the user
        for account in Bank.data:
            if account['account_number'] == account_number and account['pin'] == pin:
                return account  # Found the user
        
        return None  # User not found

    def show_details_by_data(self, data_dict):
        """Prints user details in a clean, readable format."""
        print("-" * 30)
        for key, value in data_dict.items():
            # Format the key (e.g., 'user_name' becomes 'User Name')
            formatted_key = key.replace("_", " ").title()
            print(f"{formatted_key:<15} : {value}")
        print("-" * 30 + "\n")

    # ---------------------------------------------------------
    # CORE LOGIC (MAIN FEATURES)
    # ---------------------------------------------------------
    def create_account(self):
        """Creates a new user account after validating age and PIN."""
        print("\n--- NEW ACCOUNT CREATION ---")
        
        # Get age and PIN safely
        try:
            age = int(input("Enter Your Age: "))
            pin = int(input("Set a 4-digit PIN: "))
        except ValueError:
            print("\n[ERROR] Age and PIN must be numeric values. Account creation aborted.")
            return

        # Validate business rules
        if age < 18:
            print("\n[DECLINED] You must be at least 18 years old to create an account.")
            return
            
        if len(str(pin)) != 4:
            print("\n[DECLINED] Your PIN must be exactly 4 digits long.")
            return

        # Create the user data dictionary
        info = {
            "user_name": self.name.upper(),
            "email": input("Enter Email Address: ").strip(),
            "pin": pin,
            "age": age,
            "gender": input("Enter Gender: ").strip().capitalize(),
            "account_number": self.generate_account_id(),
            "balance": 0.0  # New accounts start with zero balance
        }

        # Save the new account
        Bank.data.append(info)
        Bank.update_info()

        print("\n[SUCCESS] Congratulations! Your ZaRion account has been successfully created.")
        print("Please note down your Account Details below:\n")
        self.show_details_by_data(info)

    def deposit_money(self):
        """Adds money to an existing user's balance."""
        print("\n--- DEPOSIT MONEY ---")
        user_data = self.get_user_account() 
        
        if not user_data:
            print("\n[ERROR] Invalid Credentials or Account Not Found.")
            return 

        # Ask for amount safely
        try:
            amount = float(input("Enter the amount you wish to deposit: "))
        except ValueError:
            print("\n[ERROR] Invalid amount format.")
            return
            
        # Validate deposit limit
        if amount <= 0 or amount > 50000:
            print("\n[DECLINED] Amount must be greater than 0 and up to 50,000.")
            return

        # Update balance
        old_balance = user_data['balance']
        user_data['balance'] += amount
        Bank.update_info()

        print("\n[SUCCESS] Transaction completed successfully.")
        print(f"Deposited Amount : ${amount:.2f}")
        print(f"Old Balance      : ${old_balance:.2f}")
        print(f"New Balance      : ${user_data['balance']:.2f}")

    def withdraw_money(self):
        """Subtracts money from a user's balance if they have enough funds."""
        print("\n--- WITHDRAW MONEY ---")
        user_data = self.get_user_account()
        
        if not user_data:
            print("\n[ERROR] Invalid Credentials or Account Not Found.")
            return

        # Ask for amount safely
        try:
            amount = float(input("Enter the amount you wish to withdraw: "))
        except ValueError:
            print("\n[ERROR] Invalid amount format.")
            return
            
        # Ensure user has enough money
        if amount <= 0 or amount > user_data['balance']:
            print("\n[DECLINED] Insufficient balance or invalid amount.")
            print(f"Your current balance is: ${user_data['balance']:.2f}")
            return

        # Update balance
        old_balance = user_data['balance']
        user_data['balance'] -= amount
        Bank.update_info()

        print("\n[SUCCESS] Transaction completed successfully.")
        print(f"Withdrawn Amount : ${amount:.2f}")
        print(f"Old Balance      : ${old_balance:.2f}")
        print(f"New Balance      : ${user_data['balance']:.2f}")

    def show_details(self):
        """Finds and prints a user's account details."""
        print("\n--- VIEW ACCOUNT DETAILS ---")
        user_data = self.get_user_account()
        
        if not user_data:
            print("\n[ERROR] Invalid Credentials or Account Not Found.")
            return
            
        print("\n[SUCCESS] Account verified. Here are your details:\n")
        self.show_details_by_data(user_data)

    def update_details(self):
        """Allows a user to safely update their Name, Email, or PIN."""
        print("\n--- UPDATE ACCOUNT DETAILS ---")
        user_data = self.get_user_account()
        
        if not user_data:
            print("\n[ERROR] Invalid Credentials or Account Not Found.")
            return
            
        print("\n[SUCCESS] Logged in successfully.")
        print("Note: Press ENTER if you wish to skip updating a specific field.\n")
        
        # Get new inputs
        new_name = input(f"Enter New Name [{user_data['user_name']}]: ").strip()
        new_email = input(f"Enter New Email [{user_data['email']}]: ").strip()
        new_pin_str = input(f"Enter New 4-digit PIN [{user_data['pin']}]: ").strip()

        # Fallback to old data if input is empty
        new_data = {
            "user_name": new_name.upper() if new_name else user_data["user_name"],
            "email": new_email if new_email else user_data["email"],
        }
        
        # Validate new PIN
        if new_pin_str:
            if len(new_pin_str) == 4 and new_pin_str.isdigit():
                new_data["pin"] = int(new_pin_str)
            else:
                print("\n[ERROR] Invalid PIN format. PIN must be a 4-digit number. PIN update skipped.")
                new_data["pin"] = user_data["pin"]
        else:
            new_data["pin"] = user_data["pin"]

        # Check if anything actually changed
        is_updated = False
        for key in new_data:
            if new_data[key] != user_data[key]:
                user_data[key] = new_data[key] 
                is_updated = True 

        # Save only if changes were made
        if is_updated:
            Bank.update_info()
            print("\n[SUCCESS] Your details have been updated successfully!")
        else:
            print("\n[INFO] No changes were made to your profile.")
            
        print("Here are your current details:\n")
        self.show_details_by_data(user_data)

    def delete_account(self):
        """Removes a user's account from the database permanently."""
        print("\n--- DELETE ACCOUNT ---")
        print("WARNING: This action is permanent and cannot be undone.")
        
        user_data = self.get_user_account()
        
        if not user_data:
            print("\n[ERROR] Invalid Credentials or Account Not Found.")
            return
            
        print("\n[SUCCESS] Account verified.")
        print(f"User Name: {user_data['user_name']}")
        print(f"Current Balance: ${user_data['balance']:.2f}")
        
        # Final confirmation check
        confirm = input("\nAre you absolutely sure? Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            Bank.data.remove(user_data)
            Bank.update_info()
            print(f"\n[SUCCESS] Account for {user_data['user_name']} has been permanently deleted from ZaRion servers.")
        else:
            print("\n[INFO] Deletion cancelled. Your account is safe.")


# ==========================================
# MAIN EXECUTION BLOCK 
# ==========================================
# This only runs if the script is executed directly
if __name__ == "__main__":
    app = Bank()          
    app.user_welcome()    
    
    # Infinite loop to keep the program running
    while True:
        app.screen_welcome() 
        app.user_instruct()  
        
        user_choice = input("Enter your preference (1-7): ").strip()
        
        # Route the user to the correct feature based on their input
        if user_choice == '1':
            app.create_account()
        elif user_choice == '2':
            app.deposit_money()
        elif user_choice == '3':
            app.withdraw_money()
        elif user_choice == '4':
            app.show_details()
        elif user_choice == '5':
            app.update_details()
        elif user_choice == '6':
            app.delete_account()
        elif user_choice == '7':
            app.closing()  
            break  # Exit the loop and close the program
        else:
            print("\n[ERROR] Invalid option selected. Please choose a valid number from 1 to 7.")
            
        app.transaction_closing()