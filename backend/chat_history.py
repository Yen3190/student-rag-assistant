from database import conn

def add_history(question, answer):

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history (question, answer) VALUES (?, ?)",
        (question, answer)
    )

    conn.commit()


def get_history():

    cursor = conn.cursor()

    cursor.execute(
        "SELECT question, answer FROM history ORDER BY id DESC LIMIT 50"
    )

    rows = cursor.fetchall()

    return [
        {
            "question": r[0],
            "answer": r[1]
        }
        for r in rows
    ]