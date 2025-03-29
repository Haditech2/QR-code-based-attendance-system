from datetime import datetime
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
    
    # Check if event is active
    if current_time < event.start_time:
        flash('Event has not started yet.')
        return redirect(url_for('events.index'))
    if current_time > event.end_time:
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
    
    # Determine attendance status
    status = 'present'
    if current_time > event.start_time.replace(hour=event.start_time.hour + 1):
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
    if event.creator_id != current_user.id:
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