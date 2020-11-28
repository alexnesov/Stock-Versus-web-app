from SV import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os



db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')




@app.route('/')
def home():
    return render_template('home.html')


@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form)




@app.route('/table')
@login_required
def table():
    def fetch():
        db = pymysql.connect(host=f'{db_endp}',user=f'{db_user}',password=f'{db_pass}',database='flaskfinance')
        cursor = db.cursor()
        cursor.execute(
        "SELECT ticker, sector, price, industry, change_, volume FROM usStocksOverview")
        items = cursor.fetchmany(50)
        print(items)
        cursor.close()
        db.close()

        return items
        # simply to have a proposer display without commas and parantheses specific to tuple format
        # items = [item[0] for item in items]

    items = fetch()
    return render_template('table.html', items=items)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/chart')
@login_required
def chart():
    return render_template('chart.html')


@app.route('/rtvs')
@login_required
def rtvs():
    return render_template('rtvs.html')

@app.route('/rtvs', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    print(processed_text)
    return render_template('rtvs.html')

#https://stackoverflow.com/questions/55768789/how-to-read-in-user-input-on-a-webpage-in-flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

