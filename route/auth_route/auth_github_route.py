from fastapi import APIRouter, HTTPException,Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Annotated
from db.config import init_db
from db.data_models import Users
from utils.jwt import generate_token
from models.pymodel import token_payload
import httpx
import os 

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/github/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter()

@router.get("/githublogin")
def githublogin():
    """
    Initiates GitHub OAuth login flow.
    
    Note: This endpoint redirects to GitHub and cannot be tested from Swagger UI.
    Test directly in browser: http://localhost:8000/githublogin
    """
    if not CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth CLIENT_ID not configured"
        )
    
    # GitHub OAuth authorization URL with required parameters
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
    )
    
    return RedirectResponse(github_auth_url, status_code=302)

@router.get("/github/callback")
async def github_callback(code: str,db: Annotated[Session, Depends(init_db)]):
    """
    GitHub OAuth callback endpoint.
    Receives the authorization code and exchanges it for an access token.
    """
    try:
        # Parameters for token exchange
        params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code
        }
        headers = {
            'Accept': 'application/json'
        }
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://github.com/login/oauth/access_token",
                params=params,
                headers=headers
            )
        
        # Check if request was successful
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get access token from GitHub"
            )
        
        data = response.json()
        
        # Check if there's an error in the response
        if 'error' in data:
            raise HTTPException(
                status_code=400,
                detail=f"GitHub OAuth error: {data.get('error_description', data['error'])}"
            )
        
        # Check if access_token exists
        if 'access_token' not in data:
            raise HTTPException(
                status_code=400,
                detail="No access token received from GitHub"
            )
        
        access_token = data['access_token']
        
        # Fetch user data from GitHub API
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                url="https://api.github.com/user",
                headers={'Authorization': f'Bearer {access_token}'}
            )
        
        # Check if user request was successful
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code,
                detail="Failed to fetch user data from GitHub"
            )
        
        userdata = user_response.json()
        username=userdata["login"]
        
        # Get email - fetch from /user/emails if not public
        useremail = userdata.get("email")
        if not useremail:
            async with httpx.AsyncClient() as client:
                email_response = await client.get(
                    url="https://api.github.com/user/emails",
                    headers={'Authorization': f'Bearer {access_token}'}
                )
            
            if email_response.status_code == 200:
                emails = email_response.json()
                # Get primary email or first verified email
                primary_email = next((e['email'] for e in emails if e.get('primary') and e.get('verified')), None)
                if not primary_email:
                    primary_email = next((e['email'] for e in emails if e.get('verified')), None)
                useremail = primary_email
        
        if not useremail:
            raise HTTPException(
                status_code=400,
                detail="Unable to retrieve email from GitHub account"
            )
        
        existing_user = db.query(Users).filter(Users.email == useremail).first()
        if existing_user:
            # Generate JWT token for existing user
            token_data = token_payload(userid=existing_user.user_id)
            jwt_token = generate_token(token_data)
            
            if not jwt_token:
                raise HTTPException(status_code=500, detail="Failed to generate token")
            
            # Redirect to frontend with token and user data
            return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/github/callback?token={jwt_token}&user_id={existing_user.user_id}&user_name={existing_user.user_name}&email={existing_user.email}",
                status_code=302
            )
        
        # Create new user
        newuser = Users(
            user_name=username,
            email=useremail,
        )
        db.add(newuser)
        db.commit()
        db.refresh(newuser)
        
        # Generate JWT token for new user
        token_data = token_payload(userid=newuser.user_id)
        jwt_token = generate_token(token_data)
        
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to generate token")
        
        # Redirect to frontend with token and user data
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/github/callback?token={jwt_token}&user_id={newuser.user_id}&user_name={newuser.user_name}&email={newuser.email}",
            status_code=302
        )
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with GitHub: {str(e)}"
        )
    except Exception as e:
        print(f"Error in GitHub callback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )