from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from .models import PendingStatus, Note, Birth_certificate, National_id_renewal, National_id_new, Driver_license_renewal
from . import db
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)
UPLOAD_FOLDER = '/website/static/uploads'

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

@views.route('/form', methods=['GET', 'POST'])
@login_required
def forms():
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

        photo = None
        birthPhoto = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file:
                filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{photo_file.filename.rsplit('.', 1)[1].lower()}")
                photo_file.save(os.path.join(UPLOAD_FOLDER, filename))
                photo = 'UPLOAD_FOLDER' + '/filename'


        if variable == 'driver_license_renewal' or variable == 'national_id_new' or variable == 'national_id_renewal':
            subCity = request.form.get('subCity')
            woreda = request.form.get('woreda')
            houseNumber = request.form.get('houseNumber')
            phoneNumber = request.form.get('phoneNumber')
            bloodType = request.form.get('bloodType')

        if variable == 'driver_license_renewal' or variable == 'national_id_renewal':
            expiryDate_str = request.form.get('expiryDate')
            expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()

        if variable == 'national_id_renewal' or variable == 'national_id_new':
            ecName = request.form.get('ecName')
            ecphoneNumber = request.form.get('ecphoneNumber')

        if variable == 'driver_license_renewal':
            grade = request.form.get('grade')
            new_driver_license_renewal = Driver_license_renewal(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, grade=grade, user_id=current_user.id)
            db.session.add(new_driver_license_renewal)
            db.session.commit()
            flash('Application completed!', category='success')
            return redirect(url_for('views.home'))
        
        if variable == 'birth_certificate':
            fatherfullName = request.form.get('fatherfullName')
            motherfullName = request.form.get('motherfullName')
            new_birth_certificate = Birth_certificate(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, fatherfullName=fatherfullName, motherfullName=motherfullName, user_id=current_user.id)
            db.session.add(new_birth_certificate)
            db.session.commit()
            flash('Application completed!', category='success')
            return redirect(url_for('views.home'))
        
        if variable == 'national_id_new':
            if 'birthPhoto' in request.files:
                birthPhoto_file = request.files['birthPhoto']
                if birthPhoto_file:
                    filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{birthPhoto_file.filename.rsplit('.', 1)[1].lower()}")
                    birthPhoto_file.save(os.path.join(UPLOAD_FOLDER, filename))
                    birthPhoto = 'UPLOAD_FOLDER' + '/filename'

            new_national_id_new = National_id_new(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, birthPhoto=birthPhoto, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
            db.session.add(new_national_id_new)
            db.session.commit()
            flash('Application completed!', category='success')
            return redirect(url_for('views.home'))
        
        if variable == 'national_id_renewal':
            new_national_id_renewal = National_id_renewal(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
            db.session.add(new_national_id_renewal)
            db.session.commit()
            flash('Application completed!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template("form.html", user=current_user, variable=variable)

@views.route('/applications', methods=['GET'])
@login_required
def applications():
    applied_pending_models = []

    table_models = [Driver_license_renewal, National_id_new, National_id_renewal, Birth_certificate]

    for table_model in table_models:
        table_name = table_model.__tablename__
        table_pending_status = table_model.query.filter_by(pending=PendingStatus.APPLIED_PENDING).first()
        if table_pending_status:
            applied_pending_models.append(table_name)

    return render_template('applications.html', tables=applied_pending_models, user=current_user)