from .. import db
from datetime import datetime


class RequirementDocument(db.Model):
    __tablename__ = 'requirement_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_path = db.Column(db.String(255))
    
    # 确保每个需求的版本唯一
    __table_args__ = (
        db.UniqueConstraint('requirement_id', 'version'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'version': self.version,
            'content': self.content,
            'generated_at': self.generated_at.isoformat(),
            'pdf_path': self.pdf_path
        }