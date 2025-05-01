import socket

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect(("localhost", 8888))

# Prompt the user for the operation to perform
print("Available operations:")
print("1. add")
print("2. passwd")
print("3. forcepass")
print("4. del")

operation = input("Enter operation number: ")

# Perform the selected operation
if operation == "1":
    username = input("Enter username: ")
    password = input("Enter password: ")
    message = f"add|{username}|{password}"
elif operation == "2":
    username = input("Enter username to change password: ")
    password = input("Enter new password: ")
    message = f"passwd|{username}|{password}"
elif operation == "3":
    username = input("Enter username to force password change: ")
    message = f"forcepass|{username}"
elif operation == "4":
    username = input("Enter username to remove: ")
    message = f"del|{username}"
else:
    print("Invalid operation")
    exit()

# Send the operation and username to the server
client.send(operation.encode())
if operation in ("1", "2", "3", "4"):
    client.send(username.encode())

# Receive and print the server's response
response = client.recv(1024).decode()
print(response)

# Close the connection
client.close()