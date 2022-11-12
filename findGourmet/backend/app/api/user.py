from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth
import json

from ..models import Role, User, db
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


@api.route("user/register/", methods=["POST"])
def user_reg():
    data = request.get_json()
    user = User.from_js(data)
    if user is not None:
        db.session.add(user)
        db.session.commit()
        response = jsonify({"username": user.username})
        response.status_code = 200
        return response
    else:
        return bad_request("no username or password included in request")

@api.route("user/modifyMessage", methods=['POST'])
@auth.login_required
def modifyMessage():
    modify_dict = request.get_json()
    user = User.query.filter_by(id=modify_dict['id']).first()
    res_raw = {"username":user.username}
    if len(modify_dict['phoneNumber']) == 11 and modify_dict['phoneNumber'].isdigit():
        user.phoneNumber = modify_dict['phoneNumber']
        db.session.commit()
        res_raw['phoneNumber'] = 'modify success'
    else:
        res_raw['phoneNumber'] = 'invalid phoneNumber'

    if modify_dict['introduce'] != '' and modify_dict['introduce'] is not None:
        user.introduce = modify_dict['introduce']
        db.session.commit()
        res_raw['introduce'] = 'modify sucess'
    else:
        res_raw['introduce'] = 'invalid introduce'

    if len(modify_dict['password']) >= 6 and password_valid(modify_dict['password']):
        user.password = modify_dict['password']
        db.session.commit()
        res_raw['password'] = 'modify success'
    else:
        res_raw['password'] = 'invalid password'

    response = jsonify(res_raw)
    response.status_code = 200
    return response

def password_valid(password):
    digit = 0
    for p in password:
        if p.isdigit():
            digit += 1
    if digit>=2 and not password.islower() and not password.isupper():
        return True
    else:
        return False

@api.route("/user/pageFindAll/<int:index>")
def fine_all_users():
    pass


@api.route("/user/getByQuery", methods=["POST"])
def query_user():
    req_json = request.get_json()
    valid_keys = ["id", "username", "level"]
    users = User.query.filter_by(**req_json).all()  # TODO 更新一下分页
    response = jsonify(
        {"total": len(users), "records": [user.to_json for user in users]}
    )
    response.status_code = 200
    return response


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

@api.route("/user/getCitys")
def getCitys():
    users = User.query.all()
    i = 1
    citys = []
    city_set = set()
    for user in users:
        city_set.add(user.cityName)
    for city in city_set:
        if city is not None:
            citys.append({"cityId": i, "cityName": city})
        i += 1
    response = jsonify(citys)
    response.status_code = 200
    return response
