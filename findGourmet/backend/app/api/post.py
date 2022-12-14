from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth
import json

from ..models import Role, User, db, FindG, PleEat, Success, FeeSummary
from . import api
from .errors import bad_request, forbidden, unauthorized
import datetime
from werkzeug.utils import secure_filename
import random
from findGourmet import basedir
import base64
import hashlib
import os
from .user import auth
commentors = []

# auth = HTTPBasicAuth()
def get_photo_path(photo_hash):
    photo_path = os.path.join(basedir, "app")
    photo_path = os.path.join(photo_path, "static")
    photo_path = os.path.join(photo_path, "UserImages")
    photo_path = os.path.join(photo_path, photo_hash + ".jpg")
    return photo_path


@api.route("/findG/getType")  # 获取寻味道请求类型
@auth.login_required
def getType():
    type_all = [
        {"TypeId": 1, "TypeName": "家乡小吃"},
        {"TypeId": 2, "TypeName": "地方特色小馆"},
        {"TypeId": 3, "TypeName": "香辣味"},
        {"TypeId": 4, "TypeName": "甜酸味"},
        {"TypeId": 5, "TypeName": "绝一味菜"},
    ]
    response = jsonify(type_all)
    response.status_code = 200
    return response


@api.route("/findG/getGraphByFindGId/<int:postID>", methods=["GET"])
def getFindGGraph(postID):
    post = FindG.query.filter_by(id=postID).first()
    
    if post == None :
        return bad_request("post not exitst")
    elif post.to_json()["photos"] is None:
        rep=jsonify({"data":[]})
        rep.status_code=200
        return rep
    else:
        rep =jsonify(
            {"data": [{"graphLocation": photo} for photo in post.to_json()["photos"]]}
        )
        rep.status_code=200
        return rep


@api.route("/findG/UploadFindGPhoto/<int:postID>", methods=["POST"])
@auth.login_required
def addPhoto(postID):
    post = FindG.query.filter_by(id=postID).first()

    if post.userId != g.current_user.id:
        return forbidden("Not your findG post.")
    # number = request.form.get("number")
    # number = int(number)
    if (
        post.photos is not None
        and len(post.photos.split()) >= current_app.config["POST_PHOTO_NUM"]
    ):
        return bad_request("photo number exceed limit.")
    print(request.files)
    photo = request.files['file']
    
    photo_hash = hashlib.md5(
        photo.read() + str(g.current_user.id).encode("utf-8")
    ).hexdigest()
    photo_path = get_photo_path(photo_hash)

    # print(photo_path)
    photo.seek(0)
    photo.save(photo_path)
    imgs = post.photos
    if imgs == None:
        imgs = ""
    imgs = imgs.split()
    # if number < len(imgs):
    #     imgs[number] = photo_hash
    # else:
    if photo_hash not in imgs:
        imgs += [photo_hash]
    imgs = " ".join(imgs)  # seperator being " "
    post.photos = imgs
    db.session.commit()
    return {"graphLocation": photo_hash}


@api.route("/findG/delGraphByLocation/<int:id>", methods=["POST"])
@auth.login_required
def del_photo(id):
    req = request.form
    loc = req["location"]
    postid = id

    post = FindG.query.filter_by(id=postid).first()
    if post.userId != g.current_user.id:
        return forbidden("Not your post.")
    imgs = post.photos
    imgs = imgs.split()
    imgs = [img for img in imgs if img != loc]
    imgs = " ".join(imgs)
    post.photos = imgs
    db.session.commit()

    os.remove(get_photo_path(loc))
    response = jsonify({})
    response.status_code = 200
    return response


