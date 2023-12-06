from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from .models import PendingStatus, Birth_certificate, National_id, Driver_license_renewal
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

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/admin/home', methods=['GET', 'POST'])
@login_required
def home_admin():
    applied_pending_models = []

    table_models = [(Driver_license_renewal, 'Driver_license_renewal'), (National_id, 'National_id'), (Birth_certificate, 'Birth_certificate')]

    for table_model, table_name in table_models:
        table_pending_status = table_model.query.filter_by(pending=PendingStatus.APPLIED_PENDING).all()
        for item in table_pending_status:
            user_id = item.user_id
            applied_pending_models.append((user_id, table_name))

    grouped_applications = {}
    for user_id, table_name in applied_pending_models:
        if user_id in grouped_applications:
            grouped_applications[user_id].append(table_name)
        else:
            grouped_applications[user_id] = [table_name]
            
    return render_template('home_admin.html', tables=grouped_applications, user=current_user)

@views.route('/', methods=['GET', 'POST'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    return render_template("landing.html", user=current_user)

@views.route('/delete', methods=['POST'])
@login_required
def delete_application():
    data = request.get_json()
    table_id = data['table_id']


    table_models = [Driver_license_renewal, National_id, Birth_certificate]
    for table_model in table_models:
        table = table_model.query.filter_by(user_id=current_user.id, id=table_id).first()
        if table:
            db.session.delete(table)
            db.session.commit()
            flash('Application deleted successfully.', category='success')
            return redirect(url_for('views.applications', user_id=current_user.id))

    flash('Table not found.', category='error')
    return redirect(url_for('views.applications'))

@views.route('/form/birth_certificate', methods=['GET', 'POST'])
@login_required
def birth_certificate():
    button_type = request.args.get('button_type')
    if button_type == 'button2':
        existing_application = Birth_certificate.query.filter_by(user_id=current_user.id).first()
        if existing_application and existing_application.pending in [PendingStatus.APPLIED_PENDING, PendingStatus.APPLIED_ACCEPTED]:
            flash('Application already exists!', category='error')
            return redirect(url_for('views.home'))
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
        
        file = request.files['fileInput']
        filename_parts = file.filename.rsplit('.', 1)
        if len(filename_parts) > 1:
            file_extension = filename_parts[1].lower()
        else:
            file_extension = ""
        filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}")
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
        photo = UPLOAD_FOLDER + '/' + filename

        existing_birth_certificate = Birth_certificate.query.filter_by(user_id=current_user.id).first()
        if existing_birth_certificate:
            existing_birth_certificate.firstName = firstName
            existing_birth_certificate.fatherName = fatherName
            existing_birth_certificate.gfatherName = gfatherName
            existing_birth_certificate.birthDay = birthDay
            existing_birth_certificate.gender = gender
            existing_birth_certificate.region = region
            if file:
                existing_birth_certificate.photo = photo
            existing_birth_certificate.pending = pending
            existing_birth_certificate.fatherfullName = fatherfullName
            existing_birth_certificate.motherfullName = motherfullName
        else:
            new_birth_certificate = Birth_certificate(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, fatherfullName=fatherfullName, motherfullName=motherfullName, user_id=current_user.id)
            db.session.add(new_birth_certificate)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    birth = Birth_certificate.query.filter_by(user_id=current_user.id).first()
    return render_template("birth_certificate.html", user=current_user, form=form, Birth_certificate=birth, button_type=button_type)

@views.route('admin/form/birth_certificate', methods=['GET', 'POST'])
@login_required
def birth_certificate_admin():
    user_id = request.args.get('user_id', type=int)
    birth = Birth_certificate.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            birth.pending = PendingStatus.APPLIED_ACCEPTED
            db.session.commit()
            flash('Application approved', category='success')
            return redirect(url_for('views.home_admin'))
        elif action == 'reject':
            table_name = Birth_certificate.__tablename__
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    return render_template("birth_certificate_admin.html", user=current_user, Birth_certificate=birth)
    
@views.route('/form/driver_license_renewal', methods=['GET', 'POST'])
@login_required
def driver_license_renewal():
    button_type = request.args.get('button_type')
    if button_type == 'button2':
        existing_application = Driver_license_renewal.query.filter_by(user_id=current_user.id).first()
        if existing_application and existing_application.pending in [PendingStatus.APPLIED_PENDING, PendingStatus.APPLIED_ACCEPTED]:
            flash('Application already exists!', category='error')
            return redirect(url_for('views.home'))
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
        subCity = request.form.get('subCity')
        woreda = request.form.get('woreda')
        houseNumber = request.form.get('houseNumber')
        phoneNumber = request.form.get('phoneNumber')
        bloodType = request.form.get('bloodType')
        expiryDate_str = request.form.get('expiryDate')
        expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()
        grade = request.form.get('grade')
        file = request.files['fileInput']
        filename_parts = file.filename.rsplit('.', 1)
        if len(filename_parts) > 1:
            file_extension = filename_parts[1].lower()
        else:
            file_extension = ""
        filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}")
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
        photo = UPLOAD_FOLDER + '/' + filename

        existing_driver_license_renewal = Driver_license_renewal.query.filter_by(user_id=current_user.id).first()
        if existing_driver_license_renewal:
            existing_driver_license_renewal.firstName = firstName
            existing_driver_license_renewal.fatherName = fatherName
            existing_driver_license_renewal.gfatherName = gfatherName
            existing_driver_license_renewal.birthDay = birthDay
            existing_driver_license_renewal.gender = gender
            existing_driver_license_renewal.region = region
            if file:
                existing_driver_license_renewal.photo = photo
            existing_driver_license_renewal.pending = pending
            existing_driver_license_renewal.subCity = subCity
            existing_driver_license_renewal.woreda = woreda
            existing_driver_license_renewal.houseNumber = houseNumber
            existing_driver_license_renewal.phoneNumber = phoneNumber
            existing_driver_license_renewal.bloodType = bloodType
            existing_driver_license_renewal.expiryDate = expiryDate
            existing_driver_license_renewal.grade = grade
        else:
            new_driver_license_renewal = Driver_license_renewal(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, grade=grade, user_id=current_user.id)
            db.session.add(new_driver_license_renewal)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    license = Driver_license_renewal.query.filter_by(user_id=current_user.id).first()
    return render_template("driver_license_renewal.html", user=current_user, form=form, Driver_license_renewal=license, button_type=button_type)

