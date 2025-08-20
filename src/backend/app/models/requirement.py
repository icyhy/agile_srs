from .. import db
from datetime import datetime


class Requirement(db.Model):
    __tablename__ = 'requirements'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='draft')  # draft, in_progress, completed
    
    # 关系
    user_requirements = db.relationship('UserRequirement', backref='requirement', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creator_id': self.creator_id,
            'creator_name': self.creator.username if self.creator else 'Unknown',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status
        }


class UserRequirement(db.Model):
    __tablename__ = 'user_requirements'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='member')  # owner, member


class RequirementContent(db.Model):
    __tablename__ = 'requirement_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'), nullable=False)
    content_type = db.Column(db.String(50))  # text, image, audio
    content_text = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'content_type': self.content_type,
            'content_text': self.content_text,
            'file_path': self.file_path,
            'submitted_by': self.submitted_by,
            'submitted_at': self.submitted_at.isoformat()
        }