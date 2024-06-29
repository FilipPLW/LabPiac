import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.github import make_github_blueprint, github
import secrets
import os


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
DATABASE = 'database.db'
github_blueprint = make_github_blueprint(
    client_id="Ov23liqkgAhvCrkYfJ94",
    client_secret="6206fbf720517986e95af37b5da50cb39aac347d",
)
app.register_blueprint(github_blueprint, url_prefix='/login')
def create_table():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS data (name TEXT, text TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()


create_table()


# Routes
@app.route('/')
def index():
    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            return render_template('index.html')
        return '<h1>Request failed!</h1>'
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


@app.route('/result')
def result():
    if github.authorized:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            github_name = account_info_json['login']
        else:
            github_name = None
    else:
        github_name = None

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('SELECT name, text, created_at, rowid FROM data ORDER BY created_at DESC')
    data = cur.fetchall()
    conn.close()

    return render_template('result.html', data=data, github_name=github_name)


@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if github.authorized:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            github_name = account_info_json['login']
        else:
            github_name = None
    else:
        github_name = None

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('INSERT INTO data (name, text) VALUES (?, ?)', (name, text))
        conn.commit()
        conn.close()
        return redirect(url_for('result'))

    return render_template('add_entry.html', github_name=github_name)


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
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
