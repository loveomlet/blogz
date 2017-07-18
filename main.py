from flask import request, redirect, render_template, session, flash, url_for
from app import app, db
from models import Blog, User


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


# TODO: fix static folder
@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    blog_owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':

        blog_title = request.form['blog']
        blog_body = request.form['blog-body']
        is_error = False

        if len(blog_title) < 1:
            flash('Your title must contain at least 1 character', 'error')
            is_error = True
        elif len(blog_body) < 1:
            flash('Your blog body must contain at least 1 character', 'error')
            is_error = True
        elif not is_error:
            new_blog = Blog(blog_title, blog_body, blog_owner.id)
            db.session.add(new_blog)
            db.session.commit()

            new_blog_id = new_blog.id
            url = "/blog?blog_id=" + str(new_blog_id)
            return redirect(url)

    return render_template('newpost.html', title="Add New Blog Post")


@app.route('/blog', methods=['GET'])
def blog():
    if request.args:
        user_username = request.args.get('user')
        blog_id = request.args.get('blog_id')

        if blog_id:
            blog = Blog.query.get(blog_id)
            return render_template('blog.html', blog=blog)
        elif user_username:
            user = User.query.filter_by(username=user_username).first()
            user_blogs = Blog.query.filter_by(owner_id=user.id).all()
            return render_template('blogs.html', blogs=user_blogs)

    posted_blogs = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blogs.html', blogs=posted_blogs)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        verify = request.form.get('verify')
        existing_user = User.query.filter_by(username=username).first()
        is_error = False

        if len(username) < 3 or len(username) > 20 or not username.isalnum():
            flash('Length of username must be 3-20 countinuous alpha/numeric characters', 'error')
            is_error = True
        elif len(password) < 3 or len(username) > 20 or (' ') in password:
            flash('Length of password must be 3-20 continuous characters', 'error')
            is_error = True
        elif verify != password:
            flash('Passwords do not match', 'error')
            is_error = True
        elif not existing_user and not is_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = username
            return redirect('/')
        else:
            flash('User already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/')
        else:
            flash('Username/password incorrect or user does not exist', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()
