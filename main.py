from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "super secret key"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(50))
    content = db.Column(db.Text)
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, content):
        self.blogtitle = blogtitle
        self.content = content
        self.owner = owner 

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 


blogs = []

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('', blogs=blogs)

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id).one()

    return render_template('blog.html', blog=blog)

@app.route('/add')
def add():
    return render_template('newpost.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/base')
    render_template('signup.html')

def good_username(username):
    username = request.form['username']

    if (len(username) > 3 and len(username) < 15):
        return True
    else:
        return False

def good_password(password):
    password = request.form['password']

    if (len(password) > 3 and len(password) < 15):
        if (" ") in password:
            return True
    else:
        return False 

def password_match(verify):
    verify = request.form['verify']
    password = request.form['password']

    if [password] == [verify]:
        return True
    else:
        return False

@app.route("/", methods=['POST'])
def validate_form():
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']

    username_error = ''
    password_error = ''
    verify_error = ''
    email_error=''

    if good_username(username) == False:
        username_error = 'That is not a valid username.'
        username = ''

    if good_password(password) == False:
        password_error = 'That is not a valid password.'
        password = ''

    if password_match(verify) == False:
        verify_error = 'Passwords do not match.'
        verify = ''
    if not username_error and not password_error and not verify_error:
            return redirect('/newpost')
    else:
        template = render_template('index.html')
        return template.render(username_error=username_error, password_error=password_error, 
            verify_error=verify_error, 
            username = username,
            password = '',
            verify = '')

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("logged in")
            return redirect('/newpost')
        else:
            if user and user.password != password:
                flash('User password incorrect', 'error')
                return redirect('/login')
            else:
                if not username:
                    flash('Username does not exist, please create an account.', 'error')
                    return('/signup')
    return render_template('login.html')

@app.route('/newpost', methods=['POST'])
def add_new_post():
    blogtitle = request.form["blogtitle"]
    content = request.form["content"]

    if not blogtitle or not content:
        flash("All fields are required. Please try again.")
        return redirect(url_for('/newpost.html'))
    else:

        post = Blog(blogtitle=blogtitle, content=content)

        db.session.add(post)
        db.session.commit()
        
        flash('New entry was successfully posted!')
        return redirect('/')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



if __name__ == '__main__':
    app.run()