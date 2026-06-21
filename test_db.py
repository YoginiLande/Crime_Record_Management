from database.db import get_connection

conn = get_connection()

if conn:
    print("Database Connected Successfully 🚀")
else:
    print("Connection Failed ❌")