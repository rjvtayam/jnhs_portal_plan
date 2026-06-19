from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user, require_role
from app.routes.notifications import create_notification
from app.routes.activity import log_activity

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin", "registrar")),
):
    if current_user.role == "super_admin" and user.role not in ("admin", "principal", "registrar"):
        raise HTTPException(status_code=403, detail="Super Admin can only create admin, principal, and registrar accounts")

    if current_user.role == "admin" and user.role != "teacher":
        raise HTTPException(status_code=403, detail="Admin can only create teacher accounts")

    if current_user.role == "registrar" and user.role not in ("student", "parent"):
        raise HTTPException(status_code=403, detail="Registrar can only create student and parent accounts")

    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        username=user.username,
        password_hash=hash_password(user.password),
        role=user.role,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Notify the new user
    create_notification(
        db=db,
        user_id=new_user.id,
        title="Account Created",
        message=f"Your {user.role} account has been created. Username: {user.username}",
        notif_type="account",
        link="/login.html",
    )

    # Log activity
    log_activity(
        db=db, user_id=current_user.id, username=current_user.username, user_role=current_user.role,
        action="register", category="account",
        description=f"Created {user.role} account: {user.username}",
        target_type="user", target_id=new_user.id,
        ip_address=request.client.host if request.client else None,
    )

    return new_user


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="login", category="auth",
        description=f"{user.username} logged in as {user.role}",
        ip_address=request.client.host if request.client else None,
    )

    return Token(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
