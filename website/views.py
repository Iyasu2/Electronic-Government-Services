from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user, login_user, logout_user
from .models import PendingStatus, Birth_certificate, National_id, Driver_license_renewal, User
from . import db
import pytz
import requests
import base64
import os
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired

API_ID = os.environ.get('ZOOM_ID')
API_SECRET = os.environ.get('ZOOM_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/zoom_callback'

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
    applied_models = []

    table_models = [(Driver_license_renewal, 'Driver_license_renewal'), (National_id, 'National_id'), (Birth_certificate, 'Birth_certificate')]

    for table_model, table_name in table_models:
        table_pending_status = table_model.query.filter((table_model.pending == PendingStatus.APPLIED_PENDING) | (table_model.pending == PendingStatus.APPLIED_AWAITING_VERIFICATION)).all()
        for item in table_pending_status:
            user_id = item.user_id
            pending_status = item.pending.name
            applied_models.append((user_id, table_name, pending_status))

    grouped_applications = {}
    for user_id, table_name, pending_status in applied_models:
        if user_id in grouped_applications:
            grouped_applications[user_id].append((table_name, pending_status))
        else:
            grouped_applications[user_id] = [(table_name, pending_status)]
            
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
        fatherfullName_list = fatherfullName.split()
        motherfullName = request.form.get('motherfullName')
        motherfullName_list = motherfullName.split()
        
        if len(fatherfullName_list) != 3 or len(motherfullName_list) != 3:
            flash("Please give full name for the Father's or Mother's Full Name fields", category='error')
            return redirect(url_for('views.birth_certificate', button_type='button2'))

        file = request.files['fileInput']
        filename_parts = file.filename.rsplit('.', 1)
        if len(filename_parts) > 1:
            file_extension = filename_parts[1].lower()
        else:
            file_extension = ""
        filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}")
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER,filename))
        photo = UPLOAD_FOLDER + '/' + filename

        today = date.today()
        age = today.year - birthDay.year - ((today.month, today.day) < (birthDay.month, birthDay.day))
        if age < 18:
            flash('You must be 18 or older to apply.', category='error')
            return redirect(url_for('views.birth_certificate', button_type='button2'))

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
    user_id = request.args.get('user_id')
    pending_status = request.args.get('status', type=str)
    birth = Birth_certificate.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        table_name = Birth_certificate.__tablename__
        if action == 'approve':
            if pending_status != 'APPLIED_AWAITING_VERIFICATION':
                birth.pending = PendingStatus.APPLIED_AWAITING_VERIFICATION
                db.session.commit()
                flash('Application awaiting physical verification', category='success')
                return redirect(url_for('views.schedule_admin', user_id=user_id, table_name=table_name))
            else:
                date = request.form.get('datePicker')
                date_object = datetime.strptime(date, '%Y-%m-%d').date()
                # Check if the date is before the next day
                if date_object < datetime.now().date() + timedelta(days=1):
                    flash('You can only schedule from tomorrow onwards', category='error')
                    return redirect(url_for('views.birth_certificate_admin', user_id=user_id, status=pending_status))
                birth.pending = PendingStatus.APPLIED_ACCEPTED
                user = User.query.get(user_id)
                if user:
                    user.link = ''
                birth.Date1 = date_object
                db.session.commit()
                flash('Application accepted', category='success')
                return redirect(url_for('views.home_admin'))
            
        elif action == 'reject':
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    
    user_link = birth.link if birth else None
    date1 = birth.Date1 if birth else None
    time1 = birth.Time1 if birth else None
    return render_template("birth_certificate_admin.html", user=current_user, Birth_certificate=birth, status=pending_status, user_link=user_link, date1=date1, time1=time1)
    
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

        today = date.today()
        age = today.year - birthDay.year - ((today.month, today.day) < (birthDay.month, birthDay.day))
        if age < 18:
            flash('You must be 18 or older to apply.', category='error')
            return redirect(url_for('views.driver_license_renewal', button_type='button2'))

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
    user_id = request.args.get('user_id')
    pending_status = request.args.get('status', type=str)
    license = Driver_license_renewal.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        table_name = Driver_license_renewal.__tablename__
        if action == 'approve':
            if pending_status != 'APPLIED_AWAITING_VERIFICATION':
                license.pending = PendingStatus.APPLIED_AWAITING_VERIFICATION
                db.session.commit()
                flash('Application awaiting physical verification', category='success')
                return redirect(url_for('views.schedule_admin', user_id=user_id, table_name=table_name))
            else:
                date = request.form.get('datePicker')
                date_object = datetime.strptime(date, '%Y-%m-%d').date()
                # Check if the date is before the next day
                if date_object < datetime.now().date() + timedelta(days=1):
                    flash('You can only schedule from tomorrow onwards', category='error')
                    return redirect(url_for('views.driver_license_renewal_admin', user_id=user_id, status=pending_status))
                license.pending = PendingStatus.APPLIED_ACCEPTED
                user = User.query.get(user_id)
                if user:
                    user.link = ''
                license.Date1 = date_object
                db.session.commit()
                flash('Application accepted', category='success')
                return redirect(url_for('views.home_admin'))
        elif action == 'reject':
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    
    user_link = license.link if license else None
    
    date1 = license.Date1 if license else None
    time1 = license.Time1 if license else None
    return render_template("driver_license_renewal_admin.html", user=current_user, Driver_license_renewal=license, status=pending_status, user_link=user_link, date1=date1, time1=time1)
    
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

        today = date.today()
        age = today.year - birthDay.year - ((today.month, today.day) < (birthDay.month, birthDay.day))
        if age < 18:
            flash('You must be 18 or older to apply.', category='error')
            return redirect(url_for('views.national_id', button_type='button2'))

        new_national_id = National_id(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
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
            existing_national_id.ecName = ecName
            existing_national_id.ecphoneNumber = ecphoneNumber
        else:
            new_national_id = National_id(firstName=firstName, fatherName=fatherName, gfatherName=gfatherName, birthDay=birthDay, gender=gender, region=region, photo=photo, pending=pending, subCity=subCity, woreda=woreda, houseNumber=houseNumber, phoneNumber=phoneNumber, bloodType=bloodType, ecName=ecName, ecphoneNumber=ecphoneNumber, user_id=current_user.id)
            db.session.add(new_national_id)
        db.session.commit()
        flash('Application completed!', category='success')
        return redirect(url_for('views.home'))
    national = National_id.query.filter_by(user_id=current_user.id).first()
    return render_template("national_id.html", user=current_user, form=form, National_id=national, button_type=button_type)

@views.route('admin/form/national_id', methods=['GET', 'POST'])
@login_required
def national_id_admin():
    user_id = request.args.get('user_id')
    pending_status = request.args.get('status', type=str)
    national_id = National_id.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        table_name = National_id.__tablename__
        if action == 'approve':
            if pending_status != 'APPLIED_AWAITING_VERIFICATION':
                national_id.pending = PendingStatus.APPLIED_AWAITING_VERIFICATION
                db.session.commit()
                flash('Application awaiting physical verification', category='success')
                return redirect(url_for('views.schedule_admin', user_id=user_id, table_name=table_name))
            else:
                date = request.form.get('datePicker')
                date_object = datetime.strptime(date, '%Y-%m-%d').date()
                # Check if the date is before the next day
                if date_object < datetime.now().date() + timedelta(days=1):
                    flash('You can only schedule from tomorrow onwards', category='error')
                    return redirect(url_for('views.national_id_admin', user_id=user_id, status=pending_status))
                national_id.pending = PendingStatus.APPLIED_ACCEPTED
                user = User.query.get(user_id)
                if user:
                    user.link = ''
                national_id.Date1 = date_object
                db.session.commit()
                flash('Application accepted', category='success')
                return redirect(url_for('views.home_admin'))
        elif action == 'reject':
            return redirect(url_for('views.reject_admin', user_id=user_id, table_name=table_name))
    
    user_link = national_id.link if national_id else None
    date1 = national_id.Date1 if national_id else None
    time1 = national_id.Time1 if national_id else None
    return render_template("national_id_admin.html", user=current_user, National_id=national_id, status=pending_status, user_link=user_link, date1=date1, time1=time1)
    
@views.route('/applications', methods=['GET'])
@login_required
def applications():
    applied_models = []

    table_models = [Driver_license_renewal, National_id, Birth_certificate]
    user_link = ''
    i = 0

    for table_model in table_models:
        table_name = table_model.__tablename__
        table_pending_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_PENDING).first()
        if table_pending_status:
            table_id = table_pending_status.id
            applied_models.append((table_name, table_id, 'Pending', ''))

        table_accepted_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_ACCEPTED).first()
        if table_accepted_status:
            table_id = table_accepted_status.id
            table_date = table_accepted_status.Date1
            applied_models.append((table_name, table_id, 'Accepted', table_date))

        table_rejected_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_REJECTED).first()
        if table_rejected_status:
            
            table_id = table_rejected_status.id
            applied_models.append((table_name, table_id, 'Rejected', table_rejected_status.comment))
            print(applied_models)

        table_waiting_status = table_model.query.filter_by(user_id=current_user.id, pending=PendingStatus.APPLIED_AWAITING_VERIFICATION).first()
        if table_waiting_status:
            table_id = table_waiting_status.id
            user_link = table_waiting_status.link
            applied_models.append((table_name, table_id, 'Waiting', user_link))
            i += 1
            
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

