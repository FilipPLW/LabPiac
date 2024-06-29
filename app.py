import sqlite3

from flask import Flask, render_template, send_from_directory, request, redirect, url_for
app = Flask(__name__)
DATABASE = 'database.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS data (name TEXT, text TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

create_table()
@app.route('/result')
def result():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('SELECT name, text, created_at, rowid FROM data ORDER BY created_at DESC')
    data = cur.fetchall()
    conn.close()
    return render_template('result.html', data=data)

@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('INSERT INTO data (name, text) VALUES (?, ?)', (name, text))
        conn.commit()
        conn.close()
        return redirect(url_for('result'))
    return render_template('add_entry.html')

@app.route('/edit_entry/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    if request.method == 'POST':
        new_name = request.form['name']
        new_text = request.form['text']
        cur.execute('UPDATE data SET name=?, text=? WHERE rowid=?', (new_name, new_text, id))
        conn.commit()
        conn.close()
        return redirect(url_for('result'))
    else:
        cur.execute('SELECT name, text FROM data WHERE rowid=?', (id,))
        entry = cur.fetchone()
        conn.close()
        if entry:
            return render_template('edit_entry.html', id=id, name=entry[0], text=entry[1])
        else:
            return 'Entry not found', 404

@app.route('/delete_entry/<int:id>')
def delete_entry(id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('DELETE FROM data WHERE rowid=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('result'))
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
