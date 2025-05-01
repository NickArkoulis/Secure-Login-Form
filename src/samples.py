import sqlite3
import hashlib
import sys
import getpass
import socket
import threading

conn = sqlite3.connect("userdata.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

username1, password1 = "nick", hashlib.sha256("nick".encode()).hexdigest()
username2, password2 = "arkoulis", hashlib.sha256("arkoulis".encode()).hexdigest()
username3, password3 = "unizg", hashlib.sha256("unizg".encode()).hexdigest()
username4, password4 = "nikos", hashlib.sha256("nikos".encode()).hexdigest()

cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username1, password1))
cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username2, password2))
cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username3, password3))
cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username4, password4))

conn.commit()

class UserManagement:
    def __init__(self):
        self.conn = sqlite3.connect("userdata.db")
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS userdata (
                id INTEGER PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        self.conn.commit()
    #add
    def add_user(self, username: str, password: str) -> None:
        password = hashlib.sha256(password.encode()).hexdigest()
        self.cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()
        print(f"User '{username}' added successfully.")
    #passwd
    def change_password(self, username: str, password: str) -> None:
        password = hashlib.sha256(password.encode()).hexdigest()
        self.cur.execute("UPDATE userdata SET password = ? WHERE username = ?", (password, username))
        self.conn.commit()
        print(f"Password changed successfully for user '{username}'.")
    #forcepass
    def force_password_change(self, username: str) -> None:
        self.cur.execute("UPDATE userdata SET force_password_change = 1 WHERE username = ?", (username,))
        self.conn.commit()
        print(f"User '{username}' will be prompted to change password on next login.")
    #del
    def delete_user(self, username: str) -> None:
        self.cur.execute("DELETE FROM userdata WHERE username = ?", (username,))
        self.conn.commit()
        print(f"User '{username}' deleted successfully.")

#login
class Login:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", 8888))
        self.server.listen()
        self.user_mgmt = UserManagement()

    def handle_connection(self, c) -> None:
        c.send("Username: ".encode())
        username = c.recv(1024).decode()

        # Prompt for password without echoing the user's input to the console
        c.send("Password: ".encode())
        password = self.getpass()
        # Hash the password
        password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

        if cur.fetchall():
            c.send("Successful Login!".encode())
            force_password_change = self.user_mgmt.get_force_password_change(username)
            if force_password_change:
                c.send("You are required to change your password.".encode())
                c.send("New password: ".encode())
                new_password = self.getpass()
                self.user_mgmt.change_password(username, new_password)
                self.user_mgmt.disable_force_password_change(username)
        else:
            c.send("Try again!".encode())

    def run(self) -> None:
        while True:
            client, addr = self.server.accept()
            threading.Thread(target=self.handle_connection, args=(client,)).start()

    def getpass(self) -> str:
        """
        Prompt for password without echoing the user's input to the console
        """
        if sys.stdin is not sys.__stdin__:
            return getpass.getpass()
        try:
            import msvcrt  # for Windows
        except ImportError:
            import termios  # for UNIX
            import tty

            def getpass_unix(prompt="Password: "):
                sys.stdout.write(prompt)
                sys.stdout.flush()
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                except Exception as e:
                    print("Error:", e)