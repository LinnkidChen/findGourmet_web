@api.route("/findG/getType")  # 获取寻味道请求类型
@auth.login_required
def getType():
    type_all = [
        {"findGTypeId": 1, "findGTypeName": "家乡小吃"},
        {"findGTypeId": 2, "findGTypeName": "地方特色小馆"},
        {"findGTypeId": 3, "findGTypeName": "香辣味"},
        {"findGTypeId": 4, "findGTypeName": "甜酸味"},
        {"findGTypeId": 5, "findGTypeName": "绝一味菜"},
    ]
    response = jsonify(type_all)
    response.status_code = 200
    return response


@api.route("/findG/pageFind/<int:index>/<int:rows>")  # 得到所有寻味道请求的分页信息
@auth.login_required
def get_findG_all(index, rows):
    if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    findGs = FindG.query.paginate(page=index, per_page=rows).items
    response = jsonify(
        {"total": len(findGs), "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


@api.route("/findG/pageFind/byName/<int:index>/<int:rows>/<input>")  # 模糊名称查找
@auth.login_required
def get_findG_byInput(index, rows, input):
    if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    findGs = (
        FindG.query.filter(FindG.name.like("%" + str(input) + "%"))
        .paginate(page=index, per_page=rows)
        .items
    )
    response = jsonify(
        {"total": len(findGs), "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


@api.route("/findG/pageFind/byType/<int:index>/<int:rows>/<int:typeId>")  # 按类型查找
@auth.login_required
def get_findG_byType(index, rows, typeId):
    if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    findGs = None
    if typeId == 1:
        findGs = (
            FindG.query.filter_by(type="家乡小吃").paginate(page=index, per_page=rows).items
        )
    elif typeId == 2:
        findGs = (
            FindG.query.filter_by(type="地方特色小馆")
            .paginate(page=index, per_page=rows)
            .items
        )
    elif typeId == 3:
        findGs = (
            FindG.query.filter_by(type="香辣味").paginate(page=index, per_page=rows).items
        )
    elif typeId == 4:
        findGs = (
            FindG.query.filter_by(type="甜酸味").paginate(page=index, per_page=rows).items
        )
    elif typeId == 5:
        findGs = (
            FindG.query.filter_by(type="绝一味菜").paginate(page=index, per_page=rows).items
        )
    response = jsonify(
        {"total": len(findGs), "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


@api.route("/findG/pageFind/byTypeAndName/<int:index>/<int:rows>/<int:value>/<input>")
#   按类型和模糊名称同时查找
@auth.login_required
def get_findG_byTypeAndName(index, rows, value, input):
    if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
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
    elif value == 2:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "地方特色小馆"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
    elif value == 3:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "香辣味"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
    elif value == 4:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "甜酸味"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
    elif value == 5:
        findGs = (
            FindG.query.filter(
                FindG.name.like("%" + str(input) + "%"), FindG.type == "绝一味菜"
            )
            .paginate(page=index, per_page=rows)
            .items
        )
    response = jsonify(
        {"total": len(findGs), "records": [findG.to_json() for findG in findGs]}
    )
    response.status_code = 200
    return response


# 得到自己已经发布的所有寻味道请求的分页信息
@api.route("findG/pageFind/byUserId/<int:index>/<int:rows>/<int:id>")
@auth.login_required
def get_findG_byUserId(index, rows, id):
    findGs = FindG.query.filter_by(userId=id).paginate(page=index, per_page=rows).items
    response = jsonify(
        {"total": len(findGs), "records": [findG.to_json() for findG in findGs]}
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
        "type": add_fG.get("type"),
        "name": add_fG.get("name"),
        "description": add_fG.get("description"),
        "peopleCount": add_fG.get("peopleCount"),
        "endTime": endTime,
        #   "typeId":add_fG.get("typeId")
    }  # 最终的字典,因时间格式传入数据库时要经过转换
    fG_new = FindG(**add_fG_fi)
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
    if g.current_user.role.permissions != current_app.config["ADMIN_PERMISSION"]:
        return forbidden("Not logged in as an Admin")
    pleEats = PleEat.query.paginate(page=index, per_page=rows).items
    response = jsonify(
        {"total": len(pleEats), "records": [pleEat.to_json() for pleEat in pleEats]}
    )
    response.status_code = 200
    return response


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
