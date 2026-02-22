from fastapi import APIRouter, HTTPException,Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Annotated
from db.config import init_db
import httpx
import os 

CLIENT_ID = "Ov23liE9lY7D7lywrXcI"
CLIENT_SECRET = "42de518cd9138a02cd2fc415465f67b00bc4862f"
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/github/callback")

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
        print(f"GitHub user data: {userdata}")
        print(f"GitHub OAuth access token: {access_token}")
        
        return {
            "access_token": access_token,
            "user": userdata
        }
        
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