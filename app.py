from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "secure_key_123"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="maintenance_db"
    )

# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ================= AUTH CHECK =================
def login_required():
    return 'user' in session

# ================= HOME =================
@app.route('/')
def index():
    if not login_required():
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipment")
    equipment = cursor.fetchall()
    conn.close()
    return render_template('index.html', equipment=equipment)

# ================= ADD EQUIPMENT =================
@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if not login_required():
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        location = request.form['location']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO equipment (name, type, location, status) VALUES (%s,%s,%s,%s)",
            (name, type_, location, 'Working')
        )
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add_equipment.html')

# ================= ADD LOG =================
@app.route('/add_log/<int:id>', methods=['GET', 'POST'])
def add_log(id):
    if not login_required():
        return redirect('/login')

    if request.method == 'POST':
        fault = request.form['fault']
        action = request.form['action']
        technician = request.form['technician']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO maintenance_log (equipment_id, log_date, fault, action_taken, technician) VALUES (%s,%s,%s,%s,%s)",
            (id, date.today(), fault, action, technician)
        )
        cursor.execute(
            "UPDATE equipment SET status=%s WHERE id=%s",
            ('Under Maintenance', id)
        )
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add_log.html')

# ================= MARK WORKING =================
@app.route('/mark_working/<int:id>')
def mark_working(id):
    if not login_required():
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE equipment SET status=%s WHERE id=%s",
        ('Working', id)
    )
    conn.commit()
    conn.close()
    return redirect('/')

# ================= VIEW LOGS =================
@app.route('/logs/<int:id>')
def view_logs(id):
    if not login_required():
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM maintenance_log WHERE equipment_id=%s",
        (id,)
    )
    logs = cursor.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)

# ================= DELETE EQUIPMENT =================
@app.route('/delete_equipment/<int:id>')
def delete_equipment(id):
    if not login_required():
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipment WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run()
