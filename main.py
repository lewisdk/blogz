from flask import Flask, request, redirect, render_template, url_for, flash, session
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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, content, owner):
        self.blogtitle = blogtitle
        self.content = content
        self.owner= owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 


blogs = []
users = []

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

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
            
    return render_template('login.html')


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
            return redirect('/')
        else:
            return "<h1>Duplicate user</h1>"
    return render_template('signup.html')

@app.route('/blog')
def blog_page():
    blogs = request.args.get('blog')
    users = request.args.get('user')
    for blog in blogs:
        return render_template('blog.html', blogs=blogs)
    for user in users:
        return render_template('singleUser.html', user=user)

@app.route('/base')
def all_blogs():
    return render_template('base.html')

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id).one()

    return render_template('blog.html', blog=blog)

@app.route('/singleUser/<int:user_id>')
def singleUser(user_id):
    user = User.query.filter_by(id=user_id).one()
    blogs = Blog.query.all(user_id)

    return render_template('singleUser.html', user=user)

@app.route('/add')
def add():
    return render_template('newpost.html')


@app.route('/newpost', methods=['POST'])
def add_new_post():
    blogtitle = request.form["blogtitle"]
    content = request.form["content"]

    if not blogtitle or not content:
        flash("All fields are required. Please try again.")
        return redirect(url_for('/newpost.html'))
    else:

        post = Blog(blogtitle=blogtitle, content=content, owner=owner)

        db.session.add(post)
        db.session.commit()
        
        flash('New entry was successfully posted!')
        return redirect('/blog')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



if __name__ == '__main__':
    app.run()