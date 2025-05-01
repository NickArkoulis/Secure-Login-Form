import sqlite3
import hashlib
import socket
import threading
import getpass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8888))
server.listen()

def handle_connection(c):
    c.send("Username: ".encode())
    username = c.recv(1024).decode()

    # Prompt for password without echoing the user's input to the console
    c.send("Password: ".encode())
    password = getpass.getpass()
    password = c.recv(1024).decode()
    # Hash the password
    password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

    if cur.fetchall():
        # User has been authenticated, proceed with requested operation
        c.send("Welcome to the user management system!".encode())

        # Prompt the user for the operation to perform
        c.send("Available operations:\n".encode())
        c.send("1. add\n".encode())
        c.send("2. passwd\n".encode())
        c.send("3. forcepass\n".encode())
        c.send("4. del\n".encode())

        operation = c.recv(1024).decode()

        if operation == "1":
            # Add a new user to the database
            c.send("Enter username: ".encode())
            username = c.recv(1024).decode()
            c.send("Enter password: ".encode())
            password = c.recv(1024).decode()
            # Hash the password before storing it in the database
            password = hashlib.sha256(password.encode()).hexdigest()
            cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            c.send(f"User {username} added successfully!".encode())

        elif operation == "2":
            # Change a user's password
            c.send("Enter username to change password: ".encode())
            username = c.recv(1024).decode()
            c.send("Enter new password: ".encode())
            password = c.recv(1024).decode()
            # Hash the password before updating the database
            password = hashlib.sha256(password.encode()).hexdigest()
            cur.execute("UPDATE userdata SET password = ? WHERE username = ?", (password, username))
            conn.commit()
            c.send(f"Password for user {username} changed successfully!".encode())

        elif operation == "3":
            # Force a user to change their password on next login
            c.send("Enter username to force password change: ".encode())
            username = c.recv(1024).decode()
            cur.execute("UPDATE userdata SET force_password_change = 1 WHERE username = ?", (username,))
            conn.commit()
            c.send(f"User {username} must change their password on next login.".encode())

        elif operation == "4":
            # Remove a user from the database
            c.send("Enter username to remove: ".encode())
            username = c.recv(1024).decode()
            cur.execute("DELETE FROM userdata WHERE username = ?", (username,))
            conn.commit()
            c.send(f"User {username} removed successfully!".encode())

        else:
            c.send("Invalid operation".encode())
            exit()

    else:
        c.send("Try again!".encode())

while True:
    client, addr = server.accept()
    threading.Thread(target=handle_connection, args=(client,)).start()