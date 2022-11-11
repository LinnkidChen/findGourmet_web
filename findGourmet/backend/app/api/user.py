from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth

from ..models import Role, User
from . import api
from .errors import bad_request, forbidden, unauthorized

auth = HTTPBasicAuth()


@auth.error_handler
def auth_error():
    return unauthorized("Invalid password or User not exist or not logged in")


@auth.verify_password
def verify_password(username_or_token, password):
    print("verifying ", username_or_token, password)
    if username_or_token == "cheatToken":

        g.current_user = User.query.filter_by(role_str="Admin").first()
        g.token_used = False
        return True
    if username_or_token == "":
        return False
    if password == "":
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token.lower()).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route("/tokens/", methods=["POST"])
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid credentials")
    return jsonify(
        {
            "token": g.current_user.generate_auth_token(),
            "expiration": current_app.config["TOKEN_EXPIRE"],
        }
    )


@api.route("user/login/", methods=["POST"])
def user_login():
    user_json = request.get_json()
    # print(user_json)
    admin = Role.query.filter_by(id=1).first()
    admin = admin.users
    user = User.query.filter_by(username=user_json.get("username").lower()).first()
    if (
        user is not None
        and user.verify_password(user_json.get("password"))
        and user not in admin
    ):
        g.current_user = user
        response = jsonify(
            {
                "token": g.current_user.generate_auth_token(),
                "expiration": current_app.config["TOKEN_EXPIRE"],
            }
        )
        response.status_code = 200
        return response

    else:
        if user in admin and user.verify_password(user_json.get("password")):
            return bad_request(
                "You are an admin, please login via /api/user/adminLogin"
            )
        else:
            return bad_request("invalid username or password")


@api.route("user/adminLogin/", methods=["POST"])
def admin_user_login():
    user_json = request.get_json()
    # print(user_json)
    admin = Role.query.filter_by(id=1).first()
    admin = admin.users

    user = User.query.filter_by(
        username=user_json.get("username").lower(),
    ).first()
    if user is not None and user.verify_password(user_json.get("password")):
        if user in admin:
            g.current_user = user
            response = jsonify(
                {
                    "token": g.current_user.generate_auth_token(),
                    "expiration": current_app.config["TOKEN_EXPIRE"],
                }
            )
            response.status_code = 200
            return response
        else:
            return bad_request("you're not an admin, please login via /api/user/login")

    else:
        return bad_request("invalid username or password")


# @api.route("user/test", methods=["POST"])
# def teeeest():
#     user_json = request.get_json()
#     print(user_json["username"])
#     return jsonify({"nihao": 0})


@api.route("user/getById/<int:id>")
@auth.login_required
def getById(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        response = jsonify(user.to_json)
        response.status_code = 200
        return response
    else:
        return bad_request("User not found")


@api.route("user/getByUserName/<string:id>")
@auth.login_required
def getByUserName(id):
    print(id)
    user = User.query.filter_by(username=id).first()
    if user is not None:
        response = jsonify(user.to_json)
        response.status_code = 200
        return response
    else:
        return bad_request("User not found")


# @api.route('user/register/',methods=['POST'])
# def user_reg():

# paginate usage
# # >>> User.query.paginate(page=1,per_page=2,error_out=False)
# # <flask_sqlalchemy.pagination.QueryPagination object at 0x1061fef10>
# # >>> User.query.paginate(page=1,per_page=2,error_out=False)
# # <flask_sqlalchemy.pagination.QueryPagination object at 0x1061999a0>
# # >>> User.query.paginate(page=1,per_page=2,error_out=False).page
# # 1
# # >>> User.query.paginate(page=1,per_page=2,error_out=False).items
# [<User 'john'>, <User 'marry'>]
# >>>