@views.route('/admin/schedule', methods=['GET', 'POST'])
@login_required
def schedule_admin():
    possible_schedules = []
    user_id = request.args.get('user_id')
    table_name = request.args.get('table_name')
    if request.method == 'POST':
        date_format = "%Y-%m-%d"
        time_format = "%I:%M %p"
        for i in range(1, 6):
            date_str = request.form.get(f'date{i}')
            hour = request.form.get(f'hour{i}')
            minute = request.form.get(f'minute{i}')
            ampm = request.form.get(f'ampm{i}')
            time_str = hour + ":" + minute + " " + ampm

            if date_str and time_str:
                date = datetime.strptime(date_str, date_format).date()
                time = datetime.strptime(time_str, time_format).time()
                # Check if the date is before the next day
                if date < datetime.now().date() + timedelta(days=1):
                    flash('You can only schedule from tomorrow onwards', category='error')
                    return redirect(url_for('views.schedule_admin', user_id=user_id, table_name=table_name))
                possible_schedules.append((date, time))

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
            for i, schedule in enumerate(possible_schedules):
                date, time = schedule
                setattr(table, f'Date{i+1}', date)
                setattr(table, f'Time{i+1}', time)
            table.pending = PendingStatus.APPLIED_AWAITING_VERIFICATION
            db.session.commit()
            flash('Schedule sent. Waiting for user to choose', category='success')
            return redirect(url_for('views.home_admin'))
        else:
            # Handle the case when the table is not found
            flash('Table not found', category='error')

    return render_template('schedule_admin.html', user=current_user, user_id=user_id, table_name=table_name)

