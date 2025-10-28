from flask import Flask ,render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import os
import json


with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

MAIL_Username = os.getenv('MAIL_USERNAME', params.get('gmail-username'))
MAIL_Password = os.getenv('MAIL_PASSWORD', params.get('gmail-password'))

app.config.update(
    MAIL_SERVER =  'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = MAIL_Username,
    MAIL_PASSWORD = MAIL_Password
)

mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']


db = SQLAlchemy(app)

class Contacts(db.Model):
    """
    s.no, name, phone_num, email, mssg, date 
    """
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable = False)
    phone_num = db.Column(db.String(13), nullable = False)
    email = db.Column(db.String(30), nullable = False)
    mssg = db.Column(db.String(120), nullable = False)
    date = db.Column(db.String(12), nullable = False)
    


@app.route("/")
def index():
    return render_template('index.html', params = params)

@app.route("/post")
def post():
    return render_template('post.html',params = params)

@app.route("/about")
def about():
    return render_template('about.html',params = params)

@app.route("/contact", methods=["GET","POST"])
def contact():
    if (request.method == 'POST'):
        
        '''Add Entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone= request.form.get('phone')
        message= request.form.get('message')
        entry = Contacts(name=name,phone_num = phone, mssg = message, email = email, date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        db.session.add(entry)
        db.session.commit()

        mail.send_message(
            subject='New message from Blog',
            sender=email,  # user who filled the contact form
            recipients=[MAIL_Username],  # your Gmail where you’ll receive it
            body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}"
        )


        # Flash success message
        flash("Your message has been sent successfully!", "success")

        # Redirect to avoid form resubmission on page reload
        return redirect(url_for('contact'))
    
    return render_template('contact.html',params = params)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
