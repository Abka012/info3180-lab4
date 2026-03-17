import os

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app import app, db, login_manager
from app.forms import LoginForm, UploadForm
from app.models import UserProfile

###
# Routing for your application.
###


@app.route("/")
def home():
    """Render website's home page."""
    return render_template("home.html")


@app.route("/about/")
def about():
    """Render the website's about page."""
    return render_template("about.html", name="Mary Jane")


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        flash("File Saved", "success")
        return redirect(url_for("home"))

    return render_template("upload.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = db.session.execute(
            db.select(UserProfile).filter_by(username=username)
        ).scalar()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("You have successfully logged in.", "success")
            return redirect(url_for("upload"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Logout the current user."""
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("home"))


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


###
# Helper functions
###


def get_uploaded_images():
    """Iterate over the uploads folder and return a list of image filenames."""
    upload_folder = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"])
    images = []
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(file)
    return images


###
# Routes for displaying uploaded images
###


@app.route("/uploads/<filename>")
def get_image(filename):
    """Return a specific image from the upload folder."""
    return send_from_directory(
        os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"]), filename
    )


@app.route("/files")
@login_required
def files():
    """Render a page that lists all uploaded image files."""
    images = get_uploaded_images()
    return render_template("files.html", images=images)


###
# The functions below should be applicable to all Flask apps.
###


# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                "Error in the %s field - %s" % (getattr(form, field).label.text, error),
                "danger",
            )


@app.route("/<file_name>.txt")
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + ".txt"
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template("404.html"), 404
