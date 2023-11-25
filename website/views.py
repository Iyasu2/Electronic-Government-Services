from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from .models import PendingStatus, Note, Birth_certificate, National_id, Driver_license_renewal
from . import db
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired

views = Blueprint('views', __name__)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_file_dir, 'static/uploads')

class UploadFileForm(FlaskForm):
    file = FileField("FILE", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            return jsonify({})

@views.route('/form/birth_certificate', methods=['GET', 'POST'])
@login_required
def birth_certificate():
    form = UploadFileForm()
    photo = None
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        fatherName = request.form.get('fatherName')
        gfatherName = request.form.get('gfatherName')
        birthDay_str = request.form.get('birthDay')
        birthDay = datetime.strptime(birthDay_str, '%Y-%m-%d').date()
        gender = request.form.get('gender')
        region = request.form.get('region')
        pending = PendingStatus.APPLIED_PENDING
        fatherfullName = request.form.get('fatherfullName')
        motherfullName = request.form.get('motherfullName')
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
            photo = UPLOAD_FOLDER + '/' + filename

        new_birth_certificate = Birth_certificate(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, fatherfullName=fatherfullName, motherfullName=motherfullName, user_id=current_user.id)
        db.session.add(new_birth_certificate)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    return render_template("birth_certificate.html", user=current_user, form=form)
    
@views.route('/form/driver_license_renewal', methods=['GET', 'POST'])
@login_required
def driver_license_renewal():
    form = UploadFileForm()
    photo = None
    variable = request.args.get('variable')
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        fatherName = request.form.get('fatherName')
        gfatherName = request.form.get('gfatherName')
        birthDay_str = request.form.get('birthDay')
        birthDay = datetime.strptime(birthDay_str, '%Y-%m-%d').date()
        gender = request.form.get('gender')
        region = request.form.get('region')
        pending = PendingStatus.APPLIED_PENDING
        subCity = request.form.get('subCity')
        woreda = request.form.get('woreda')
        houseNumber = request.form.get('houseNumber')
        phoneNumber = request.form.get('phoneNumber')
        bloodType = request.form.get('bloodType')
        expiryDate_str = request.form.get('expiryDate')
        expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()
        grade = request.form.get('grade')
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
            photo = UPLOAD_FOLDER + '/' + filename

        new_driver_license_renewal = Driver_license_renewal(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, grade=grade, user_id=current_user.id)
        db.session.add(new_driver_license_renewal)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    return render_template("driver_license_renewal.html", user=current_user, form=form)
    
@views.route('/form/national_id', methods=['GET', 'POST'])
@login_required
def national_id():
    form = UploadFileForm()
    photo = None
    variable = request.args.get('variable')
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        fatherName = request.form.get('fatherName')
        gfatherName = request.form.get('gfatherName')
        birthDay_str = request.form.get('birthDay')
        birthDay = datetime.strptime(birthDay_str, '%Y-%m-%d').date()
        gender = request.form.get('gender')
        region = request.form.get('region')
        pending = PendingStatus.APPLIED_PENDING
        subCity = request.form.get('subCity')
        woreda = request.form.get('woreda')
        houseNumber = request.form.get('houseNumber')
        phoneNumber = request.form.get('phoneNumber')
        bloodType = request.form.get('bloodType')
        expiryDate_str = request.form.get('expiryDate')
        expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()
        ecName = request.form.get('ecName')
        ecphoneNumber = request.form.get('ecphoneNumber')
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
            photo = UPLOAD_FOLDER + '/' + filename

        new_national_id = National_id(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
        db.session.add(new_national_id)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    return render_template("national_id.html", user=current_user, form=form)
    
@views.route('/applications', methods=['GET'])
@login_required
def applications():
    applied_pending_models = []

    table_models = [Driver_license_renewal, National_id, Birth_certificate]

    for table_model in table_models:
        table_name = table_model.__tablename__
        table_pending_status = table_model.query.filter_by(pending=PendingStatus.APPLIED_PENDING).first()
        if table_pending_status:
            applied_pending_models.append(table_name)

    return render_template('applications.html', tables=applied_pending_models, user=current_user)