import getpass
import hashlib
import sqlite3
import usermgmt

usermgmt.create_table()

def login():
    # Prompt the user for their username
    username = input("Username: ")

    # Prompt for password without echoing the user's input to the console
    password = getpass.getpass(prompt="Password: ")

    # Hash the password
    password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

    if cur.fetchone():
        print("Successful Login!")

        # Check if the user needs to change their password
        cur.execute("SELECT force_password_change FROM userdata WHERE username = ?", (username,))
        if cur.fetchone()[0] == 1:
            usermgmt.change_password(username, getpass.getpass(prompt="Enter a new password: "))

    else:
        print("Try again!")

    conn.commit()
    conn.close()

# Sample usage of the function
if __name__ == "__main__":
    login()
