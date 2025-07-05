from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, os, uuid

app = Flask(__name__)
app.secret_key = 'mirumo-secret'

# Создаём базу данных при первом запуске
if not os.path.exists("database.db"):
    conn = sqlite3.connect("database.db")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.execute("CREATE TABLE videos (id INTEGER PRIMARY KEY, title TEXT, filename TEXT, owner TEXT)")
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    videos = conn.execute("SELECT * FROM videos").fetchall()
    conn.close()

    html = """
    <html><head><title>Mirumo</title>
    <style>
    body { font-family: 'Comic Sans MS', cursive; background: #fff6fb; color: #333; text-align: center; padding: 20px; }
    a { text-decoration: none; padding: 6px 12px; background: #ffc8ec; border-radius: 10px; color: #333; margin: 5px; }
    video { border-radius: 10px; margin-top: 10px; }
    .video-card { border: 2px dashed #ffc8ec; padding: 10px; margin: 20px auto; max-width: 360px; border-radius: 16px; background: #fff; }
    </style>
    </head><body>
    <h1>🎀 Добро пожаловать в Mirumo 🎀</h1>
    """

    if 'user' in session:
        html += f"<p>Привет, <b>{session['user']}</b> | <a href='/upload'>Загрузить видео</a> | <a href='/logout'>Выйти</a></p>"
    else:
        html += "<p><a href='/login'>Войти</a> | <a href='/register'>Регистрация</a></p>"

    html += "<h2>📼 Видео:</h2>"

    if videos:
        for v in videos:
            html += f"""
            <div class='video-card'>
                <h3>{v[1]}</h3>
                <video width='320' controls><source src='/videos/{v[2]}'></video>
                <p>Загрузил: {v[3]}</p>
            </div>
            """
    else:
        html += "<p>🥺 Пока никто не загрузил видео. Будь первым!</p>"

    html += "</body></html>"
    return html

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("database.db")
        user = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        if user:
            return "Пользователь уже существует"
        conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (u,p))
        conn.commit()
        conn.close()
        return redirect('/login')

    return """
    <h2>Регистрация</h2>
    <form method="post">
      Логин: <input name="username"><br>
      Пароль: <input name="password" type="password"><br><br>
      <button>Зарегистрироваться</button>
    </form>
    """

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("database.db")
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()
        conn.close()
        if user:
            session['user'] = u
            return redirect('/')
        return "Неверный логин или пароль"

    return """
    <h2>Вход</h2>
    <form method="post">
      Логин: <input name="username"><br>
      Пароль: <input name="password" type="password"><br><br>
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
        if not file:
            return "Файл не выбран"

        filename = str(uuid.uuid4()) + "_" + file.filename
        file.save(filename)

        conn = sqlite3.connect("database.db")
        conn.execute("INSERT INTO videos (title, filename, owner) VALUES (?, ?, ?)", (title, filename, session['user']))
        conn.commit()
        conn.close()
        return redirect('/')

    return """
    <h2>Загрузка видео</h2>
    <form method="post" enctype="multipart/form-data">
      Название: <input name="title"><br><br>
      Видео: <input name="file" type="file"><br><br>
      <button>Загрузить</button>
    </form>
    """

# Отдача видеофайлов
@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