@views.route('admin/form/driver_license_renewal', methods=['GET', 'POST'])
@login_required
def driver_license_renewal_admin():
    user_id = request.args.get('user_id', type=int)
    license = Driver_license_renewal.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            license.pending = PendingStatus.APPLIED_ACCEPTED
            db.session.commit()
            flash('Application approved', category='success')
            return redirect(url_for('views.home_admin'))
        elif action == 'reject':
            table_name = Driver_license_renewal.__tablename__
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    
    return render_template("driver_license_renewal_admin.html", user=current_user, Driver_license_renewal=license)
    
@views.route('/form/national_id', methods=['GET', 'POST'])
@login_required
def national_id():
    button_type = request.args.get('button_type')
    if button_type == 'button2':
        existing_application = National_id.query.filter_by(user_id=current_user.id).first()
        if existing_application and existing_application.pending in [PendingStatus.APPLIED_PENDING, PendingStatus.APPLIED_ACCEPTED]:
            flash('Application already exists!', category='error')
            return redirect(url_for('views.home'))
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
        subCity = request.form.get('subCity')
        woreda = request.form.get('woreda')
        houseNumber = request.form.get('houseNumber')
        phoneNumber = request.form.get('phoneNumber')
        bloodType = request.form.get('bloodType')
        expiryDate_str = request.form.get('expiryDate')
        expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()
        ecName = request.form.get('ecName')
        ecphoneNumber = request.form.get('ecphoneNumber')
        file = request.files['fileInput']
        filename_parts = file.filename.rsplit('.', 1)
        if len(filename_parts) > 1:
            file_extension = filename_parts[1].lower()
        else:
            file_extension = ""
        filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}")
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
        photo = UPLOAD_FOLDER + '/' + filename

        new_national_id = National_id(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
        existing_national_id = National_id.query.filter_by(user_id=current_user.id).first()
        if existing_national_id:
            existing_national_id.firstName = firstName
            existing_national_id.fatherName = fatherName
            existing_national_id.gfatherName = gfatherName
            existing_national_id.birthDay = birthDay
            existing_national_id.gender = gender
            existing_national_id.region = region
            if file:
                existing_national_id.photo = photo
            existing_national_id.pending = pending
            existing_national_id.subCity = subCity
            existing_national_id.woreda = woreda
            existing_national_id.houseNumber = houseNumber
            existing_national_id.phoneNumber = phoneNumber
            existing_national_id.bloodType = bloodType
            existing_national_id.expiryDate = expiryDate
            existing_national_id.ecName = ecName
            existing_national_id.ecphoneNumber = ecphoneNumber
        else:
            new_national_id = National_id(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, expiryDate=expiryDate, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
            db.session.add(new_national_id)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    national = National_id.query.filter_by(user_id=current_user.id).first()
    return render_template("national_id.html", user=current_user, form=form, National_id=national, button_type=button_type)

@views.route('admin/form/national_id', methods=['GET', 'POST'])
@login_required
def national_id_admin():
    user_id = request.args.get('user_id', type=int)
    national_id = National_id.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            national_id.pending = PendingStatus.APPLIED_ACCEPTED
            db.session.commit()
            flash('Application approved', category='success')
            return redirect(url_for('views.home_admin'))
        elif action == 'reject':
            table_name = National_id.__tablename__
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    
    return render_template("national_id_admin.html", user=current_user, National_id=national_id)
    
@views.route('/applications', methods=['GET'])
@login_required
def applications():
    applied_models = []

    table_models = [Driver_license_renewal, National_id, Birth_certificate]

    for table_model in table_models:
        table_name = table_model.__tablename__
        table_pending_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_PENDING).first()
        if table_pending_status:
            table_id = table_pending_status.id
            applied_models.append((table_name, table_id, 'Pending', ''))

        table_accepted_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_ACCEPTED).first()
        if table_accepted_status:
            table_id = table_accepted_status.id
            applied_models.append((table_name, table_id, 'Accepted', ''))

        table_rejected_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_REJECTED).first()
        if table_rejected_status:
            table_id = table_rejected_status.id
            applied_models.append((table_name, table_id, 'Rejected', table_rejected_status.comment))
            
    return render_template('applications.html', tables=applied_models, user=current_user)

@views.route('/admin/reject', methods=['GET', 'POST'])
@login_required
def reject_admin():
    user_id = request.args.get('user_id')
    table_name = request.args.get('table_name')
    if request.method == 'POST':
        button_type = request.form.get('action')
        if button_type == 'close':
            return redirect(url_for('views.home_admin'))
        elif button_type == 'submit':
            comment = request.form.get('comment')

            if table_name == 'national_id':
                table = National_id.query.filter_by(user_id=user_id).first()
            elif table_name == 'driver_license_renewal':
                table = Driver_license_renewal.query.filter_by(user_id=user_id).first()
            elif table_name == 'birth_certificate':
                table = Birth_certificate.query.filter_by(user_id=user_id).first()
            else:
                # Handle the case when the table name is not recognized
                flash('Invalid table name', category='error')
                return redirect(url_for('views.home_admin'))
            if table:
                table.comment = comment
                table.pending = PendingStatus.APPLIED_REJECTED
                db.session.commit()
                flash('Application rejected', category='error')
                return redirect(url_for('views.home_admin'))
            else:
                # Handle the case when the table is not found
                flash('Table not found', category='error')

    return render_template('reject_admin.html', user=current_user, user_id=user_id, table_name=table_name)