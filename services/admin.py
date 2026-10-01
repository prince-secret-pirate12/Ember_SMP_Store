from models import AdminAuditLog
from extensions import db

def audit(admin_id, action, target_type, target_id=None, details=None):
    db.session.add(AdminAuditLog(admin_id=admin_id, action=action, target_type=target_type, target_id=str(target_id) if target_id is not None else None, details=details)); db.session.commit()
