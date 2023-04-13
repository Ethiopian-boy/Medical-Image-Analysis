from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
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

import pandas as pd
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

views = Blueprint('views', __name__)
cnx = mysql.connector.connect(user='admin', database='ecom', password='Elviskhorem12!?', host='127.0.0.1')
cursor = cnx.cursor(buffered=True)


@views.route('/', methods=['GET', 'POST'])
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
    # model, predict function
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


# @views.route('/upload')
# def upload_form():
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
            # if current_user.id =
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

    return render_template('home.html', filenames=file_names)


@views.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@views.route('/xray')
def xray():
    return render_template('xray_diseases.html')


@views.route('/ctScan')
def ctScan():
    return render_template('CT_scan.html')


@views.route('/photogenic')
def photogenic():
    return render_template('photogenic_disease.html')


# @views.route('/delete-image', methods=['POST'])
# def delete_image(filename):

@views.route('/pneumonia', methods=['POST', 'GET'])
def pneumonia():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/pneumonia.h5')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        # Read the file from the request
        file = request.files['image'].read()
        filename = request.files['image'].filename
        save_path = os.path.join('static/uploads', filename)
        path = os.path.join('webapp', save_path)
        with open(path, 'wb+') as f:
            f.write(file)
        query = "SELECT last_name FROM image_analysis.doctors WHERE id=1"

        cursor.execute(query)
        doctor = cursor.fetchone()[0]
        doctor = str(doctor)

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
        output = ''
        text = ''
        if result == 0:
            output='No Pneumonia'
            text = 'The predictions are formal. There is no pneumonia detected'
        elif result == 1:
            output = 'Pneumonia'
            text = 'PNEUMONIA detected!!!'
        add_record = ("INSERT INTO image_analysis.report"
                      "(patient_name, patient_age, image_path, doctor_name, diagnosis) "
                      "VALUES (%s, %s, %s, %s, %s)")

        cursor.execute(add_record, (name, age, path, doctor, output))
        cnx.commit()
        return redirect(url_for('views.result', text=text, output=output, name=name))
    return render_template('analayse.html')


@views.route('result/<text>/<name>/<output>')
def result(text, output, name):
    query = "SELECT recommendation FROM image_analysis.recommendation WHERE disease_name=%s"
    values = (output,)
    cursor.execute(query, values)
    recommendation = cursor.fetchone()
    recommendation = recommendation[0].replace('\n', '<br>').replace('"', '')
    add_record = ("UPDATE image_analysis.report SET recommendation = %s where patient_name=%s")
    cursor.execute(add_record, (recommendation, name))
    # Retrieve the data from the SQL table
    query = "SELECT patient_name, patient_age, doctor_name, diagnosis, recommendation FROM image_analysis.report WHERE patient_name=%s"
    values = (name,)
    cursor.execute(query, values)
    data = cursor.fetchall()
    recommend=data[0][4].replace('<br>', '\n')

    df = pd.DataFrame(data, columns=['Patient Name', 'Patient age', 'Doctor name', 'Diagnosis', 'Recommendation'])

    # Create a PDF file
    pdf_file = f'/home/belvisk/PycharmProjects/Medical-Image-Analysis/webapp/static/report/reportPatient'

    canva = canvas.Canvas(pdf_file, pagesize=letter)

    # Loop over the DataFrame and add a section for each row
    for i, row in df.iterrows():
        # Add a page break between sections
        if i > 0:
            canva.showPage()

        # Add the disease result to the PDF header
        disease = row['Diagnosis']
        canva.setFont('Helvetica-Bold', 14)
        canva.drawString(50, 750, 'Diagnosis: ' + disease)

        # Add the patient name and age to the PDF header
        patient_name = row['Patient Name']
        patient_age = row['Patient age']
        canva.setFont('Helvetica', 12)
        canva.drawString(50, 725, 'Patient: ' + patient_name + ', ' + str(patient_age))

        # Add the doctor name to the PDF header
        doctor_name = row['Doctor name']
        canva.drawString(50, 710, 'Doctor: ' + doctor_name)

        # Add the treatment and recommendation to the PDF body
        canva.setFont('Helvetica', 12)
        canva.drawString(50, 670, 'Treatment: ')

        # Split the treatment text into multiple lines
        treatment_lines = textwrap.wrap(recommend, width=60)
        y = 650
        for line in treatment_lines:
            canva.drawString(150, y, line)
            y -= 15

        # canva.drawString(50, y - 15, 'Recommendation: ')
        #
        # # Split the recommendation text into multiple lines
        # # Check if there is a recommendation for this row
        # if row['Recommendation'] is not None:
        #     # Split the treatment text into multiple lines
        #     treatment_lines = textwrap.wrap(row['Recommendation'], width=60)
        #     y = 650
        #     for line in treatment_lines:
        #         canva.drawString(150, y, line)
        #         y -= 15
        #
        #     canva.drawString(50, y - 15, 'Recommendation: ')
        #
        #     # Split the recommendation text into multiple lines
        #     recommendation_lines = textwrap.wrap(row['Recommendation'], width=60)
        #     y -= 30
        #     for line in recommendation_lines:
        #         canva.drawString(150, y, line)
        #         y -= 15
        # else:
        #     # If there is no recommendation, print a message
        #     canva.drawString(50, 650, 'No recommendation found for this patient')

    # Save the PDF file
    canva.save()



    return render_template('result.html', message=text, recommendation=recommendation)