@views.route('/see_schedule', methods=['GET', 'POST'])
def see_schedule():
    user_id = current_user.id
    table_name = request.args.get('table_name')

    schedule_list = []

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
        for i in range(1, 6):
            date = getattr(table, f'Date{i}', None)
            time = getattr(table, f'Time{i}', None)
            if date and time:
                schedule_list.append((date, time))
    
    if request.method == 'POST':
        selected_schedule = request.form.get('schedule')
        if selected_schedule:
            selected_date, selected_time = selected_schedule.split(' ')
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            selected_time = datetime.strptime(selected_time, '%H:%M:%S').time()

            # Update the table with the selected date and time
            setattr(table, 'Date1', selected_date)
            setattr(table, 'Time1', selected_time)

            # Clear other dates and times
            for i in range(2, 6):
                setattr(table, f'Date{i}', None)
                setattr(table, f'Time{i}', None)

            db.session.commit()
            flash('Schedule saved successfully', category='success')
            return redirect(url_for('views.zoom', date=selected_date, time=selected_time, table_name=table_name, user_id=user_id))

    return render_template('see_schedule.html', user=current_user, table_name=table_name, schedule_list=schedule_list)

@views.route('/zoom', methods=['GET'])
def zoom():
    user_id = request.args.get('user_id')
    date_str = request.args.get('date')
    time_str = request.args.get('time')
    table_name = request.args.get('table_name')
    session['table_name'] = table_name
    session['user_id'] = user_id

    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    time = datetime.strptime(time_str, '%H:%M:%S').time()

    datetime_obj = datetime.combine(date, time)

    # You may need to adjust the timezone based on your requirements
    tz = pytz.timezone('Africa/Nairobi')
    datetime_obj = tz.localize(datetime_obj)

    # Generate the OAuth authorization URL
    authorization_url = f'https://zoom.us/oauth/authorize?response_type=code&client_id={API_ID}&redirect_uri={REDIRECT_URI}&table_name={table_name}&user_id={user_id}'

    # Store the date and time in session for later use
    session['date'] = date
    session['time'] = time_str

    # Redirect the user to the OAuth authorization URL
    return redirect(authorization_url)

