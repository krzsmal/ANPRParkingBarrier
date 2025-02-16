from flask import Flask, request, redirect, session, url_for, render_template
import sqlite3
from datetime import datetime, timedelta
from utils import generate_plot, generate_stats

database = '../Barrier/database.db'

app = Flask(__name__)
app.secret_key = 'secret'


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/historia', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        if 'plateNumber' in request.form:
            plateNumber = request.form['plateNumber'].upper()
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM przejazdy WHERE nr_rejestracyjny = ? ORDER BY data", (plateNumber,))
            rows = cursor.fetchall()
            conn.close()
            if rows:
                last = None
                total_duration = timedelta(0)
                if len(rows) % 2 == 1:
                    last = rows[-1]
                    rows = rows[:-1]
                    entry_time = datetime.strptime(last[2], '%Y-%m-%d %H:%M:%S')
                    total_duration = datetime.now() - entry_time
                    last = {'entry_time': entry_time.strftime('%H:%M:%S %d-%m-%y'), 'exit_time': 'Brak', 'duration': str(total_duration).split('.')[0]}
                data = []
                for i in range(0, len(rows), 2):
                    entry = rows[i]
                    exit = rows[i + 1]
                    entry_time = datetime.strptime(entry[2], '%Y-%m-%d %H:%M:%S')
                    exit_time = datetime.strptime(exit[2], '%Y-%m-%d %H:%M:%S')
                    duration = exit_time - entry_time
                    total_duration += duration
                    data.append({
                        'entry_time': entry_time.strftime('%H:%M:%S %d-%m-%y'),
                        'exit_time': exit_time.strftime('%H:%M:%S %d-%m-%y'),
                        'duration': str(duration).split('.')[0],
                    })
                rows = data
                total_duration = str(total_duration).split('.')[0]
                return render_template('history.html', rows=rows, total_duration=total_duration, last=last)
    return render_template('history.html')


@app.route('/karty', methods=['GET', 'POST'])
def cards():
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form['action']
            if action == 'delete':
                if 'plateNumber' in request.form:
                    plateNumber = request.form['plateNumber']
                    conn = sqlite3.connect(database)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM rejestracje_karty WHERE nr_rejestracyjny = ?", (plateNumber,))
                    conn.commit()
                    conn.close()
                    return render_template('karty.html', action=action, success=True)
            elif action == 'select':
                if 'cardNumber' in request.form:
                    cardNumber = request.form['cardNumber']
                    conn = sqlite3.connect(database)
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM rejestracje_karty WHERE nr_karty = ?", (cardNumber,))
                    rows = cursor.fetchall()
                    registrations = None
                    if rows:
                        registrations = [row[0] for row in rows]
                    conn.close()
                    return render_template('karty.html', action=action, registrations=registrations)
            elif action == 'insert':
                if 'cardNumber' in request.form and 'plateNumber' in request.form:
                    cardNumber = request.form['cardNumber']
                    plateNumber = request.form['plateNumber'].upper()
                    conn = sqlite3.connect(database)
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM rejestracje_karty WHERE nr_rejestracyjny = ?", (plateNumber,))
                    rows = cursor.fetchall()
                    if rows:
                        conn.close()
                        return render_template('karty.html', action=action)
                    cursor.execute("INSERT INTO rejestracje_karty (nr_rejestracyjny, nr_karty) VALUES (?, ?)", (plateNumber, cardNumber))
                    conn.commit()
                    conn.close()
                    return render_template('karty.html', action=action, success=True)
        return render_template('cards.html')
    return render_template('cards.html')


