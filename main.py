import os
import threading
import shutil
import uuid
import mimetypes
from flask import Flask, request, redirect, url_for, render_template_string, session, send_file
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)

# ================= SETTINGS =================
TOKEN = "8346787985:AAFRHe2-IScAOmmYHhopSuD0uw-JKRDoej0"
ADMINS = [7770767498]

FILES_DIR = r"C:\Users\XPRISTO\Desktop\Unilack"
os.makedirs(FILES_DIR, exist_ok=True)

USERNAME = "admin"
PASSWORD = "admin123"

GLOBAL_TOKEN_MAP = {}
USER_REPORTS = {}

# ================= LOGIN PAGE (HTML) =================
LOGIN_PAGE = '''''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Management Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 420px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .login-container:hover {
            transform: translateY(-5px);
        }
        h2 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 30px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #34495e;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            background: #f9f9f9;
            transition: border-color 0.3s, background 0.3s;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #3498db;
            background: white;
            outline: none;
        }
        input[type="submit"] {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px;
            border: none;
            width: 100%;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        input[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        .error {
            color: #e74c3c;
            margin-top: 20px;
            padding: 10px;
            background: #fadbd8;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
        }
        .logo {
            margin-bottom: 30px;
        }
        .logo img {
            max-width: 100px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="80" height="80" fill="#3498db">
                <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
            </svg>
        </div>
        <h2>File Management Login</h2>
        <form method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter your username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>
            <input type="submit" value="Login">
        </form>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
    </div>
</body>
</html>
'''

