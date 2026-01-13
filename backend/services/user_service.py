"""用户服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import UserModel
from schemas.user import UserCreate, UserUpdate

# 密码加密上下文
# 说明：
# - 原本使用的是 bcrypt，但在当前运行环境中会触发
#   AttributeError: module 'bcrypt' has no attribute '__about__'
#   以及 72 字节限制等问题
# - 这里改用 pbkdf2_sha256（纯 Python 实现，更稳定，不依赖系统 bcrypt 模块）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    """根据ID获取用户"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """根据用户名获取用户"""
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """根据邮箱获取用户"""
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """获取用户列表"""
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> UserModel:
    """创建用户"""
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
    """更新用户"""
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 如果更新密码，需要加密
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """验证用户"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
