from typing import Any, Dict, Optional, Union,List
# from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_id(self, db: Session, *, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_all_user(self, db: Session)-> Optional[User]:
        return db.query(User.id, User.email).all()
    
    def get_all_user_except_provider_and_current_user(self, db: Session, current_user: User
        ) -> List[Optional[User]]:
        return (
            db.query(User)
            .filter(User.id != current_user.id)  # Exclude current user
            .filter(User.is_provider != True)  # Exclude users with is_provider set to True
            .all()
        )


    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        if obj_in.password:
            obj_in.password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            password=obj_in.password,
            name=obj_in.name,
            is_provider=obj_in.is_provider,
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
        # if not user.is_google_sso:
        #     if not verify_password(password, user.password):
        #         return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_provider(self, user: User) -> bool:
        return user.is_provider


user = CRUDUser(User)
