from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os


# Initializations
live = os.environ.get('LIVE') or False
app = FastAPI(docs_url=None, redoc_url=None) if live else FastAPI()

# Middleware
origins = [
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*']
)