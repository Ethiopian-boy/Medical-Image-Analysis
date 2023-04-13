from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from werkzeug.utils import secure_filename
import os
from . import *

from PIL import Image
import io
import numpy as np
import tensorflow as tf
import cv2

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

@views.route('/pneumonia', methods=['POST', 'GET'])
def pneumonia():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/pneumonia.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('L')

        # Resize the image to the input size expected by the model
        img = img.resize((224, 224))

        # Convert the image to a numpy array
        x = np.array(img)
        x = np.stack((x,) * 3, axis=-1)
        x = tf.image.resize(x, [224, 224])
        x = np.array(x)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        threshold = 0.5
        label = np.where(pred >= threshold, 1, 0)
        result = int(label)
        if result == 0:
            output='The predictions are formal. There is no pneumonia detected'
        elif result == 1:
            output='PNEUMONIA detected!!!'
        return jsonify({'result': output})
    return render_template('deploy.html')


@views.route('/bones', methods=['POST', 'GET'])
def bones():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/bones.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('L')

        # Resize the image to the input size expected by the model
        img = img.resize((224, 224))

        # Convert the image to a numpy array
        x = np.array(img)
        x = np.stack((x,) * 3, axis=-1)
        x = tf.image.resize(x, [224, 224])
        x = np.array(x)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        threshold = 0.5
        label = np.where(pred >= threshold, 1, 0)
        result = int(label)
        if result == 0:
            output='Fracture detected !!!'
        elif result == 1:
            output='Everything seems right'
        return jsonify({'result': output})
    return render_template('deploy.html')



@views.route('/tuberculosis', methods=['POST', 'GET'])
def tuberculosis():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/tuberculosis.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('L')

        # Resize the image to the input size expected by the model
        img = img.resize((320, 320))

        # Convert the image to a numpy array
        x = np.array(img)
        x = np.stack((x,) * 3, axis=-1)
        x = tf.image.resize(x, [320, 320])
        x = np.array(x)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        threshold = 0.5
        label = np.where(pred >= threshold, 1, 0)
        result = int(label)
        if result == 0:
            output='Everything seems right'
        elif result == 1:
            output='TUBERCULOSIS detected!!!'
        return jsonify({'result': output})
    return render_template('deploy.html')



@views.route('/brainTumor', methods=['POST', 'GET'])
def brainTumor():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/brain-tumor.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('L')

        # Resize the image to the input size expected by the model
        img = img.resize((150, 150))

        # Convert the image to a numpy array
        x = np.array(img)
        x = np.stack((x,) * 3, axis=-1)
        x = tf.image.resize(x, [150, 150])
        x = np.array(x)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred[0])
        result = label
        result=int(result)
        if result == 0:
            output = 'We think you have a GLIOAMA'
        elif result==1:
            output='We think you have a MENINGIOMA'
        elif result==2:
            output='No tumor detected'
        elif result==3:
            output='We think you have a PITUITARY'

        return jsonify({'result': output})
    return render_template('deploy.html')






@views.route('/brainStroke', methods=['POST', 'GET'])
def brainStroke():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/brain_stroke_model.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('L')

        # Resize the image to the input size expected by the model
        img = img.resize((224, 224))

        # Convert the image to a numpy array
        x = np.array(img)
        x = np.stack((x,) * 3, axis=-1)
        x = tf.image.resize(x, [224, 224])
        x = np.array(x)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        threshold = 0.5
        label = np.argmax(pred)
        result = int(label)
        if result == 0:
            output='Everything seems right'
        elif result == 1:
            output='brain STroke detected!!!'
        return jsonify({'result': output})
    return render_template('deploy.html')