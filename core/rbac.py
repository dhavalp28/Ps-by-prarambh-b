from typing import Iterable

ROLE_ADMIN = "admin"
ROLE_USER = "user"
ROLE_VENDOR = "vendor"


def has_role(user, roles: Iterable[str]) -> bool:
    user_role = (getattr(user, "role", None) or ROLE_USER).lower()
    return user_role in {role.lower() for role in roles}
