from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy

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

#@app.route('/index')

if __name__ == '__main__':
    app.run()