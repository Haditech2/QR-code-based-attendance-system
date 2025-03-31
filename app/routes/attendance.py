from datetime import datetime, timedelta
import pytz
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
    local_tz = pytz.timezone('Africa/Lagos')
    current_time = datetime.now(local_tz)
    
    # Debugging logs
    print(f"Current Time (Local): {current_time}")
    print(f"Event Start Time: {event.start_time}")
    print(f"Event End Time: {event.end_time}")
    
    # Check if event is active
    if current_time < event.start_time:
        print(f"Event not started: Current time {current_time} is before start time {event.start_time}")
        flash('This event has not started yet.')
        return redirect(url_for('events.view', id=event_id))
    
    if current_time > event.end_time:
        print(f"Event ended: Current time {current_time} is after end time {event.end_time}")
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
    late_threshold = event.start_time + timedelta(minutes=15)
    status = 'late' if current_time > late_threshold else 'present'
    
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
