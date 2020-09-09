import base64

from argon2 import argon2_hash

from flask import Flask, Response, json, render_template, redirect, request, session, flash

from werkzeug.security import safe_join

app = Flask(__name__)

config = json.load(open("/srv/upload-server/config.json"))

app.secret_key = config['SECRET_KEY']
app.debug = True
app.config['ENV'] = 'debug'

username = config['USERNAME']
password = config['PASSWORD']
salt = config['SALT']

def login_route():
    if request.method == "POST":
        if request.form.get('username') == username and base64.b64encode(argon2_hash(request.form.get('password'), salt)).decode('utf-8') == password:
            session['logged_in'] = True
            return redirect('/', code = 303)

        flash("Invalid credentials!", category = "error")

    return render_template("login.html")

@app.route("/", methods = ['GET', 'POST'])
def serve_route():
    if not session.get('logged_in'):
        return login_route()

    if request.method == "POST":
        filename = request.form['filename']

        file = request.files['file']

        if filename == "": filename = file.filename

        if filename == "":
          flash("No file detected!", category = "error")

        else:
            file.save(safe_join(config['UPLOAD_DIR'], filename))
            flash("File uploaded!", category = "success")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(port = 3000, debug = True)
