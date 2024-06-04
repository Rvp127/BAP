from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, completed INTEGER, tokens INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS tokens
             (id INTEGER PRIMARY KEY AUTOINCREMENT, amount INTEGER)''')

c.execute("SELECT * FROM tokens")
if not c.fetchone():
    c.execute("INSERT INTO tokens (amount) VALUES (0)")
    conn.commit()

# List of redemption quotes
redemption_quotes = [
    "Here's a nice quote: 'The best way to predict the future is to create it.'",
    "You get a chocolate!",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "The only limit to our realization of tomorrow will be our doubts of today.",
    "Believe you can and you're halfway there.",
    "It does not matter how slowly you go as long as you do not stop."
]

@app.route('/')
def index():
    c.execute("SELECT * FROM tasks WHERE completed = 0")
    tasks = c.fetchall()
    
    c.execute("SELECT amount FROM tokens")
    token_amount = c.fetchone()[0]
    
    return render_template('index.html', tasks=tasks, token_amount=token_amount, message=None)

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form['task']
    tokens = int(request.form['tokens'])
    
    c.execute("INSERT INTO tasks (task, completed, tokens) VALUES (?, ?, ?)", (task, 0, tokens))
    conn.commit()
    return redirect('/')

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    c.execute("SELECT tokens FROM tasks WHERE id=?", (task_id,))
    task_tokens = c.fetchone()[0]
    
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    
    c.execute("UPDATE tokens SET amount=amount+? WHERE id=?", (task_tokens, 1))
    conn.commit()
    return redirect('/')

@app.route('/earn_token', methods=['GET'])
def earn_token():
    c.execute("UPDATE tokens SET amount=amount+1 WHERE id=?", (1,))
    conn.commit()
    return redirect('/')

@app.route('/redeem_token', methods=['POST'])
def redeem_token():
    redeem_amount = int(request.form['redeem_amount'])
    message = None
    
    c.execute("SELECT amount FROM tokens")
    token_amount = c.fetchone()[0]
    
    if token_amount >= redeem_amount:
        c.execute("UPDATE tokens SET amount=amount-? WHERE id=?", (redeem_amount, 1))
        conn.commit()
        
        # Randomly select a redemption quote
        message = random.choice(redemption_quotes)
    else:
        message = "Not enough tokens to redeem."

    c.execute("SELECT * FROM tasks WHERE completed = 0")
    tasks = c.fetchall()
    
    c.execute("SELECT amount FROM tokens")
    token_amount = c.fetchone()[0]

    return render_template('index.html', tasks=tasks, token_amount=token_amount, message=message)

if __name__ == '__main__':
    app.run(debug=True)

    