from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from passlib.context import CryptContext
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .config import settings
from .database import get_db
from .models import User
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); oauth=OAuth2PasswordBearer(tokenUrl='/auth/login')
def hash_password(p): return pwd.hash(p)
def verify_password(p,h): return pwd.verify(p,h)
def token(sub,days=0,minutes=0): return jwt.encode({'sub':sub,'exp':datetime.now(timezone.utc)+timedelta(days=days,minutes=minutes)},settings.jwt_secret,algorithm=settings.jwt_algorithm)
def access_token(uid): return token(str(uid),minutes=settings.access_token_expire_minutes)
def refresh_token(uid): return token(str(uid),days=settings.refresh_token_expire_days)
async def current_user(t:str=Depends(oauth),db:AsyncSession=Depends(get_db)):
    try: uid=jwt.decode(t,settings.jwt_secret,algorithms=[settings.jwt_algorithm]).get('sub')
    except JWTError: raise HTTPException(status_code=401,detail='Invalid or expired token')
    u=await db.get(User,uid)
    if not u: raise HTTPException(status_code=401,detail='User not found')
    return u
