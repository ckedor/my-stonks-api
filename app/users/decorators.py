from fastapi import Depends

from app.users.views import current_active_user, current_superuser


def authenticated():
    return Depends(current_active_user)


def admin_required():
    return Depends(current_superuser)