@views.route('/zoom_callback', methods=['GET'])
def zoom_callback():
    user_id = session.get('user_id')
    variable = request.args.get('variable')
    table_name = session.get('table_name')
    table = None
    if variable == 'schedule_agreed':
        zoom_link = ''
        date_agreed = ''
        time_agreed = ''
        if table_name == 'national_id':
            table = National_id.query.filter_by(user_id=user_id).first()
        elif table_name == 'driver_license_renewal':
            table = Driver_license_renewal.query.filter_by(user_id=user_id).first()
        elif table_name == 'birth_certificate':
            table = Birth_certificate.query.filter_by(user_id=user_id).first()

        if table:
            date_agreed = table.Date1
            time_agreed = table.Time1
            zoom_link = table.link

        
        return render_template('zoom.html', user=current_user, zoom_link=zoom_link, date=date_agreed, time=time_agreed, table_name=table_name)

    code = request.args.get('code')
    

    # Exchange the authorization code for an access token
    token_url = 'https://zoom.us/oauth/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{API_ID}:{API_SECRET}".encode()).decode()}'
    }
    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        access_token = response.json().get('access_token')

        # Retrieve the stored date and time from session
        date = session.pop('date', None)
        time = session.pop('time', None)

        if access_token and date and time:
            date_obj = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z').date()
            datetime_obj = datetime.combine(date_obj, datetime.strptime(time, '%H:%M:%S').time())

            # You may need to adjust the timezone based on your requirements
            tz = pytz.timezone('Africa/Nairobi')
            datetime_obj = tz.localize(datetime_obj)

            # Generate the Zoom meeting link based on the datetime
            zoom_link = generate_zoom_link(access_token, datetime_obj)

            
            if table_name == 'national_id':
                table = National_id.query.filter_by(user_id=user_id).first()
            elif table_name == 'driver_license_renewal':
                table = Driver_license_renewal.query.filter_by(user_id=user_id).first()
            elif table_name == 'birth_certificate':
                table = Birth_certificate.query.filter_by(user_id=user_id).first()


            if table:
                table.link = zoom_link
            db.session.commit()

            # Redirect to the Zoom meeting link
            return render_template('zoom.html', user=current_user, zoom_link=zoom_link, date=date_obj, time=time, table_name=table_name)

    # Handle error case if the required data is missing
    return "Error: Missing required data"

def generate_zoom_link(access_token, datetime_obj):
    # Convert the datetime object to ISO 8601 format
    start_time = datetime_obj.isoformat()

    # Set up the meeting parameters
    meeting_params = {
        'topic': 'Physical verification',
        'type': 2,  # Scheduled meeting
        'start_time': start_time,
        'timezone': 'Africa/Nairobi',
        'password': '123456',  # Set your desired password
    }

    # Create the Zoom meeting using the API
    create_meeting_url = 'https://api.zoom.us/v2/users/me/meetings'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(create_meeting_url, json=meeting_params, headers=headers)
    if response.status_code == 201:
        meeting_data = response.json()
        meeting_id = meeting_data.get('id')
        zoom_link = f'https://zoom.us/j/{meeting_id}'


        # Return the generated Zoom meeting link
        return zoom_link

    # Handle error case if the meeting creation failed
    return "Error: Failed to create Zoom meeting"
