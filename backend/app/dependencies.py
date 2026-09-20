from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import UserAccount, RoleEnum, UserStatusEnum
from backend.app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserAccount:
    """Validate JWT token and return active current user account."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("user_id")
    if not user_id:
        raise credentials_exception

    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise credentials_exception

    if user.status != UserStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or locked"
        )

    return user


def require_roles(allowed_roles: List[RoleEnum]) -> Callable:
    """Dependency factory to enforce role-based access control."""
    def role_checker(current_user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{current_user.role.value}' does not have permission"
            )
        return current_user

    return role_checker
