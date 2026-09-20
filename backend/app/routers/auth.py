from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import UserAccount, UserStatusEnum
from backend.app.schemas import LoginRequest, Token, UserAccountOut
from backend.app.utils.security import verify_password, create_access_token
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="User Login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with username/email and password."""
    user = db.query(UserAccount).filter(
        (UserAccount.username == request.username) | (UserAccount.email == request.username)
    ).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )

    if user.status != UserStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status is '{user.status.value}'. Please contact system admin."
        )

    access_token = create_access_token(
        data={"user_id": user.user_id, "username": user.username, "role": user.role.value}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        role=user.role
    )


@router.get("/me", response_model=UserAccountOut, summary="Get Current User Profile")
def get_me(current_user: UserAccount = Depends(get_current_user)):
    """Return currently authenticated user details."""
    return current_user