@api.route("/findG/pageFind/<int:index>/<int:rows>")  # 得到所有寻味道请求的分页信息
@auth.login_required
def get_findG_all(index, rows):
    # if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
    #     return forbidden("Not logged in as an Admin")
    totals=FindG.query.count()
    
    findGs = FindG.query.paginate(page=index, per_page=rows).items
    response = jsonify(
        {"total": totals, "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


@api.route("/findG/pageFind/byName/<int:index>/<int:rows>/<input>")  # 模糊名称查找
@auth.login_required
def get_findG_byInput(index, rows, input):
    if g.current_user.level != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    findGs = (
        
        FindG.query.filter(FindG.name.like("%" + str(input) + "%"))
        .paginate(page=index, per_page=rows)
        .items
    )
    totals=FindG.query.filter(FindG.name.like("%" + str(input) + "%")).count()
    response = jsonify(
        {"total": totals, "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response

@api.route("/findG/modify",methods=["POST"])
@auth.login_required
def modify_findG():
    input = request.get_json()
    if g.current_user.id!=input["userId"]:
        return forbidden("Not your post")
    findgPost=FindG.query.filter_by(id=input["id"]).first()
    if findgPost is None:
        return forbidden("Post not exist")
    findgPost.description=input["description"]
    # Sun, 11 Dec 2022 16:54:03 GMT
    findgPost.endTime = datetime.datetime.strptime(input.get("endTime"), "%a, %d %b %Y %H:%M:%S %Z")
    findgPost.name=input["name"]
    findgPost.type=input["typeName"]
    
    
    db.session.commit()

    response=jsonify({"success":1})
    response.status_code=200
    return response
    
    
    

@api.route("/findG/pageFind/byType/<int:index>/<int:rows>/<int:typeId>")  # 按类型查找
@auth.login_required
def get_findG_byType(index, rows, typeId):
    # if g.current_user.level != current_app.config["ADMIN_PERMISSION"]:
    #     return forbidden("Not logged in as an Admin")
    findGs = None
    if typeId == 1:
        findGs = (
            FindG.query.filter_by(type="家乡小吃").paginate(page=index, per_page=rows).items
            
        )
        totals=FindG.query.filter_by(type="家乡小吃").count()
    elif typeId == 2:
        findGs = (
            FindG.query.filter_by(type="地方特色小馆")
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter_by(type="地方特色小馆").count()
    elif typeId == 3:
        findGs = (
            FindG.query.filter_by(type="香辣味").paginate(page=index, per_page=rows).items
        )
        totals=FindG.query.filter_by(type="香辣味").count()
    elif typeId == 4:
        findGs = (
            FindG.query.filter_by(type="甜酸味").paginate(page=index, per_page=rows).items
        )
        totals=FindG.query.filter_by(type="甜酸味").count()
    elif typeId == 5:
        findGs = (
            FindG.query.filter_by(type="绝一味菜").paginate(page=index, per_page=rows).items
        )
        totals=FindG.query.filter_by(type="绝一味菜").count()
    response = jsonify(
        {"total": totals, "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


@api.route("/findG/pageFind/byTypeAndName/<int:index>/<int:rows>/<int:value>/<input>")
#   按类型和模糊名称同时查找
@auth.login_required
def get_findG_byTypeAndName(index, rows, value, input):
    if g.current_user.level!= current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    findGs = None
    if value == 1:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "家乡小吃"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "家乡小吃"
            ).count()
    elif value == 2:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "地方特色小馆"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "地方特色小馆"
            ).count()
    elif value == 3:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "香辣味"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "香辣味"
            ).count()
    elif value == 4:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "甜酸味"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "甜酸味"
            ).count()
    elif value == 5:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "绝一味菜"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
        totals=FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "绝一味菜"
            ).count()
    response = jsonify(
        {"total": totals, "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


# 得到自己已经发布的所有寻味道请求的分页信息
@api.route("findG/pageFind/byUserId/<int:index>/<int:rows>/<int:id>")
@auth.login_required
def get_findG_byUserId(index, rows, id):
    findGs = FindG.query.filter_by(userId=id).paginate(page=index, per_page=rows).items
    totals=FindG.query.filter_by(userId=id).count()
    response = jsonify(
        {"total": totals, "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


# 点击显示详细信息按钮展示信息
@api.route("findG/findById/<int:id>")
@auth.login_required
def showInfo(id):
    findG = FindG.query.filter_by(id=id).first()
    return findG.to_json()


# 发布寻味道请求信息
@api.route("findG/add", methods=["POST"])
@auth.login_required
def addFindG():
    add_fG = request.get_json()  # 初始的字典
    endTime = datetime.datetime.strptime(add_fG.get("endTime"), "%Y-%m-%d %H:%M:%S")
    add_fG_fi = {
        "userId": add_fG.get("userId"),
        "type": add_fG.get("typeName"),
        "name": add_fG.get("name"),
        "description": add_fG.get("description"),
        "peopleCount": add_fG.get("peopleCount"),
        "endTime": endTime,
        #   "typeId":add_fG.get("typeId")
    }  # 最终的字典,因时间格式传入数据库时要经过转换
    fG_new = FindG(**add_fG_fi)
    fG_new.state = "待响应"
    db.session.add(fG_new)
    db.session.commit()
    response = jsonify({"state": "findG add success"})
    response.status_code = 200
    return response


# 删除寻味道请求
@api.route("findG/delById/<int:id>", methods=["POST"])
@auth.login_required
def delFindG(id):
    findG_del = FindG.query.get(id)
    pleEats = PleEat.query.filter_by(findG_id=id).all()
    if len(pleEats) == 0:
        db.session.delete(findG_del)
        db.session.commit()
        response = jsonify({"state": "findG delete success"})
        response.status_code = 200
        return response
    else:
        return forbidden("The findG already be responded")


# 填写请品鉴信息后 点击 确认按钮
@api.route("pleEat/add", methods=["POST"])
@auth.login_required
def addPleEat():
    req_json = request.get_json()
    pleEat = PleEat(**req_json)
    pleEat.state = 0  # 待接受
    db.session.add(pleEat)
    db.session.commit()
    response = jsonify({"state": "pleEat add success"})
    response.status_code = 200
    return response


# 管理员获取所有请品鉴信息
@api.route("pleEat/pageFind/<int:index>/<int:rows>")
@auth.login_required
def get_pleEat_all(index, rows):
    if g.current_user.level != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    pleEats = PleEat.query.paginate(page=index, per_page=rows).items
    
    totals= PleEat.query.count()
    response_raw = {"total": totals, "records": []}
    for pleEat in pleEats:
        findG = FindG.query.filter_by(id=pleEat.findG_id).first()
        response_raw["records"].append(
            {
                "id": pleEat.id,
                "findGId": pleEat.findG_id,
                "findGName": findG.name,
                "userId": pleEat.userId,
                "description": pleEat.description,
                "createTime": pleEat.createTime,
                "modifyTime": pleEat.modifyTime,
                "state": pleEat.state,
            }
        )
    response = jsonify(response_raw)
    response.status_code = 200
    return response


# 我的请品鉴列表
@api.route("pleEat/pageFind/byUser/<int:index>/<int:rows>/<int:userId>")
@auth.login_required
def get_my_pleEat(index, rows, userId):
    pleEats = (
        PleEat.query.filter_by(userId=userId).paginate(page=index, per_page=rows).items
    )
    totals= PleEat.query.filter_by(userId=userId).count()
    response_raw = {"total": totals, "records": []}
    for pleEat in pleEats:
        findG = FindG.query.filter_by(id=pleEat.findG_id).first()
        response_raw["records"].append(
            {
                "id": pleEat.id,
                "findGId": pleEat.findG_id,
                "findGName": findG.name,
                "userId": pleEat.userId,
                "description": pleEat.description,
                "createTime": pleEat.createTime,
                "modifyTime": pleEat.modifyTime,
                "state": pleEat.state,
            }
        )
    response = jsonify(response_raw)
    response.status_code = 200
    return response


# 判断是否有新的请品鉴消息
@api.route("pleEat/pageFind/byfindG/<int:index>/<int:rows>/<int:id>")
@auth.login_required
def judge(index, rows, id):
    pleEats = (
        PleEat.query.filter_by(findG_id=id).paginate(page=index, per_page=rows).items
    )
    totals= PleEat.query.filter_by(findG_id=id).count()
    response_raw = {"total": totals, "records": []}
    for pleEat in pleEats:
        findG = FindG.query.filter_by(id=id).first()
        response_raw["records"].append(
            {
                "id": pleEat.id,  # 品鉴响应标识
                "findGId": pleEat.findG_id,  # 味道请求标识
                "findGName": findG.name,  # 寻味道请求名字
                "userId": pleEat.userId,  # 响应用户ID（请品鉴）
                "description": pleEat.description,  # 响应描述（请品鉴）
                "createTime": pleEat.createTime,  # 创建时间（请品鉴）
                "modifyTime": pleEat.modifyTime,  # 修改时间（请品鉴）
                # 状态 0：待处理  1：同意  2：拒绝  3：取消
                "state": pleEat.state,
            }
        )
    response = jsonify(response_raw)
    response.code = 200
    return response


# TODO 同意/拒绝请求
@api.route("pleEat/modifyState", methods=["POST"])
@auth.login_required
def modifyState():
    req_json = request.get_json()
    pleEat = PleEat.query.get(req_json["id"])
    if pleEat == None:
        response = jsonify(
            {"exist state": "The pleEat id " + str(req_json["id"]) + " does not exist"}
        )
        return response
#     pleEat.state = req_json["state"]
    findG = FindG.query.get(pleEat.findG_id)
    # print(findG)
    
    # if findG.state == '待响应':
    if req_json["state"] == 1:  # 只可能为1或2，1表示"同意"
        pleEat.state = req_json["state"]
        success = Success(findG.id, 
        findG.userId, [pleEat.userId])
        success.fee = 3
        success.fee2 = 1
        success.type = findG.type
        db.session.add(success)
        db.session.commit()
        Date_str = datetime.datetime.strftime(
            success.date, "%Y-%m-%d") + " 00:00:00"
        Date = datetime.datetime.strptime(
            Date_str, "%Y-%m-%d %H:%M:%S")
        user = User.query.get(findG.userId)
        if (
            FeeSummary.query.filter_by(
                cityName=user.cityName, 
            Date=Date, type=findG.type).first() != None
        ):
            feeSummary_exist = FeeSummary.query.filter_by(
                cityName=user.cityName, 
            Date=Date, type=findG.type).first()
            feeSummary_exist.totalFee += 4
            db.session.commit()
        else:
            feeSummary = FeeSummary(user.cityName, 
            Date, findG.type)
            db.session.add(feeSummary)
            db.session.commit()
        findG.people += 1
        
        if findG.people == findG.peopleCount:
            findG.state = '已完成'
        db.session.commit()
        response = jsonify({"state": "The pleEat already be agreed"})
        
        return response

    else:  # 拒绝
        pleEat.state = req_json["state"]
        db.session.commit()
        response = jsonify({"state": "The pleEat already be refused"})
        
        return response
    # elif findG.state == '已完成':
    #     response = jsonify({"state: The findG already finish! Can't accept pleEat(s)!"})
    #     return response
    # elif findG.state == '已取消':
        


# 点击 确认修改请品鉴信息的按钮
@api.route("pleEat/modify", methods=["POST"])
@auth.login_required
def modifyPleEat():
    req_json = request.get_json()  # 获得前端请求
    pleEat = PleEat.query.filter_by(id=req_json["id"]).first()
    if req_json["description"] == "":
        response = bad_request("The pleEat description must be not null!")
        return response
    else:
        pleEat.description = req_json["description"]
        db.session.commit()
        response = jsonify({"state": "The pleEat modify success"})
        response.status_code = 200
        return response


# 点击 删除请品鉴信息按钮
@api.route("pleEat/deleteById/<int:id>", methods=["POST"])
@auth.login_required
def delPleEat(id):
    pleEat = PleEat.query.get(id)
    if pleEat == None:
        response = bad_request("This pleEat does not exist")
        return response
    db.session.delete(pleEat)
    db.session.commit()
    response = jsonify({"state": "This pleEat delete success"})
    response.status_code = 200
    return response


# class Success(db.Model):  # "寻味道"成功明细表

#     __tablename__ = "success"
#     id = db.Column(db.Integer, primary_key=True)  # 请求标识
#     userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 发布用户标识
#     user1 = db.relationship("User", backref="published", foreign_keys=[userId])
#     userId2 = db.Column(db.Integer, db.ForeignKey("users.id"))
#     commentors = db.relationship(
#         "User",
#         secondary=Success_Commentor,
#         backref=db.backref("commentor", lazy="dynamic"),
#         lazy="dynamic",
#     )
#     date = db.Column(db.DateTime, default=datetime.now)  # 达成日期
#     fee = db.Column(db.Integer)  # 发布者支付中介费
#     fee2 = db.Column(db.Integer)  # 响应者支付中介费
#     cityName = db.Column(db.Unicode(64))
#     Date = db.Column(db.DateTime)
#     type = db.Column(db.Unicode(32))  # 寻味道请求类型

# 点击 确认修改请品鉴信息的按钮
# @api.route("pleEat/modify", methods=['POST'])
# @auth.login_required
# def modify_pleEat():
#     req_json = request.get_json()


# class PleEat(db.Model):  # 请品鉴表
#     __tablename__ = "pleEat"
#     id = db.Column(db.Integer, primary_key=True)  # 品鉴响应标识
#     findG_id = db.Column(db.Integer, db.ForeignKey("findG.id"))  # 味道请求标识
#     userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 响应用户标识
#     description = db.Column(db.UnicodeText)  # 响应描述
#     createTime = db.Column(db.DateTime, default=datetime.now)  # 创建时间
#     modifyTime = db.Column(
#         db.DateTime, default=datetime.now, onupdate=datetime.now
#     )  # 修改时间
#     state = db.Column(db.Integer)  # 状态


#     id = db.Column(db.Integer, primary_key=True)  # 寻味道请求标识
#     userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 发布者标识
#     type = db.Column(db.Unicode(32))  # 寻味道请求类型
#     name = db.Column(db.Unicode(64))  # 寻味道请求名称
#     description = db.Column(db.UnicodeText)  # 寻味道请求描述
#     people = db.Column(db.Integer, default=0)   # 已响应人数
#     peopleCount = db.Column(db.Integer)     # 想要响应的总人数
#     price = db.Column(db.Integer)  # 最高单价
#     endTime = db.Column(db.DateTime)  # 请求结束时间
#     photo = db.Column(db.Unicode(128), nullable=True)
#     createTime = db.Column(db.DateTime, default=datetime.now)
#     modifyTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
#     state = db.Column(db.Unicode(32))
