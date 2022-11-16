import sqlite3


def get_all_users():
    result = []

    with sqlite3.connect("phonebook.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        for r in rows:
            result.append({
                "id": r[0],
                "first_name": r[1],
                "last_name": r[2],
                "phone": r[3],
                "description": r[4],
            })

    return result


def add_user(user: {}):
    with sqlite3.connect("phonebook.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO users (first_name, last_name, phone, description)
                       VALUES (:first_name, :last_name, :phone, :description)""",
                       {
                           "first_name": user["first_name"],
                           "last_name": user["last_name"],
                           "phone": user["phone"],
                           "description": user["description"],
                       })

        conn.commit()


def delete_user(user_id):
    with sqlite3.connect("phonebook.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM users
                          WHERE id = :user_id""",
                       {
                           "user_id": user_id,
                       })

        conn.commit()


def search_users(search_string):
    result = []
    with sqlite3.connect("phonebook.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE last_name LIKE :filter",
                       {
                           "filter": f'%{search_string}%',
                       })

        rows = cursor.fetchall()
        for r in rows:
            result.append({
                "id": r[0],
                "first_name": r[1],
                "last_name": r[2],
                "phone": r[3],
                "description": r[4],
            })

    return result
