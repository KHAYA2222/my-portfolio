from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail's SMTP server
app.config['MAIL_PORT'] = 587  # Port for TLS
app.config['MAIL_USE_TLS'] = True  # Use TLS
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your email
# Your email password or app password
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.secret_key = os.getenv('SECRET_KEY')  # Required for flashing messages

# Initialize Flask-Mail
mail = Mail(app)

# Route for the homepage


@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Create and send the email
        try:
            msg = Message(
                # Email subject
                subject=f"New Contact Form Submission: {subject}",
                sender='khayelihlexolani28@gmail.com',  # Sender's email
                # Your email (recipient)
                recipients=['khayelihlexolani28@gmail.com']
            )
            msg.body = f"""
            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """
            mail.send(msg)  # Send the email

            # Flash a success message
            flash('Thank you! Your message has been sent.', 'success')
        except Exception as e:
            # Flash an error message if something goes wrong
            flash('Oops! Something went wrong. Please try again.', 'error')
            print(f"Error: {e}")

        # Redirect back to the homepage
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
