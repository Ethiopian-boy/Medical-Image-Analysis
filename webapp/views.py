from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from werkzeug.utils import secure_filename
import os
from . import *

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            # providing the schema for the note
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)  # adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')
            
    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    # this function expects a JSON from the INDEX.js file
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
@views.route('d1')
def d1():
    #model, predict function
    return render_template('predict.html')


@views.route('d2')
def d2():
    return render_template('predict.html')


@views.route('/about')
def about():
    return render_template("about.html")


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#@views.route('/upload')
#def upload_form():
#    return render_template('upload.html')

@views.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if 'files[]' not in request.files:
        flash('No file selected')
        return redirect(url_for("views.home"))
    files = request.files.getlist('files[]')
    file_names = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_names.append(filename)
            from main import app
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,
                                   app.config['UPLOAD_FOLDER'], filename))
            #if current_user.id = 
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

    return render_template('home.html', filenames=file_names)


@views.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

#@views.route('/delete-image', methods=['POST'])
#def delete_image(filename):
    