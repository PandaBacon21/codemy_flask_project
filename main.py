import os
from datetime import datetime
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, email_validator, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

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


# DB Models
# USERS DATABASE MODEL
class Users(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #password section
    password_hash = db.Column(db.String(128))

    @property
    def password(self): 
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #create a string repr
    def __repr__(self): 
        return f'DB Name: {self.name}'


# BLOG POST DATABASE MODEL
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    

#FORMS
#create a User Form
class UserForm(FlaskForm): 
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), 
                                                          EqualTo('password_hash2', 
                                                          message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a POST Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField()


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
            #hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data.title(),
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User Added Successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('sign_up.html', form=form, name=name, our_users=our_users)


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
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


@app.route('/delete/<int:id>/')
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


@app.route('/add-post/', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit(): 
        post = Posts(title=form.title.data, content=form.content.data, 
                     author=form.author.data, slug=form.slug.data)
        # Clear Form
        form.title.data = ''
        form.content.data = ''
        form.author.date = ''
        form.slug.data = ''

        # Add Post data to database
        db.session.add(post)
        db.session.commit()

        # Return Message
        flash('Blog Post Submitted Successfully!')

    # Redirect to webpage
    return render_template('add_post.html', form=form)




# PASSWORD TEST - Will remove
@app.route('/test_pw/', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    #validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # clear the form data
        form.email.data = ''
        form.password_hash.data = ''

        #check user against database by email
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hashed PW
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password=password, 
                           pw_to_check=pw_to_check, passed=passed, form=form)


# JSON Demo - Will DELETE
@app.route('/date/')
def get_current_data():
    favorite_pizza = {
        'Josh': 'Pepperoni', 
        'Kerry': 'Cheese'
    }
    return favorite_pizza


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