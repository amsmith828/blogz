from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

"""The /blog route displays all the blog posts.

You're able to submit a new post at the /newpost route. After submitting a new post, your app displays the main blog page.

You have two templates, one each for the /blog (main blog listings) and /newpost (post new blog entry) views. Your templates should extend a base.html template which includes some boilerplate HTML that will be used on each page.

In your base.html template, you have some navigation links that link to the main blog page and to the add new blog page.

If either the blog title or blog body is left empty in the new post form, the form is rendered again, with a helpful error message and any previously-entered content in the same form inputs.
"""


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(8000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_id = request.args.get('id')

    if blog_id is None:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs, title="Build a Blog")
    else:
        blog = Blog.query.get(blog_id)
        return render_template('view-blog.html', blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_post.id))

    else:
        return render_template('new-blog.html', title='New Blog Post')


if __name__ == '__main__':
    app.run()
