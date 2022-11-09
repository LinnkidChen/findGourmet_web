from flask import g, jsonify,request,g
from flask_httpauth import HTTPBasicAuth
from ..models import User,Role
from . import api
from .errors import unauthorized, forbidden,bad_request

auth=HTTPBasicAuth()

@auth.error_handler
def auth_error():
    return unauthorized('Invalid password or User not exist.')

@auth.verify_password
def verify_password(username_or_token, password):
    if username_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token,expiration=3600)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token.lower()).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)
        
        

    
@api.route('/tokens/', methods=['POST'])
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(), 'expiration': 3600})
    
@api.route('user/login/',methods=['POST'])
def user_login():
    user_json=request.get_json()
    # print(user_json)
    admin=Role.query.filter_by(id=1).first()
    admin=admin.users
    user=User.query.filter_by(username=user_json.get('username').lower()).first()
    if user is not None and user.verify_password(user_json.get('password')) and user not in admin:
        g.current_user=user
        response = jsonify({'token': g.current_user.generate_auth_token(), 'expiration': 3600})
        response.status_code = 200
        return response

    else:
        if user in admin and user.verify_password(user_json.get('password')):
            return bad_request("You are an admin, please login via /api/user/adminLogin")
        else:
            return bad_request("invalid username or password")


@api.route('user/adminLogin/',methods=['POST'])
def admin_user_login():
    user_json=request.get_json()
    # print(user_json)
    admin=Role.query.filter_by(id=1).first()
    admin=admin.users
    
    user=User.query.filter_by(username=user_json.get('username').lower(),).first()
    if user is not None and user.verify_password(user_json.get('password')) :
        if user in admin:
            g.current_user=user
            response = jsonify({'token': g.current_user.generate_auth_token(), 'expiration': 3600})
            response.status_code = 200
            return response
        else :
            return bad_request("you're not an admin, please login via /api/user/login")
            

    else:
        return bad_request("invalid username or password")
        
 
    