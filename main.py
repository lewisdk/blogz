from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import current_user, LoginManager, login_user, logout_user
import cgi
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "super secret key"
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    blogs = db.relationship('Blog', backref='owner', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password 
    
    def __repr__(self):
        return f"User('{self.username}')"
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.id

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, blogtitle, content, owner):
        self.blogtitle = blogtitle
        self.content = content
        self.owner = owner

    def __repr__(self):
        return f"Blog('{self.blogtitle}', '{self.date_posted}'', {self.content}', '{self.owner}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


blogs = []
users = []

@app.before_request
def require_login():

    allowed_routes = ['login', 'index', 'signup', 'singleUser,' 'base']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.order_by(User.username.desc()).all()

    return render_template('index.html', users=users)

def logged_in_user():
    owner = User.query.filter_by(username=session['user']).first()
    return owner

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''
        verify_error = ''

        def good_username(username):
            username = request.form['username']

            if (len(username) > 3 and len(username) < 20):
                return True
            else:
                return False

        def good_password(password):
            password = request.form['password']

            if (len(password) > 3 and len(password) < 20):
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

        if existing_user:
            username_error = "Username exists. Try harder."
            return render_template('signup.html', username_error=username_error)
            

        if good_username(username) == False:
            username_error = 'That is not a valid username.'            
            return render_template('signup.html', username_error=username_error, username = '')    

        if good_password(password) == False:
            password_error = 'That is not a valid password.'
            return render_template('signup.html', password_error=password_error, password = '')

        if password_match(verify) == False:
            verify_error = 'Passwords do not match.'
            return render_template('signup.html', verify_error=verify_error, verify = '')

        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            flash('Your account has been created. You are now able to log in.')
            return redirect('login')
                
    return render_template('signup.html')   

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            if not user:
                flash('User does not exist', 'error')
                return redirect('/signup')
            else:
                flash('Password is incorrect', 'error')
                return redirect('/login')
            
    return render_template('login.html', title='login')     

# @app.route('/add')
# def add():
#     return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def add_new_post():
    if request.method == 'POST':
        blogtitle = request.form["blogtitle"]
        content = request.form["content"]
        owner = session['usernamer']
        
        if not blogtitle or not content:
            flash("All fields are required. Please try again.")
            return redirect(url_for('/newpost.html'))
        else:
            post = Blog(blogtitle, content, owner)

            db.session.add(post)
            db.session.commit()

            posted = '/blog/'+ str(post.id)
            
            flash('New entry was successfully posted!')

            return redirect(posted)
    return render_template('newpost.html')

@app.route('/singleUser/<username>')
def singleUser(username):
   user = User.query.filter_by(username=User.username).first()
    
   return render_template('singleUser.html', title='singleUser', user=user)

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id).one()

    return render_template('blog.html', blog_id=blog.id)

# @app.route('/blog/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     user = request.args.get('username')
#     return render_template('singleUser.html', user=user)

@app.route('/base')
def all_blogs():
    blogs = Blog.query.all()
    return render_template('base.html', blogs=blogs)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/base')



if __name__ == '__main__':
    app.run()