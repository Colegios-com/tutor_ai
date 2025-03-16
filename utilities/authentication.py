# Async
from fastapi import HTTPException

# Standard
import jwt
import os


def sign(phone_number):
    jwt_key = os.environ.get('JWT_KEY')

    if not jwt_key:
        raise HTTPException(status_code=401, detail='JWT key is missing.')

    try:
        web_token = jwt.encode({'phone_number': phone_number}, jwt_key, algorithm='HS256')
        return web_token
    except jwt.InvalidKeyError:
        raise HTTPException(status_code=401, detail='Invalid key.')
    except jwt.InvalidAlgorithmError:
        raise HTTPException(status_code=401, detail='Invalid algorithm.')
    except Exception:
        raise HTTPException(status_code=401, detail='Token creation failed.')


def verify(authorization_token):
    jwt_key = os.environ.get('JWT_KEY')

    if not jwt_key:
        raise HTTPException(status_code=401, detail='JWT key is missing.')
        
    try:
        user = jwt.decode(authorization_token, jwt_key, algorithms=["HS256"])
        return user['phone_number']
    except jwt.InvalidKeyError:
        raise HTTPException(status_code=401, detail='Invalid key.')
    except jwt.InvalidAlgorithmError:
        raise HTTPException(status_code=401, detail='Invalid algorithm.')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired.')
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail='Invalid token.')
    except Exception:
        raise HTTPException(status_code=401, detail='Token verification failed.')