from fastapi import FastAPI
from auth.router import  router as auth
from articles.router import router as articles
import logging
logging.getLogger('passlib').setLevel(logging.ERROR)




app = FastAPI(
    title="Orher Code API"
)

app.include_router(auth)
app.include_router(articles)

