import sqlite3
import hashlib

def create_table():
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    # Create userdata table with columns: username, password, force_password_change
    cur.execute('''CREATE TABLE IF NOT EXISTS userdata (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        force_password_change INTEGER DEFAULT 0)''')

    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    # Hash the password
    password = hashlib.sha256(password.encode()).hexdigest()

    # Insert new user into database
    cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

def change_password(username, new_password):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    # Hash the new password
    new_password = hashlib.sha256(new_password.encode()).hexdigest()

    # Update password of existing user
    cur.execute("UPDATE userdata SET password = ? WHERE username = ?", (new_password, username))

    conn.commit()
    conn.close()

def force_password_change(username):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    # Check if the column exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='userdata' AND sql LIKE '%force_password_change%'")
    result = cur.fetchone()
    if result is None:
        # If the column doesn't exist, add it to the table
        cur.execute("ALTER TABLE userdata ADD COLUMN force_password_change INTEGER DEFAULT 0")

    # Update force_password_change field of existing user
    cur.execute("UPDATE userdata SET force_password_change = 1 WHERE username = ?", (username,))

    conn.commit()
    conn.close()


def remove_user(username):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    # Delete user from database
    cur.execute("DELETE FROM userdata WHERE username = ?", (username,))

    conn.commit()
    conn.close()

# Sample usage of the functions
if __name__ == "__main__":
    create_table()
    add_user("newuser", "newpassword")
    change_password("existinguser", "newpassword")
    force_password_change("existinguser")
    remove_user("existinguser")

