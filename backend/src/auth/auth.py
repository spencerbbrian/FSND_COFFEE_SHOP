import json, os
from dotenv import load_dotenv
from flask import request,abort,Flask
from functools import wraps
from jose import jwt
from urllib.request import urlopen

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = os.getenv("ALGORITHMS")
API_AUDIENCE = os.getenv("API_AUDIENCE")
token = os.getenv("token")
## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)
    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')
    if len(header_parts) != 2:
        abort(401)
    elif header_parts[0].lower() != 'bearer':
        abort(401)

    return header_parts[1]


def check_permissions(permission,payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code':'invalid_claims',
            'description':'Permission not included in JWT.'
        },400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code':'unauthorized',
            'description':'Permission not found.'
        },403)
    return True

def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # GET HEADER DATA
    unverified_header = jwt.get_unverified_header(token)
    
    # KEY CHOICE
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # VERIFICATION
    if rsa_key:
        try:
            # VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            jwt = get_token_auth_header()
            try:
                payload = verify_decode_jwt(jwt)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

app = Flask(__name__)

@app.route('/coffee')
@requires_auth('get:drinks')
def images(jwt):
    print(jwt)
    return 'not implemented'