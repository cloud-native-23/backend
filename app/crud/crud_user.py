from typing import Any, Dict, Optional, Union
# from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_user_uuid(self, db: Session, *, user_uuid: int) -> Optional[User]:
        return db.query(User).filter(User.user_uuid == user_uuid).first()

    def get_by_uuid(self, db: Session, *, uuid: int) -> Optional[User]:
        return db.query(User).filter(User.user_uuid == uuid).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        if obj_in.password:
            obj_in.password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            password=obj_in.password,
            name=obj_in.name,
            image=obj_in.image,
            is_provider=obj_in.is_provider,
            is_google_sso=obj_in.is_google_sso,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.is_google_sso:
            if not verify_password(password, user.password):
                return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_provider(self, user: User) -> bool:
        return user.is_provider


user = CRUDUser(User)
