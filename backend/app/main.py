from fastapi import FastAPI,Depends,HTTPException,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy import select,desc
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .database import Base,engine,get_db
from .models import User,Room,RoomMember,Message,Presence
from .auth import hash_password,verify_password,access_token,refresh_token,current_user
from jose import jwt,JWTError
from datetime import datetime,timezone
from uuid import UUID
app=FastAPI(title='Airnet API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class Register(BaseModel): username:str=Field(min_length=3,max_length=50); email:EmailStr; password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr; password:str
class RoomIn(BaseModel): name:str=Field(min_length=1,max_length=100); is_private:bool=False
class TokenIn(BaseModel): refresh_token:str
connections:dict[str,set[WebSocket]]={}
@app.on_event('startup')
async def startup():
 async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
@app.get('/health')
async def health(): return {'status':'ok','service':'airnet'}
@app.post('/auth/register')
async def register(x:Register,db:AsyncSession=Depends(get_db)):
 if (await db.execute(select(User).where((User.email==x.email)|(User.username==x.username)))).scalar_one_or_none(): raise HTTPException(409,'Email or username already exists')
 u=User(username=x.username,email=x.email,password_hash=hash_password(x.password)); db.add(u); await db.commit(); await db.refresh(u); return {'access_token':access_token(u.id),'refresh_token':refresh_token(u.id),'token_type':'bearer','user':{'id':str(u.id),'username':u.username,'email':u.email}}
@app.post('/auth/login')
async def login(x:Login,db:AsyncSession=Depends(get_db)):
 u=(await db.execute(select(User).where(User.email==x.email))).scalar_one_or_none()
 if not u or not verify_password(x.password,u.password_hash): raise HTTPException(401,'Invalid credentials')
 return {'access_token':access_token(u.id),'refresh_token':refresh_token(u.id),'token_type':'bearer'}
@app.post('/auth/refresh')
async def refresh(x:TokenIn,db:AsyncSession=Depends(get_db)):
 try: p=jwt.decode(x.refresh_token,settings.jwt_secret,algorithms=[settings.jwt_algorithm]); u=await db.get(User,p.get('sub'))
 except JWTError: u=None
 if not u: raise HTTPException(401,'Invalid refresh token')
 return {'access_token':access_token(u.id),'refresh_token':refresh_token(u.id),'token_type':'bearer'}
@app.get('/users/me')
async def me(u:User=Depends(current_user)): return {'id':str(u.id),'username':u.username,'email':u.email,'avatar_url':u.avatar_url}
@app.get('/rooms')
async def rooms(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
 rows=(await db.execute(select(Room).join(RoomMember,Room.id==RoomMember.room_id).where(RoomMember.user_id==u.id))).scalars().all(); return [{'id':str(r.id),'name':r.name,'is_private':r.is_private} for r in rows]
@app.post('/rooms')
async def create_room(x:RoomIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
 r=Room(name=x.name,is_private=x.is_private,created_by=u.id); db.add(r); await db.flush(); db.add(RoomMember(room_id=r.id,user_id=u.id,role='admin')); await db.commit(); return {'id':str(r.id),'name':r.name,'is_private':r.is_private}
@app.post('/rooms/{rid}/join')
async def join(rid:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
 if not await db.get(Room,rid): raise HTTPException(404,'Room not found')
 if await db.get(RoomMember,(rid,u.id)): return {'joined':True}
 db.add(RoomMember(room_id=rid,user_id=u.id)); await db.commit(); return {'joined':True}
@app.delete('/rooms/{rid}/leave')
async def leave(rid:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
 m=await db.get(RoomMember,(rid,u.id));
 if m: await db.delete(m); await db.commit()
 return {'left':True}
@app.get('/rooms/{rid}/messages')
async def messages(rid:UUID,limit:int=50,before:datetime|None=None,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
 if not await db.get(RoomMember,(rid,u.id)): raise HTTPException(403,'Join the room first')
 q=select(Message,User.username).join(User,User.id==Message.user_id).where(Message.room_id==rid).order_by(desc(Message.created_at)).limit(min(limit,100))
 if before: q=q.where(Message.created_at<before)
 rows=(await db.execute(q)).all(); return [{'id':str(m.id),'content':m.content,'username':name,'user_id':str(m.user_id),'created_at':m.created_at.isoformat()} for m,name in reversed(rows)]
async def ws_auth(ws):
 t=ws.query_params.get('token')
 if not t: await ws.close(code=1008); return None
 try: return jwt.decode(t,settings.jwt_secret,algorithms=[settings.jwt_algorithm]).get('sub')
 except JWTError: await ws.close(code=1008); return None
@app.websocket('/ws/rooms/{rid}')
async def room_ws(ws:WebSocket,rid:UUID):
 uid=await ws_auth(ws)
 if not uid:return
 await ws.accept(); key=str(rid); connections.setdefault(key,set()).add(ws)
 try:
  while True:
   data=await ws.receive_json(); typ=data.get('type','chat_message')
   if typ=='chat_message' and data.get('content','').strip():
    async for db in get_db():
     if not await db.get(RoomMember,(rid,uid)): await ws.send_json({'type':'error','payload':{'message':'Not a room member'}}); break
     m=Message(room_id=rid,user_id=uid,content=data['content'].strip()); db.add(m); await db.commit(); await db.refresh(m)
     event={'type':'chat_message','payload':{'id':str(m.id),'content':m.content},'sender_id':uid,'timestamp':m.created_at.isoformat()};
     for peer in list(connections[key]):
      try: await peer.send_json(event)
      except: connections[key].discard(peer)
   elif typ=='presence':
    event={'type':'presence','payload':data.get('payload',{}),'sender_id':uid,'timestamp':datetime.now(timezone.utc).isoformat()}
    for peer in list(connections[key]): await peer.send_json(event)
 finally: connections[key].discard(ws)
@app.websocket('/ws/signal/{rid}')
async def signal_ws(ws:WebSocket,rid:UUID):
 uid=await ws_auth(ws)
 if not uid:return
 await ws.accept(); key='signal:'+str(rid); connections.setdefault(key,set()).add(ws)
 try:
  while True:
   data=await ws.receive_json(); data['sender_id']=uid
   for peer in list(connections[key]):
    if peer is not ws:
     try: await peer.send_json(data)
     except: connections[key].discard(peer)
 except WebSocketDisconnect: pass
 finally: connections[key].discard(ws)
