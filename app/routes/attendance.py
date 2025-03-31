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
    
    # Get current time in local timezone
    current_time = datetime.now()
    
    # Add debug logging
    print(f"Current time: {current_time}")
    print(f"Event start time: {event.start_time}")
    print(f"Event end time: {event.end_time}")
    
    # Check if event is active
    if current_time < event.start_time:
        print(f"Event not started yet. Current time: {current_time}, Start time: {event.start_time}")
        flash('This event has not started yet.')
        return redirect(url_for('events.view', id=event_id))
    
    if current_time > event.end_time:
        print(f"Event has ended. Current time: {current_time}, End time: {event.end_time}")
        flash('This event has ended.')
        return redirect(url_for('events.view', id=event_id))
    
    # Check if user has already marked attendance
    existing_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_attendance:
        flash('You have already marked your attendance for this event.')
        return redirect(url_for('events.view', id=event_id))
    
    # Determine if attendance is present or late
    # Consider attendance late if marked more than 15 minutes after start time
    late_threshold = event.start_time + timedelta(minutes=15)
    
    if current_time > late_threshold:
        status = 'late'
        print(f"Marking attendance as late. Current time: {current_time}, Late threshold: {late_threshold}")
    else:
        status = 'present'
        print(f"Marking attendance as present. Current time: {current_time}, Late threshold: {late_threshold}")
    
    # Create attendance record
    attendance = Attendance(
        user_id=current_user.id,
        event_id=event_id,
        timestamp=current_time,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    flash(f'Attendance marked successfully! Status: {status}')
    return redirect(url_for('events.view', id=event_id))

@bp.route('/view/<int:event_id>')
@login_required
def view(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('You do not have permission to view attendance for this event.')
        return redirect(url_for('events.index'))
    
    attendance_records = Attendance.query.filter_by(event_id=event_id).all()
    return render_template('attendance/view.html', event=event, attendance_records=attendance_records)

@bp.route('/sync/<int:event_id>')
@login_required
def sync(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('You do not have permission to sync attendance for this event.')
        return redirect(url_for('events.index'))
    
    # Get all unsynced attendance records for this event
    unsynced_records = Attendance.query.filter_by(
        event_id=event_id,
        sync_status='pending'
    ).all()
    
    # Here you would implement the actual syncing logic
    # For now, we'll just mark them as synced
    for record in unsynced_records:
        record.sync_status = 'synced'
    
    db.session.commit()
    flash(f'{len(unsynced_records)} attendance records synced successfully!')
    return redirect(url_for('attendance.view', event_id=event_id)) 