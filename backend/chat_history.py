history = []

def add_history(question, answer):
    history.append({
        "question": question,
        "answer": answer
    })

def get_history():
    return history