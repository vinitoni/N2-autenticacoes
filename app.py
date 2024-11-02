import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import Flask, redirect, url_for, render_template, request, session, flash
import logging

app = Flask(__name__)
app.secret_key = "toni123"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'vinitonii@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'qxgo eyfo jbms gcdi')
app.config['MAIL_DEFAULT_SENDER'] = 'vinitonii@gmail.com'

print(app.config['MAIL_USERNAME'])
print(app.config['MAIL_PASSWORD'])  


mail = Mail(app)

# Google OAuth
google_blueprint = make_google_blueprint(
    client_id="887822136397-2sk4m9rttrceiils7ag0qc7c8t4qperq.apps.googleusercontent.com",
    client_secret="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",
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(google_blueprint, url_prefix="/login")

# GitHub OAuth
github_blueprint = make_github_blueprint(
    client_id="Ov23lis42G6M5B6iPu7T",
    client_secret="7aa4d35118d863f87fb89e7a987f4f1616b12dfd",
    scope="user:email"
)
app.register_blueprint(github_blueprint, url_prefix="/github_login")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

@app.route("/")
def index():
    google_data = None
    github_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    
    if google.authorized:
        google_data = google.get(user_info_endpoint).json()

    if github.authorized:
        github_data = github.get("/user").json()

    return render_template(
        'index.html',
        google_data=google_data,
        github_data=github_data,
        google_fetch_url=google.base_url + user_info_endpoint,
        github_fetch_url="https://api.github.com/user"
    )

@app.route("/login")
def login():
    return redirect(url_for("google.login"))

@app.route("/github_login")
def github_login():
    return redirect(url_for("github.login"))

mail = Mail(app)

s = URLSafeTimedSerializer(app.secret_key)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        token = s.dumps(email, salt='password_recovery')
        msg = Message(
            'Redefinição de senha',
            sender='vinitonii@gmail.com',
            recipients=[email]
        )
        link = url_for('reset_password', token=token, _external=True)
        msg.body = f'Clique no link para redefinir a sua senha: {link}'
        mail.send(msg)

        flash('Um link de recuperação de senha foi enviado para o seu e-mail', category='success')
        return redirect(url_for('index'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password_recovery', max_age=3600) # 1hora
    except SignatureExpired:
        return '<h1>O link de redefinição de senha expirou</h1>'
    except BadSignature:
        return '<h1>Token inválido</h1>'
    if request.method == 'POST':
        new_password = request.form['password']
        flash('Sua senha foi redefinida com sucesso!!', category='success')
        return redirect(url_for('index'))
    return render_template('reset_password.html')

if __name__ == "__main__":
    app.run(debug=True)