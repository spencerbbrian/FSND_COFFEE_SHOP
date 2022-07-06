import json, os
from dotenv import load_dotenv
from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = os.getenv("ALGORITHMS")
API_AUDIENCE = os.getenv("API_AUDIENCE")

token = ""

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


def check_permissions(permission, payload):
    if 'permission' not in payload:
        raise AuthError({
            'code':'invalid_claims',
            'description':'Permission not included in JWT.'
        },400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code':'unauthorized',
            'description':'Permission not found.'
        },403)

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    raise Exception('Not Implemented')

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator