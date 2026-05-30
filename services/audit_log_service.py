import json
from typing import Any, Optional

from db.models.admin_audit_log import AdminAuditLog
from sqlalchemy.orm import Session


def log_admin_action(
    db: Session,
    *,
    admin_user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[Any] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> AdminAuditLog:
    payload = AdminAuditLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        method=method,
        path=path,
        details=json.dumps(details) if details is not None else None,
    )
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload
