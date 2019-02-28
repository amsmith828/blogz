from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(8000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged In")
            return redirect('/')
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            return '<h1>Duplicate User</h1>'

    return render_template('register.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if 'user' in request.args:
        user_id = request.args.get('user')
        blogs = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html', blogs=blogs, user_id=user_id)

    if 'id' in request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('view-blog.html', blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs, title="Blogz")


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_post.id))

    else:
        return render_template('new-blog.html', title='New Blog Post')


@app.route('/users', methods=['POST', 'GET'])
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user', methods=['POST', 'GET'])
def user_page():
    pass


if __name__ == '__main__':
    app.run()