# ================= HOME PAGE (HTML) =================
HOME_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: #2c3e50;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }
        .header h1 {
            color: #2c3e50;
            font-size: 28px;
            font-weight: 600;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-logout {
            background: #e74c3c;
            color: white;
        }
        .btn-logout:hover {
            background: #c0392b;
            transform: translateY(-2px);
        }
        .path-display {
            background: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            font-size: 16px;
            color: #3498db;
            font-weight: 500;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-3px);
        }
        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            display: flex;
            align-items: center;
        }
        .card-title svg {
            margin-right: 10px;
            color: #3498db;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #34495e;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="file"]:focus {
            border-color: #3498db;
            outline: none;
        }
        input[type="submit"] {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        input[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .file-item {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        .file-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        .file-info {
            display: flex;
            align-items: center;
        }
        .file-icon {
            margin-right: 15px;
            font-size: 24px;
        }
        .file-name {
            font-weight: 500;
            color: #2c3e50;
        }
        .file-link {
            text-decoration: none;
            color: #2c3e50;
            display: flex;
            align-items: center;
            width: 100%;
        }
        .file-link:hover .file-name {
            color: #3498db;
        }
        .delete-button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .delete-button:hover {
            background: #c0392b;
            transform: scale(1.05);
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📂 File Management Panel</h1>
            <div class="header-actions">
                <a href="{{ url_for('logout') }}"><button class="btn btn-logout">🚪 Logout</button></a>
            </div>
        </div>

        <div class="path-display">
            Current path: {{ current_path or '/' }}
        </div>

        <div class="card">
            <div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                Create New Folder
            </div>
            <form method="post" action="{{ url_for('create_folder') }}">
                <div class="form-group">
                    <input type="text" name="folder_name" placeholder="Enter folder name" required>
                </div>
                <input type="hidden" name="current_path" value="{{ current_path }}">
                <input type="submit" value="Create Folder">
            </form>
        </div>

        <div class="card">
            <div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Upload Files
            </div>
            <form method="post" action="{{ url_for('upload_file') }}" enctype="multipart/form-data">
                <div class="form-group">
                    <input type="file" name="files" multiple required>
                </div>
                <input type="hidden" name="current_path" value="{{ current_path }}">
                <input type="submit" value="Upload Files">
            </form>
        </div>

        {% if contents %}
        <div class="file-list">
            {% for name, is_dir in contents %}
            <div class="file-item">
                {% if is_dir %}
                <a class="file-link" href="{{ url_for('home', path=(current_path + '/' + name).lstrip('/')) }}">
                    <div class="file-info">
                        <div class="file-icon">📁</div>
                        <div class="file-name">{{ name }}</div>
                    </div>
                </a>
                {% else %}
                <div class="file-info">
                    <div class="file-icon">📄</div>
                    <div class="file-name">{{ name }}</div>
                </div>
                {% endif %}
                <form method="post" action="{{ url_for('delete_item') }}" onsubmit="return confirm('Are you sure you want to delete this item?')">
                    <input type="hidden" name="item_path" value="{{ (current_path + '/' + name).lstrip('/') }}">
                    <button type="submit" class="delete-button">Delete</button>
                </form>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
            <h3>No files or folders</h3>
            <p>Upload files or create folders to get started</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

# ================= AUTH & SECURITY HELPERS =================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def secure_path_join(base, *paths):
    new_path = os.path.abspath(os.path.join(base, *paths))
    if not new_path.startswith(os.path.abspath(base)):
        raise Exception("Access outside the base directory is not allowed.")
    return new_path

def list_files_safe(path):
    try:
        return sorted([(name, os.path.isdir(os.path.join(path, name)))
                       for name in os.listdir(path)],
                      key=lambda x: (not x[1], x[0].lower()))
    except Exception:
        return []

# ================= FLASK APP SETUP =================
app = Flask(__name__)
app.secret_key = app.secret_key or "change-me-secret"

# ================= FLASK ROUTES =================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == USERNAME and p == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password."
    return render_template_string(LOGIN_PAGE, error=error)

@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@login_required
def home(path):
    try:
        base_path = secure_path_join(FILES_DIR, path)
    except Exception:
        return "Access to this path is not allowed.", 403

    if not os.path.exists(base_path):
        base_path = FILES_DIR
        path = ""

    contents = list_files_safe(base_path)
    return render_template_string(HOME_PAGE, contents=contents, current_path=path)

@app.route("/create_folder", methods=["POST"])
@login_required
def create_folder():
    folder_name = request.form.get("folder_name", "").strip()
    current_path = request.form.get("current_path", "")
    if not folder_name:
        return redirect(url_for("home", path=current_path))
    try:
        base_path = secure_path_join(FILES_DIR, current_path)
        os.makedirs(os.path.join(base_path, folder_name), exist_ok=True)
    except Exception as e:
        return f"Error: {e}", 400
    return redirect(url_for("home", path=current_path))

@app.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
    current_path = request.form.get("current_path", "")
    try:
        base_path = secure_path_join(FILES_DIR, current_path)
    except Exception:
        return "Access to this path is not allowed.", 403

    if "files" not in request.files:
        return "No files were selected.", 400

    files = request.files.getlist("files")
    for f in files:
        if not f or f.filename == "":
            continue
        save_path = os.path.join(base_path, f.filename)
        f.save(save_path)
    return redirect(url_for("home", path=current_path))

@app.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    item_path = request.form.get("item_path", "")
    try:
        full = secure_path_join(FILES_DIR, item_path)
    except Exception:
        return "Access is not allowed.", 403
    if not os.path.exists(full):
        return "Item not found.", 404
    try:
        if os.path.isdir(full):
            shutil.rmtree(full)
        else:
            os.remove(full)
    except Exception as e:
        return f"Deletion error: {e}", 500
    parent = os.path.dirname(item_path)
    return redirect(url_for("home", path=parent))

@app.route("/download/<path:filename>")
@login_required
def download_file(filename):
    try:
        full = secure_path_join(FILES_DIR, filename)
    except Exception:
        return "Access is not allowed.", 403
    if not os.path.exists(full):
        return "File not found.", 404
    mime_type, _ = mimetypes.guess_type(full)
    if mime_type is None:
        mime_type = "application/octet-stream"
    return send_file(full, mimetype=mime_type, as_attachment=True, download_name=os.path.basename(full))

# ================= TELEGRAM: NAVIGATION KEYBOARD =================
def build_nav_keyboard_for_path(rel_path=""):
    abs_path = os.path.join(FILES_DIR, rel_path) if rel_path else FILES_DIR
    items = list_files_safe(abs_path)

    keyboard = []
    if rel_path:
        parent = os.path.dirname(rel_path)
        token = "D" + uuid.uuid4().hex
        GLOBAL_TOKEN_MAP[token] = {"type": "dir", "path": parent}
        keyboard.append([InlineKeyboardButton("⬆️ Back", callback_data=token)])

    for name, is_dir in items:
        token = ("D" if is_dir else "F") + uuid.uuid4().hex
        entry_rel = os.path.join(rel_path, name) if rel_path else name
        GLOBAL_TOKEN_MAP[token] = {"type": "dir" if is_dir else "file", "path": entry_rel}
        text = f"📁 {name}" if is_dir else f"📄 {name}"
        keyboard.append([InlineKeyboardButton(text, callback_data=token)])

    return InlineKeyboardMarkup(keyboard)

async def send_root_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = build_nav_keyboard_for_path("")
    await update.message.reply_text("📂 Choose a folder or file:", reply_markup=markup)

# ================= TELEGRAM: REPORT COMMAND =================
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = " ".join(context.args) if context.args else ""

    if not message_text:
        await update.message.reply_text(
            "Please provide a message for the admins. Usage: /report your message here"
        )
        return

    report_id = str(uuid.uuid4())[:8]
    USER_REPORTS[report_id] = {
        "user_id": user.id,
        "username": user.username or user.first_name,
        "message": message_text,
        "timestamp": update.message.date
    }

    for admin_id in ADMINS:
        try:
            keyboard = [[InlineKeyboardButton("Answer", callback_data=f"ANSWER_{report_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"NEW REPORT from {user.username or user.first_name} (ID: {user.id})\n\nReport ID: {report_id}\nMessage: {message_text}",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

    await update.message.reply_text("Your message has been sent to admins. They will contact you soon.")

# ================= TELEGRAM: BASIC COMMANDS =================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    buttons = [[InlineKeyboardButton("📥 Browse Files", callback_data="NAV_ROOT")]]
    if user_id in ADMINS:
        buttons.insert(0, [InlineKeyboardButton("🌐 Admin Panel", callback_data="ADMIN_PANEL")])
    else:
        buttons.append([InlineKeyboardButton("Contact Admin", callback_data="REPORT_HELP")])
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Welcome to Unilak PDF Bot 📚         📚اهلا بيك في بوت يونيلاك"
                                    , reply_markup=markup)

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not an administrator.")
        return
    link = "http://192.168.1.70:5000"
    await update.message.reply_text(f"🌐 Open the control panel: {link}\nUse your username and password to log in.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/start - Start the bot
/report - Contact admins
/help - Show this help

Use /report your_message to contact administrators.
"""
    await update.message.reply_text(help_text)

# ================= TELEGRAM: CALLBACKS & TEXT HANDLER =================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id

        if data == "NAV_ROOT":
            markup = build_nav_keyboard_for_path("")
            if query.message:
                await query.message.reply_text("📂 Choose a folder or file:", reply_markup=markup)
            else:
                await context.bot.send_message(chat_id=user_id, text="📂 Choose a folder or file:", reply_markup=markup)
            return

        if data == "ADMIN_PANEL":
            if user_id not in ADMINS:
                await query.message.reply_text("❌ You are not an administrator.")
                return
            link = "http://192.168.1.70:5000"
            await query.message.reply_text(f"🌐 Open the control panel: {link}\nUse your username and password to log in.")
            return

        if data == "REPORT_HELP":
            await query.message.reply_text(
                "To contact admins, use: /report your_message_here\nExample: /report I need help with a file"
            )
            return

        if data.startswith("ANSWER_"):
            report_id = data.replace("ANSWER_", "")
            if report_id not in USER_REPORTS:
                await query.message.reply_text("Report not found.")
                return
            report = USER_REPORTS[report_id]
            context.user_data["current_report"] = report_id
            context.user_data["report_user_id"] = report["user_id"]
            await query.message.reply_text(
                f"Replying to report from {report['username']}:\n{report['message']}\n\nPlease type your response:"
            )
            return

        entry = GLOBAL_TOKEN_MAP.get(data)
        if not entry:
            await query.message.reply_text("⚠️ This button is invalid or expired. Please try again.")
            return

        if entry["type"] == "dir":
            rel = entry["path"] or ""
            markup = build_nav_keyboard_for_path(rel)
            text = f"📂 Contents: /{rel}" if rel else "📂 Root:"
            if query.message:
                await query.message.reply_text(text, reply_markup=markup)
            else:
                await context.bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
            return

        if entry["type"] == "file":
            rel = entry["path"]
            full = os.path.join(FILES_DIR, rel)
            if not os.path.exists(full):
                await query.message.reply_text("❌ File not found.")
                return

            mime_type, _ = mimetypes.guess_type(full)
            if mime_type is None:
                mime_type = "application/octet-stream"
                extension = os.path.splitext(full)[1].lower()
                mime_map = {
                    '.pdf': 'application/pdf',
                    '.txt': 'text/plain',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                }
                mime_type = mime_map.get(extension, mime_type)

            filename = os.path.basename(full)

            try:
                with open(full, 'rb') as file:
                    await query.message.reply_document(
                        document=InputFile(file, filename=filename),
                        filename=filename,
                        caption=f"📄 {filename}"
                    )
            except Exception as e:
                await query.message.reply_text(f"An error occurred while sending the file. Please try again: {e}")
            return

    except Exception as e:
        print(f"[callback_handler error] {e}")
        try:
            await update.effective_chat.send_message(f"An unexpected error occurred: {e}")
        except Exception:
            pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_report" in context.user_data:
        report_id = context.user_data["current_report"]
        user_id = context.user_data["report_user_id"]
        response_text = update.message.text

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Admin response to your report:\n\n{response_text}"
            )
            await update.message.reply_text("Response sent successfully!")

            del context.user_data["current_report"]
            del context.user_data["report_user_id"]

        except Exception as e:
            await update.message.reply_text(f"Failed to send response: {e}")
        return

    txt = (update.message.text or "").lower()
    if "hello" in txt or "hi" in txt:
        await update.message.reply_text("Welcome!")
    elif "good morning" in txt:
        await update.message.reply_text("Good morning! Hope you have a great day.")
    elif "good afternoon" in txt:
        await update.message.reply_text("Good afternoon! How's your day going?")
    elif "good evening" in txt:
        await update.message.reply_text("Good evening! Hope you had a good day.")
    elif "how are you" in txt:
        await update.message.reply_text("I'm doing well, thanks! How about you?")
    elif "what's up" in txt or "whats up" in txt:
        await update.message.reply_text("Not much—just here to help you 😉")
    elif "who are you" in txt:
        await update.message.reply_text("I'm the Unilak Bot Assistant, here to get you the documents you need 😄")
    elif "good" in txt or "that's good" in txt or "awesome" in txt:
        await update.message.reply_text("Thank you! I really appreciate it! 🥰")
    elif "help" in txt:
        await update.message.reply_text("Sure! What do you need help with?")
    elif "bye" in txt or "see you" in txt:
        await update.message.reply_text("Bye! Feel free to come back anytime.")
    elif "thank you" in txt or "thanks" in txt:
        await update.message.reply_text("You're welcome! Happy to assist you ❤️")
    elif "what can you do" in txt:
        await update.message.reply_text("I can chat with you, answer questions, and provide documents. Just ask!")
    elif "i need a book" in txt or "give me a book" in txt:
        await update.message.reply_text("Just click /start and browse to get your document.")
    elif "documents" in txt or "files" in txt:
        await update.message.reply_text("Use /start to browse all available documents and files.")
    elif "study" in txt or "studying" in txt:
        await update.message.reply_text("I can help you find study materials. Click /start to begin.")
    elif "assignment" in txt or "homework" in txt:
        await update.message.reply_text("Need help with assignments? Browse our document collection using /start")
    elif "exam" in txt or "test" in txt:
        await update.message.reply_text("Good luck with your exam! I can help you find study materials.")
    elif "pdf" in txt or "document" in txt:
        await update.message.reply_text("Click /start to browse and download PDF documents.")
    elif "search" in txt or "find" in txt:
        await update.message.reply_text("Use /start to browse through all available files and documents.")
    elif "contact" in txt or "admin" in txt or "report" in txt:
        await update.message.reply_text("Use /report to contact the administrators.")
    elif "help me" in txt:
        await update.message.reply_text("I'm here to help! What do you need assistance with?")
    elif "nice" in txt or "cool" in txt:
        await update.message.reply_text("Glad you like it! 😊")
    elif "ok" in txt or "okay" in txt:
        await update.message.reply_text("Alright! Let me know if you need anything.")
    elif "yes" in txt:
        await update.message.reply_text("Great! How can I assist you?")
    elif "no" in txt:
        await update.message.reply_text("Okay, no problem. Let me know if you change your mind.")
    elif "please" in txt:
        await update.message.reply_text("Of course! How can I help you?")
    elif "sorry" in txt:
        await update.message.reply_text("No problem at all! 😊")
    elif "welcome" in txt:
        await update.message.reply_text("Thank you! 🥰")
    elif "how to" in txt:
        await update.message.reply_text("Use /start to browse files or /report to contact admins.")
    elif "where" in txt:
        await update.message.reply_text("You can find all documents by clicking /start")
    elif "when" in txt:
        await update.message.reply_text("You can access documents anytime using /start")
    elif "why" in txt:
        await update.message.reply_text("I'm here to help students access learning materials easily.")
    elif "can you" in txt:
        await update.message.reply_text("I can help you find documents and answer basic questions.")
    elif "need help" in txt:
        await update.message.reply_text("I'm here to help! Tell me what you need.")
    elif "problem" in txt or "issue" in txt:
        await update.message.reply_text("Use /report to contact administrators about any problems.")
    elif "work" in txt or "working" in txt:
        await update.message.reply_text("Yes, I'm working! How can I help you?")
    elif "bot" in txt:
        await update.message.reply_text("Yes, I'm a bot designed to help students with documents.")
    elif "unilak" in txt:
        await update.message.reply_text("I'm here to help Unilak students access learning materials.")
    elif "student" in txt:
        await update.message.reply_text("As a student, you can use /start to access all study materials.")
    elif "library" in txt:
        await update.message.reply_text("Think of me as your digital library assistant! Use /start to browse.")
    elif "material" in txt or "resources" in txt:
        await update.message.reply_text("Click /start to access all learning materials and resources.")
    elif "download" in txt:
        await update.message.reply_text("You can download files by browsing with /start")
    elif "upload" in txt:
        await update.message.reply_text("Admins can upload files using the web panel. Contact them with /report")
    elif "course" in txt or "class" in txt:
        await update.message.reply_text("I can help you find course materials. Use /start to browse.")
    elif "lesson" in txt:
        await update.message.reply_text("Browse lesson materials using /start command.")
    elif "note" in txt or "notes" in txt:
        await update.message.reply_text("Find study notes by clicking /start")
    elif "guide" in txt:
        await update.message.reply_text("Use /start to browse study guides and materials.")
    elif "tutorial" in txt:
        await update.message.reply_text("Find tutorials and learning materials using /start")
    elif "question" in txt:
        await update.message.reply_text("I can answer basic questions or help you find documents.")
    elif "answer" in txt:
        await update.message.reply_text("I'll do my best to answer your questions!")
    elif "info" in txt or "information" in txt:
        await update.message.reply_text("I can provide information and help you find documents.")
    elif "مرحبا" in txt or "اهلا" in txt:
        await update.message.reply_text("أهلاً وسهلاً بك! 😊 سعيد جداً برؤيتك!")
    elif "شكرا" in txt or "شكراً" in txt or "تسلم" in txt :
        await update.message.reply_text("العفو! 🥰 دائماً سعيد لمساعدتك!")
    elif "كيف الحال" in txt or "كيفك" in txt or "كيف حالك" in txt:
        await update.message.reply_text("الحمد لله بخير! 🌟 وأنت كيف حالك؟")
    elif "صباح الخير" in txt:
        await update.message.reply_text("صباح النور! 🌞 أتمنى لك يوماً رائعاً!")
    elif "مساء الخير" in txt:
        await update.message.reply_text("مساء النور! 🌙 أتمنى لك مساءً سعيداً!")
    elif "مع السلامة" in txt or "باي" in txt or "مع السلامه" in txt:
        await update.message.reply_text("مع السلامة انشاء الله ربنا يوفقك ✨😉")
    elif "ممتاز" in txt or "رائع" in txt or "بخير" in txt:
        await update.message.reply_text("واو! 🎉 هذا رائع! سعيد لسماع ذلك!")
    elif "حسنا" in txt or "طيب" in txt:
        await update.message.reply_text("ممتاز! 💫 كيف يمكنني مساعدتك أكثر؟")
    elif "نعم" in txt:
        await update.message.reply_text("رائع! 😄 تفضل أخبرني ماذا تحتاج؟")
    elif "لا" in txt:
        await update.message.reply_text("حسناً! 😊 لا مشكلة، أنا هنا عندما تحتاجني!")
    elif "ماذا تفعل" in txt or "شو تسوي" in txt:
        await update.message.reply_text("أنا هنا لمساعدتك في العثور على جميع المستندات والملفات التي تحتاجها! 📚")
    elif "مساعدة" in txt or "ساعدني" in txt:
        await update.message.reply_text("بكل سرور! 🚀 أخبرني ما الذي تبحث عنه وسأساعدك!")
    elif "من انت" in txt or "مين انت" in txt:
        await update.message.reply_text("أنا بوت Unilak! 🤖 مساعدك الشخصي للعثور على جميع المستندات والملفات الدراسية!")
    elif "الوثائق" in txt or "المستندات" in txt:
        await update.message.reply_text("لدينا الكثير من المستندات الرائعة! 📂 إضغط /start لاستعراضها جميعاً!")
    elif "الملفات" in txt or "file" in txt:
        await update.message.reply_text("يمكنك تصفح كل الملفات عبر /start 🗂️ سأجد لك ما تبحث عنه!")
    elif "بحث" in txt or "ابحث" in txt:
        await update.message.reply_text("هيا لنبدأ البحث! 🔍 إضغط /start لاستكشاف جميع الملفات!")
    elif "دراسة" in txt or "مذاكرة" in txt:
        await update.message.reply_text("أتمنى لك التوفيق في دراستك! 🎓 إضغط /start للوصول إلى مواد الدراسة!")
    elif "محاضرة" in txt or "محاضرات" in txt:
        await update.message.reply_text("لدينا العديد من المحاضرات والمواد! 📝 إستخدم /start للعثور عليها!")
    elif "كتاب" in txt or "كتب" in txt:
        await update.message.reply_text("هيا نجد الكتاب المثالي لك! 📚 إضغط /start لتصفح المكتبة!")
    else:
        await update.message.reply_text("I couldn't understand that 😥")

# ================= TELEGRAM: ERROR HANDLER =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ================= FLASK SERVER THREAD =================
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

# ================= MAIN ENTRY =================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    app_tel = Application.builder().token(TOKEN).build()
    app_tel.add_handler(CommandHandler("start", start_command))
    app_tel.add_handler(CommandHandler("upload", upload_command))
    app_tel.add_handler(CommandHandler("help", help_command))
    app_tel.add_handler(CommandHandler("report", report_command))
    app_tel.add_handler(CallbackQueryHandler(callback_handler))
    app_tel.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app_tel.add_error_handler(error_handler)

    print("✅ Bot and Flask server are running...")
    app_tel.run_polling()
