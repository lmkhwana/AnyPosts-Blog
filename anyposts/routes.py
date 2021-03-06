from anyposts.models import User, Post, Comment
from anyposts import app, db, bcrypt, mail
from PIL import Image
import secrets
import os
from flask_mail import Message
from anyposts.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, CommentForm
from flask import abort, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page ,per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/register' ,methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(username = form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()

        flash(format('Account has been created, you can now login.'), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form )

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else  redirect(url_for('home'))
        else:
            flash(format('Login unsuccessful, please check the details you entered!'), 'danger')
        
    return render_template('login.html', title="Login", form=form )

@app.route('/about')
def about():
    return render_template('about.html',  title="About")

@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(path)

    return picture_fn

@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(format("Your account has been updated!"), 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Acoount', image_file=image_file, form=form)

@app.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(format("Post was submited!"), 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend="Create Post")

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['POST', 'GET'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash(format("Your post has been updated"), "success")
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title="Update Post", form=form, legend="Update Post")

    
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(format("Your post has been deleted"), "success")
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date.desc())\
        .paginate(page=page ,per_page=5)
    return render_template('user_posts.html', posts=posts, user=username)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                    sender='noreply@anyblog.com', 
                    recipients=[user.email])
    msg.body = format('To reset your password, visit the following link: http://127.0.0.1:5000/reset_password/' + token)
    mail.send(msg)

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed
        db.session.commit()

        flash(format('Your password has been updated, you can now login.'), 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/comment/<int:post_id>', methods=['POST', 'GET'])
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        flash(format("Comment Added!"), 'success')
    return render_template('comment.html', form=form, post=post)
        
