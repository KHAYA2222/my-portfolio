from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not set. Add it to your environment or .env file.")

mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')

if not mail_username or not mail_password:
    raise RuntimeError("MAIL_USERNAME and MAIL_PASSWORD must be set.")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.secret_key = app.secret_key

mail = Mail(app)

RECIPIENT_EMAIL = 'khayelihlexolani28@gmail.com'


# ─── Routes ─────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name    = request.form['name']
    email   = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    try:
        msg = Message(
            subject=f"New Contact Form Submission: {subject}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[RECIPIENT_EMAIL],
        )
        msg.body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        )
        mail.send(msg)
        flash('Thank you! Your message has been sent.', 'success')
    except Exception as e:
        flash('Oops! Something went wrong. Please try again.', 'error')
        print(f"Mail error: {e}")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)