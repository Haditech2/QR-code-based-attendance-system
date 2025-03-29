from datetime import datetime
from app import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')  # 'present', 'late', 'absent'
    sync_status = db.Column(db.String(20), default='synced')  # 'synced', 'pending', 'failed'

    def __repr__(self):
        return f'<Attendance {self.user_id} - {self.event_id}>' 