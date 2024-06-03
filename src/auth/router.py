from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from articles.pydantic_models import Token, TokenData
from auth.auth import authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: TokenData):
    user_in_db = await authenticate_user(form_data.username, form_data.password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}