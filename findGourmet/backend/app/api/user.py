from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
import json

from ..models import Role, User, db, FindG, PleEat
from . import api
from .errors import bad_request, forbidden, unauthorized
import datetime

import random
from findGourmet import basedir
import os

auth = HTTPTokenAuth(scheme='Bearer')


@auth.error_handler
def auth_error(status):
    return "Access Denied", status

# @auth.verify_password
# def verify_password(username_or_token, password):
#     print("verifying ", username_or_token, password)
#     if username_or_token == "cheatToken":

#         g.current_user = User.query.filter_by(username="john").first()
#         g.token_used = False
#         return True
#     if username_or_token == "":
#         return False
#     if password == "":
#         g.current_user = User.verify_auth_token(username_or_token)
#         g.token_used = True
#         return g.current_user is not None
#     user = User.query.filter_by(username=username_or_token.lower()).first()
#     if not user:
#         return False
#     g.current_user = user
#     g.token_used = False
#     return user.verify_password(password)

@auth.verify_token
def verify_token(token):
    g.current_user = User.verify_auth_token(token)
    g.token_used = True
    return g.current_user is not None


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
    
    user_json = request.form
    print(user_json["password"])
    admin = Role.query.filter_by(id=1).first()
    admin = admin.users
    user = User.query.filter_by(username=user_json["username"].lower()).first()
    if (
        user is not None
        and user.verify_password(user_json["password"])
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
        if user in admin and user.verify_password(user_json["password"]):
            return bad_request(
                "You are an admin, please login via /api/user/adminLogin"
            )
        else:
            return bad_request("invalid username or password")


@api.route("user/adminLogin/", methods=["POST"])
def admin_user_login():
    user_json = request.form
    # print(user_json)
    admin = Role.query.filter_by(id=1).first()
    admin = admin.users

    user = User.query.filter_by(
        username=user_json["username"].lower(),
    ).first()
    if user is not None and user.verify_password(user_json["password"]):
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


@api.route("user/register", methods=["POST"])
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


@api.route("user/modifyMessage", methods=["POST"])
@auth.login_required
def modifyMessage():
    modify_dict = request.get_json()
    user = User.query.filter_by(id=modify_dict["id"]).first()
    res_raw = {"username": user.username}
    if len(modify_dict["phoneNumber"]) == 11 and modify_dict["phoneNumber"].isdigit():
        user.phoneNumber = modify_dict["phoneNumber"]
        db.session.commit()
        res_raw["phoneNumber"] = "modify success"
    else:
        res_raw["phoneNumber"] = "invalid phoneNumber"

    if modify_dict["introduce"] != "" and modify_dict["introduce"] is not None:
        user.introduce = modify_dict["introduce"]
        db.session.commit()
        res_raw["introduce"] = "modify sucess"
    else:
        res_raw["introduce"] = "invalid introduce"
    if "password" in modify_dict.keys():
        if len(modify_dict["password"]) >= 6 and password_valid(modify_dict["password"]):
            user.password = modify_dict["password"]
            db.session.commit()
            res_raw["password"] = "modify success"
        else:
            res_raw["password"] = "invalid password"

    response = jsonify(res_raw)
    response.status_code = 200
    return response


def password_valid(password):
    digit = 0
    for p in password:
        if p.isdigit():
            digit += 1
    if digit >= 2 and not password.islower() and not password.isupper():
        return True
    else:
        return False


@api.route("/user/pageFindAll/<int:index>/<int:rows>")
@auth.login_required
def fine_all_users(index, rows):

    if g.current_user.level != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    users = User.query.paginate(page=index, per_page=rows).items
    totals = User.query.count()
    # users=users.
    response = jsonify(
        {"total": totals, "records": [user.to_json for user in users]}
    )
    response.status_code = 200
    return response


@api.route("/user/getByQuery", methods=['POST'])
@auth.login_required
def query_user():
    if g.current_user.level != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    req_json = request.get_json()
    valid_keys = ["id", "username", "level"]
    # valid_keys = [valid_key for valid_key in valid_keys if valid_key in req_json.keys()]
    # valid_keys = [valid_key for valid_key in valid_keys if req_json[valid_key] != '']   # 过滤掉空的查询条件
    # filter_dict = {your_key: req_json[your_key] for your_key in valid_keys}
    for key in valid_keys:
        if key not in req_json.keys():
            req_json[key]=""
    print(req_json)
    # users = User.query.filter_by(**req_json).paginate()
    if req_json["id"] is not "":
        users=User.query.filter_by(id=req_json['id']).all()
        totals=len(users)
    else:
        users = (
        User.query.filter(User.username.like("%"+req_json["username"]+"%"),User.level.like("%"+req_json["level"]+"%"))
       
    )
        totals=users.count()
        users=users.paginate(page=req_json.get("page"), per_page=req_json.get("rows")).items
    # totals = User.query.filter_by(**filter_dict).count()
    # users=users.
    response = jsonify(
        {"total": totals, "records": [user.to_json for user in users]}
    )
    response.status_code = 200
    return response


# paginate usage
# # >>> User.query.paginate(page=1,per_page=2,error_out=False)
# # <flask_sqlalchemy.pagination.QueryPagination object at 0x1061fef10>
# # >>> User.query.paginate(page=1,per_page=2,error_out=False)
# # <flask_sqlalchemy.pagination.QueryPagination object at 0x1061999a0>
# # >>> User.query.paginate(page=1,per_page=2,error_out=False).page
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