@views.route('/download/', methods=['GET'])
def download_report():
    filename = f'/home/belvisk/PycharmProjects/Medical-Image-Analysis/webapp/static/report/reportPatient'
    return send_file(filename, as_attachment=True)

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
            output = 'Fracture detected !!!'
        elif result == 1:
            output = 'Everything seems right'
        return jsonify({'result': output})
    return render_template('analayse.html')


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
            output = 'Everything seems right'
        elif result == 1:
            output = 'TUBERCULOSIS detected!!!'
        return jsonify({'result': output})
    return render_template('analayse.html')


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
        result = int(result)
        if result == 0:
            output = 'We think you have a GLIOAMA'
        elif result == 1:
            output = 'We think you have a MENINGIOMA'
        elif result == 2:
            output = 'No tumor detected'
        elif result == 3:
            output = 'We think you have a PITUITARY'

        return jsonify({'result': output})
    return render_template('analayse.html')


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
            output = 'Everything seems right'
        elif result == 1:
            output = 'brain STroke detected!!!'
        return jsonify({'result': output})
    return render_template('analayse.html')


@views.route('/chestCancer', methods=['POST', 'GET'])
def chestCancer():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/chest_cancer_classifier.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('RGB')

        # Resize the image to the input size expected by the model
        img = img.resize((256, 256))

        # Convert the image to a numpy array
        x = np.array(img)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred)
        result = label
        result = int(result)
        if result == 0:
            output = 'We think you have a adenocarcinoma'
        elif result == 1:
            output = 'We think you have a large_cell_carcinoma'
        elif result == 2:
            output = 'normal'
        elif result == 3:
            output = 'We think you have squamous_cell_carcinoma'

        return jsonify({'result': output})
    return render_template('analayse.html')


@views.route('/breastCancer', methods=['POST', 'GET'])
def breastCancer():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/breast_cancer_classifier.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('RGB')

        # Resize the image to the input size expected by the model
        img = img.resize((256, 256))

        # Convert the image to a numpy array
        x = np.array(img)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred)
        result = label
        result = int(result)
        if result == 0:
            output = 'benign'
        elif result == 1:
            output = 'malignant'

        return jsonify({'result': output})
    return render_template('analayse.html')


@views.route('/leukemia', methods=['POST', 'GET'])
def leukemia():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/leukemia_model.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('RGB')

        # Resize the image to the input size expected by the model
        img = img.resize((224, 224))

        # Convert the image to a numpy array
        x = np.array(img)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred)
        result = label
        result = int(result)
        if result == 0:
            output = 'benign'
        elif result == 1:
            output = 'pre'
        elif result == 2:
            output = 'early'
        elif result == 3:
            output = 'pro'

        return jsonify({'result': output})
    return render_template('analayse.html')


@views.route('/lungCancer', methods=['POST', 'GET'])
def lungCancer():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/lung_cancer_model.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('RGB')

        # Resize the image to the input size expected by the model
        img = img.resize((256, 256))

        # Convert the image to a numpy array
        x = np.array(img)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred)
        result = label
        result = int(result)
        if result == 0:
            output = 'benign'
        elif result == 1:
            output = 'malignant'
        elif result == 2:
            output = 'normal'

        return jsonify({'result': output})
    return render_template('analayse.html')


@views.route('/oralCancer')
def oralCancer():
    model = tf.keras.models.load_model('/home/belvisk/Documents/models/oral_cancer_model.h5')
    if request.method == 'POST':

        # Read the file from the request
        file = request.files['file'].read()

        # Convert the file to an image
        img = Image.open(io.BytesIO(file))
        img = img.convert('RGB')

        # Resize the image to the input size expected by the model
        img = img.resize((224, 224))

        # Convert the image to a numpy array
        x = np.array(img)

        # Normalize the pixel values
        x = x / 255.0

        # Add a batch dimension to the array
        x = np.expand_dims(x, axis=0)

        # Make the prediction
        pred = model.predict(x)
        label = np.argmax(pred)
        result = label
        result = int(result)
        if result == 0:
            output = 'normal'
        elif result == 1:
            output = 'Oral Cancer'

        return jsonify({'result': output})
    return render_template('analayse.html')
