from datetime import datetime, timezone
import os
from smtplib import SMTPException

from flask import Flask, render_template, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not set. Add it to your environment or .env file.")

mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024
app.config['CONTACT_ENABLED'] = bool(mail_username and mail_password)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

if not app.config['CONTACT_ENABLED']:
    app.logger.warning("Contact form disabled: configure MAIL_USERNAME and MAIL_PASSWORD.")

mail = Mail(app)

RECIPIENT_EMAIL = 'khayelihlexolani28@gmail.com'


def strip_text(value):
    return value.strip() if value else value


class ContactForm(FlaskForm):
    name = StringField('Name', filters=[strip_text], validators=[
        DataRequired(), Length(max=100),
        Regexp(r'^[^\r\n]+$', message='Please use a single line.'),
    ])
    email = StringField('Email', filters=[strip_text], validators=[
        DataRequired(), Length(max=254), Email(),
    ])
    subject = StringField('Subject', filters=[strip_text], validators=[
        DataRequired(), Length(max=150),
        Regexp(r'^[^\r\n]+$', message='Please use a single line.'),
    ])
    message = TextAreaField('Message', filters=[strip_text], validators=[
        DataRequired(), Length(max=5000),
    ])


@app.context_processor
def template_context():
    return {
        'current_year': datetime.now(timezone.utc).year,
        'contact_enabled': app.config['CONTACT_ENABLED'],
    }


@app.route('/')
def home():
    return render_template('index.html', form=ContactForm())


@app.route('/submit', methods=['POST'])
def submit():
    form = ContactForm()
    if not app.config['CONTACT_ENABLED']:
        flash('The contact form is unavailable. Please use the email link below.', 'error')
        return render_template('index.html', form=form), 503

    if not form.validate_on_submit():
        flash('Your message was not sent. Please review the form below.', 'error')
        return render_template('index.html', form=form), 400

    try:
        msg = Message(
            subject=f"New Contact Form Submission: {form.subject.data}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[RECIPIENT_EMAIL],
            reply_to=form.email.data,
        )
        msg.body = (
            f"Name: {form.name.data}\n"
            f"Email: {form.email.data}\n"
            f"Subject: {form.subject.data}\n\n"
            f"Message:\n{form.message.data}"
        )
        mail.send(msg)
    except (SMTPException, OSError):
        app.logger.exception("Contact email delivery failed")
        flash('Your message could not be sent. Please try again or email me directly. Your draft is still below.', 'error')
        return render_template('index.html', form=form), 503

    flash('Thank you! Your message has been sent.', 'success')
    return redirect(url_for('home', _anchor='contact'), code=303)


@app.errorhandler(413)
def request_too_large(error):
    flash('Your message is too large. Please keep it under 5,000 characters.', 'error')
    return render_template('index.html', form=ContactForm(formdata=None)), 413


if __name__ == '__main__':
    app.run()