@app.route('/bank', methods=['GET', 'POST'])
def bank():
    if request.method == 'POST':
        if 'cardNumber' in request.form:
            cardNumber = request.form['cardNumber']
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute("SELECT saldo FROM bank WHERE nr_karty = ?", (cardNumber,))
            row = cursor.fetchone()
            if row:
                balance = row[0]
                print(balance)
                conn.close()
                return render_template('bank.html', balance=balance)
    return render_template('bank.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' in session:
        plot_json = generate_plot()
        stats = generate_stats()
        return render_template('admin.html', plot_json=plot_json, stats=stats)
    else:
        return redirect(url_for('admin_login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form['action']
        
            if action == 'logout':
                session.pop('admin', None)
                return render_template('login.html', login='logout')
            elif action == 'login' and 'username' in request.form and 'password' in request.form:
                username = request.form['username']
                password = request.form['password']
                if username == 'admin' and password == 'admin':
                    session['admin'] = True
                    return render_template('login.html', login='success')
                else:
                    return render_template('login.html', login='failure')
    return render_template('login.html')


@app.route('/admin/historia', methods=['GET', 'POST'])
def admin_history():
    if 'admin' in session:
        if request.method == 'POST':
            if 'action' in request.form:
                action = request.form['action']
                if action == 'delete':
                    if 'id' in request.form:
                        id = request.form['id']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM przejazdy WHERE id = ?", (id,))
                        conn.commit()
                        conn.close()
                elif action == 'update':
                    if 'id' in request.form and 'plateNumber' in request.form and 'date' in request.form and 'entry' in request.form:
                        id = request.form['id']
                        plateNumber = request.form['plateNumber']
                        date = request.form['date']
                        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        entry = request.form['entry']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE przejazdy SET nr_rejestracyjny=?, data=?, wjazd=? WHERE id = ?", (plateNumber, date, entry, id))
                        conn.commit()
                        conn.close()
                elif action == 'insert':
                    if 'plateNumber' in request.form and 'date' in request.form and 'entry' in request.form:
                        plateNumber = request.form['plateNumber']
                        date = request.form['date']
                        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        entry = request.form['entry']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO przejazdy (nr_rejestracyjny, data, wjazd) VALUES (?, ?, ?)", (plateNumber, date, entry))
                        conn.commit()
                        conn.close()
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM przejazdy ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return render_template('admin_history.html', rows=rows)
    else:
        return redirect(url_for('admin_login'))


@app.route('/admin/karty', methods=['GET', 'POST'])
def admin_cards():
    if 'admin' in session:
        if request.method == 'POST':
            if 'action' in request.form:
                action = request.form['action']
                if action == 'delete':
                    if 'plateNumber' in request.form:
                        plateNumber = request.form['plateNumber']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM rejestracje_karty WHERE nr_rejestracyjny = ?", (plateNumber,))
                        conn.commit()
                        conn.close()
                elif action == 'update':
                    if 'plateNumber' in request.form and 'cardNumber' in request.form:
                        plateNumber = request.form['plateNumber']
                        cardNumber = request.form['cardNumber']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE rejestracje_karty SET nr_karty=? WHERE nr_rejestracyjny = ?", (cardNumber, plateNumber))
                        conn.commit()
                        conn.close()
                elif action == 'insert':
                    if 'plateNumber' in request.form and 'cardNumber' in request.form:
                        plateNumber = request.form['plateNumber']
                        cardNumber = request.form['cardNumber']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM rejestracje_karty WHERE nr_rejestracyjny = ?", (plateNumber,))
                        rows = cursor.fetchall()
                        if not rows:
                            cursor.execute("INSERT INTO rejestracje_karty (nr_rejestracyjny, nr_karty) VALUES (?, ?)", (plateNumber, cardNumber))
                            conn.commit()
                        conn.close()
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rejestracje_karty ORDER BY nr_rejestracyjny")
        rows = cursor.fetchall()
        conn.close()
        return render_template('admin_cards.html', rows=rows)
    else:
        return redirect(url_for('admin_login'))


@app.route('/admin/bank', methods=['GET', 'POST'])
def admin_bank():
    if 'admin' in session:
        if request.method == 'POST':
            if 'action' in request.form:
                action = request.form['action']
                if action == 'delete':
                    if 'cardNumber' in request.form:
                        cardNumber = request.form['cardNumber']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM bank WHERE nr_karty = ?", (cardNumber,))
                        conn.commit()
                        conn.close()
                elif action == 'update':
                    if 'cardNumber' in request.form and 'balance' in request.form:
                        cardNumber = request.form['cardNumber']
                        balance = request.form['balance']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE bank SET saldo=? WHERE nr_karty = ?", (balance, cardNumber))
                        conn.commit()
                        conn.close()
                elif action == 'insert':
                    if 'cardNumber' in request.form and 'balance' in request.form:
                        cardNumber = request.form['cardNumber']
                        balance = request.form['balance']
                        conn = sqlite3.connect(database)
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM bank WHERE nr_karty = ?", (cardNumber,))
                        rows = cursor.fetchall()
                        if not rows:
                            cursor.execute("INSERT INTO bank (nr_karty, saldo) VALUES (?, ?)", (cardNumber, balance))
                            conn.commit()
                        conn.close()
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bank ORDER BY nr_karty")
        rows = cursor.fetchall()
        print(rows)
        conn.close()
        return render_template('admin_bank.html', rows=rows)
    else:
        return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)