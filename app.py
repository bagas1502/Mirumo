from flask import Flask, request, redirect, session
import sqlite3, os, requests

app = Flask(__name__)
app.secret_key = 'mirumo-secret'

# Создание базы
if not os.path.exists("database.db"):
    conn = sqlite3.connect("database.db")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.execute("CREATE TABLE videos (id INTEGER PRIMARY KEY, title TEXT, filename TEXT, owner TEXT)")
    conn.commit()
    conn.close()

# Главная страница
from flask import render_template

@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    rows = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    conn.close()

    # Преобразуем в список словарей
    videos = [
        {
            "id": row[0],
            "title": row[1],
            "filename": row[2],
            "username": row[3],
            "thumbnail_url": "/static/preview.jpg"  # Пока временная заглушка
        }
        for row in rows
    ]

    return render_template("index.html", videos=videos)

# Регистрация
from flask import render_template, request, redirect

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("database.db")
        user = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        if user:
            conn.close()
            return "Пользователь уже существует"
        conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (u, p))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('register.html')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("database.db")
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if user:
            session['user'] = u
            return redirect('/')
        return "Неверные данные"

    return """
    <form method="post">
      <h2>Вход</h2>
      Логин: <input name="username"><br>
      Пароль: <input name="password" type="password"><br>
      <button>Войти</button>
    </form>
    """

# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# Загрузка видео
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']
        filename = file.filename
        save_path = f"vid_{filename}"
        file.save(save_path)

        # Сохраняем в базу
        conn = sqlite3.connect("database.db")
        conn.execute("INSERT INTO videos (title, filename, owner) VALUES (?, ?, ?)", (title, save_path, session['user']))
        conn.commit()
        conn.close()


        # Отправка в Telegram
        token = '7583600247:AAHpDr9cEsiYOQmSwGqJoSO1mVN_GtcGHgs'
        chat_id = '-1002329779058'
        with open(save_path, 'rb') as f:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo",
                data={'chat_id': chat_id, 'caption': title},
                files={'video': f}
            )
            print("Результат отправки:", r.text)

        # Удаляем файл после отправки
        try:
            os.remove(save_path)
        except Exception as e:
            print("Ошибка удаления файла:", e)

        return redirect('/')

    return """
    <form method="post" enctype="multipart/form-data">
      <h2>Загрузить видео</h2>
      Название: <input name="title"><br>
      Видео: <input name="file" type="file"><br>
      <button>Загрузить</button>
    </form>
    """

# Сервис отдачи видеофайлов
@app.route('/<path:filename>')
def serve_file(filename):
    return open(filename, 'rb').read()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
