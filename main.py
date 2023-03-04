import os
from datetime import datetime
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, email_validator
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
#add database
#USER_DB = os.environ.get('USER_DB') 
PASSWORD = os.environ.get('PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{PASSWORD}@localhost/users'
#SECRET KEY saved in .env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') 
#initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    #create a string
    def __repr__(self): 
        return f'DB Name: {self.name}'

#CLASSES
#create a form class
class UserForm(FlaskForm): 
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    submit = SubmitField('Submit')


#ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>/', methods=['GET', 'POST'])
def user_profile(name):
    return render_template('user_profile.html', name=name)

@app.route('/add_user/', methods=['GET', 'POST'])
def sign_up(): 
    name = None
    email = None
    form = UserForm()
    #validate form
    if form.validate_on_submit(): 
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None: 
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''

        flash('User Added Successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('sign_up.html', form=form, name=name, our_users=our_users)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id): 
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST': 
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash('Error! There was an issue. Please try again.')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else: 
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!')

        our_users = Users.query.order_by(Users.date_added)
        return render_template('sign_up.html', form=form, name=name, our_users=our_users)

    except:
        flash('Whoops! There was a problem deleting the user. Please try again.')
        return render_template('sign_up.html', form=form, name=name, our_users=our_users)

#CUSTOM ERROR PAGES
#invalid URL
@app.errorhandler(404)
def page_not_found(e): 
    return render_template('404.html'), 404

#internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



if __name__ == '__main__': 
    app.run(debug=True)