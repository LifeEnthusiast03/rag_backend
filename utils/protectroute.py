from fastapi import Header,HTTPException,status,Depends
from sqlalchemy.orm import Session
from typing import Annotated,Union
from db.config import init_db
from .jwt import verify_token
from models.pymodel import token_payload,userdataforapi
from db.data_models import Users
async def get_current_user(
        db:Annotated[Session,Depends(init_db)],
        authorization:Annotated[Union[str,None],Header(...)]):
    try:
        auth_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Authentication Credentials"
        )
        if not authorization:
            raise auth_exception
        if not authorization.startswith("Bearer "):
            raise auth_exception
        usertoken = authorization[len("Bearer "):]
        data:token_payload = verify_token(token=usertoken)
        if not data:
            raise Exception("Token verification failed")
        user = db.query(Users).filter(Users.user_id==data.userid).first()
        userData = userdataforapi(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email
        )
        print("get user data succesfully")
        return userData
    except HTTPException as e:
        raise
    except Exception as e:
        print(f"failed to verify token,{e}");
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )