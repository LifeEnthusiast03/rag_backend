from fastapi import APIRouter,Depends,HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from db.config import init_db
from utils.hash import hash_password,verify_password
from models.pymodel import create_user_request,create_user_response,login_user_request,login_user_response,token_payload
from utils.jwt import generate_token
from db.data_models import Users
router = APIRouter()

@router.post("/signup")
def signupuser(userdata: create_user_request, db: Annotated[Session, Depends(init_db)]):
    try:
        # Check if user already exists
        existing_user = db.query(Users).filter(Users.email == userdata.email).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = hash_password(userdata.password)
        
        # Create new user with hashed password
        new_user = Users(
            user_name=userdata.user_name,
            email=userdata.email,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create response with user data
        created_user = create_user_response(
            user_id=new_user.user_id,
            user_name=new_user.user_name,
            email=new_user.email
        )
        
        return {
            "User": created_user,
            "Successful": True,
            "message": "User created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"user creation failed, error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/login")
def loginuser(userdata: login_user_request, db: Annotated[Session, Depends(init_db)]):
    try:
        # Check if user exists
        exist_user = db.query(Users).filter(Users.email == userdata.email).first()
        if not exist_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Verify password
        password_same = verify_password(userdata.password, exist_user.password)
        if not password_same:
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
            )
        
        # Generate token
        payload = token_payload(userid=exist_user.user_id)
        usertoken = generate_token(payload)
        if not usertoken:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate authentication token"
            )
        
        # Create response with user data and token
        logged_user = login_user_response(
            user_id=exist_user.user_id,
            user_name=exist_user.user_name,
            email=exist_user.email,
            token=usertoken
        )
        
        return {
            "User": logged_user,
            "Successful": True,
            "message": "User logged in successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"failed to login: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )