import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class User(Base):
    __tablename__='users'; id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); username:Mapped[str]=mapped_column(String(50),unique=True,index=True); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash:Mapped[str]=mapped_column(Text); avatar_url:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Room(Base):
    __tablename__='rooms'; id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); name:Mapped[str]=mapped_column(String(100)); is_private:Mapped[bool]=mapped_column(Boolean,default=False); created_by:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id')); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class RoomMember(Base):
    __tablename__='room_members'; room_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('rooms.id',ondelete='CASCADE'),primary_key=True); user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),primary_key=True); role:Mapped[str]=mapped_column(String(20),default='member'); joined_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Message(Base):
    __tablename__='messages'; id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); room_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('rooms.id',ondelete='CASCADE'),index=True); user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE')); content:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Presence(Base):
    __tablename__='presence'; user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),primary_key=True); room_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('rooms.id',ondelete='CASCADE'),primary_key=True); status:Mapped[str]=mapped_column(String(20),default='online'); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
