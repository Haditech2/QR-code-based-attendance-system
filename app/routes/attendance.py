from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.event import Event
from app.models.attendance import Attendance
from app import db

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@bp.route('/mark/<int:event_id>')
@login_required
def mark(event_id):
    event = Event.query.get_or_404(event_id)
    current_time = datetime.utcnow()
    
    # Convert event times to UTC for comparison
    event_start_utc = event.start_time.replace(tzinfo=None)
    event_end_utc = event.end_time.replace(tzinfo=None)
    
    # Check if event is active
    if current_time < event_start_utc:
        flash('Event has not started yet.')
        return redirect(url_for('events.index'))
    if current_time > event_end_utc:
        flash('Event has ended.')
        return redirect(url_for('events.index'))
    
    # Check if already marked attendance
    existing_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_attendance:
        flash('You have already marked your attendance for this event.')
        return redirect(url_for('events.index'))
    
    # Determine attendance status (late if more than 15 minutes after start)
    status = 'present'
    late_threshold = event_start_utc + timedelta(minutes=15)
    if current_time > late_threshold:
        status = 'late'
    
    attendance = Attendance(
        user_id=current_user.id,
        event_id=event_id,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    flash('Attendance marked successfully!')
    return redirect(url_for('events.index'))

@bp.route('/view/<int:event_id>')
@login_required
def view(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.role != 'teacher' or event.creator_id != current_user.id:
        flash('You do not have permission to view attendance for this event.')
        return redirect(url_for('events.index'))
    
    attendances = Attendance.query.filter_by(event_id=event_id).all()
    return render_template('attendance/view.html', event=event, attendances=attendances)

@bp.route('/sync')
@login_required
def sync():
    # This endpoint would handle syncing attendance records with a remote server
    # For now, we'll just mark all pending records as synced
    pending_records = Attendance.query.filter_by(
        user_id=current_user.id,
        sync_status='pending'
    ).all()
    
    for record in pending_records:
        record.sync_status = 'synced'
    
    db.session.commit()
    return jsonify({'message': 'Attendance records synced successfully'}) 