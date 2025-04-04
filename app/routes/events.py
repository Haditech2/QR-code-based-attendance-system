import os
import qrcode
import pytz
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app.models.event import Event
from app import db

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
@login_required
def index():
    if current_user.role == 'teacher':
        events = Event.query.filter_by(creator_id=current_user.id).order_by(Event.start_time.desc()).all()
    else:
        events = Event.query.order_by(Event.start_time.desc()).all()
    return render_template('events/index.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        # Convert to UTC
        utc = pytz.utc
        try:
            local_tz = pytz.timezone('Africa/Lagos')  # Adjust timezone as needed
            start_time_local = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time_local = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            
            start_time_utc = local_tz.localize(start_time_local).astimezone(utc)
            end_time_utc = local_tz.localize(end_time_local).astimezone(utc)
            
            event = Event(
                title=title,
                description=description,
                start_time=start_time_utc,
                end_time=end_time_utc,
                creator_id=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            attendance_url = f"{request.host_url}attendance/mark/{event.id}"
            qr.add_data(attendance_url)
            qr.make(fit=True)
            
            # Ensure the qrcodes directory exists
            qr_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
            os.makedirs(qr_dir, exist_ok=True)
            
            # Generate the QR code image
            qr_path = f'qrcodes/event_{event.id}.png'
            full_path = os.path.join(qr_dir, f'event_{event.id}.png')
            
            try:
                qr.make_image(fill_color="black", back_color="white").save(full_path)
                event.qr_code_path = qr_path
                db.session.commit()
                flash('Event created successfully!')
                return redirect(url_for('events.index'))
            except Exception as e:
                print(f"Error generating QR code: {str(e)}")
                flash('Error generating QR code. Please try again.')
                return redirect(url_for('events.index'))
                
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            flash('Error creating event. Please check the date and time format.')
            return redirect(url_for('events.create'))
    
    return render_template('events/create.html')

@bp.route('/<int:id>')
@login_required
def view(id):
    event = Event.query.get_or_404(id)
    if current_user.role == 'teacher' and event.creator_id != current_user.id:
        flash('You do not have permission to view this event.')
        return redirect(url_for('events.index'))
    return render_template('events/view.html', event=event)

@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    event = Event.query.get_or_404(id)
    if event.creator_id != current_user.id:
        flash('You do not have permission to delete this event.')
        return redirect(url_for('events.index'))
    
    # Delete QR code file
    if event.qr_code_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], f'event_{id}.png'))
        except:
            pass
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!')
    return redirect(url_for('events.index'))

@bp.route('/<int:id>/qr')
@login_required
def qr_code(id):
    event = Event.query.get_or_404(id)
    if current_user.role == 'teacher' and event.creator_id != current_user.id:
        flash('You do not have permission to view this event.')
        return redirect(url_for('events.index'))
    
    # If QR code doesn't exist, generate it
    if not event.qr_code_path:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Create the URL for attendance marking
        attendance_url = f"{request.host_url}attendance/mark/{event.id}"
        
        qr.add_data(attendance_url)
        qr.make(fit=True)
        
        # Ensure the qrcodes directory exists
        qr_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
        os.makedirs(qr_dir, exist_ok=True)
        
        # Generate the QR code image
        qr_path = f'qrcodes/event_{event.id}.png'
        full_path = os.path.join(qr_dir, f'event_{event.id}.png')
        
        try:
            qr.make_image(fill_color="black", back_color="white").save(full_path)
            event.qr_code_path = qr_path
            db.session.commit()
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            flash('Error generating QR code. Please try again.')
            return redirect(url_for('events.view', id=event.id))
    
    # Serve the QR code image
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER']),
        f'event_{event.id}.png'
    )
