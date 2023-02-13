import os
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #key saved in .env

#CLASSES
#create a form class
class NameForm(FlaskForm): 
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')


#ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>/', methods=['GET', 'POST'])
def user(name):
    return render_template('user.html', name=name)

@app.route('/name/', methods=['GET', 'POST'])
def name(): 
    name = None
    form = NameForm()
    #validate form
    if form.validate_on_submit(): 
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully!')
    return render_template('name.html', name=name, form=form)


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