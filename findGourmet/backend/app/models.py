from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

# Rich Text requirement
# from markdown import markdown
# import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager
from dateutil.relativedelta import relativedelta
from itertools import product

# TODO need modification,copied from flasky
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    # def insert_roles():
    #     roles = {
    #         'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
    #         'Moderator': [Permission.FOLLOW, Permission.COMMENT,
    #                       Permission.WRITE, Permission.MODERATE],
    #         'Administrator': [Permission.FOLLOW, Permission.COMMENT,
    #                           Permission.WRITE, Permission.MODERATE,
    #                           Permission.ADMIN],
    #     }
    #     default_role = 'User'
    #     for r in roles:
    #         role = Role.query.filter_by(name=r).first()
    #         if role is None:
    #             role = Role(name=r)
    #         role.reset_permissions()
    #         for perm in roles[r]:
    #             role.add_permission(perm)
    #         role.default = (role.name == default_role)
    #         db.session.add(role)
    #     db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return "<Role %r>" % self.name


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    """
    初始化方法：User(username="1",role_str="Admin"/"User")
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.Unicode(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    password_hash = db.Column(db.String(128))
    realName = db.Column(db.Unicode(64))
    documentTypeName = db.Column(db.Unicode(64))
    documentNumber = db.Column(db.String(32))
    phoneNumber = db.Column(db.String(16))
    level = db.Column(db.Integer)
    introduce = db.Column(db.Text)
    cityName = db.Column(db.Unicode(64))
    createTime = db.Column(db.DateTime, default=datetime.now)
    modifyTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    role_str = db.Column(db.String(8))
    # confirmed = db.Column(db.Boolean, default=False)
    # name = db.Column(db.String(64))
    # location = db.Column(db.String(64))
    # about_me = db.Column(db.Text())
    # member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    # last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # avatar_hash = db.Column(db.String(32))
    # posts = db.relationship('Post', backref='author', lazy='dynamic')
    # followed = db.relationship('Follow',
    #                            foreign_keys=[Follow.follower_id],
    #                            backref=db.backref('follower', lazy='joined'),
    #                            lazy='dynamic',
    #                            cascade='all, delete-orphan')
    # followers = db.relationship('Follow',
    #                             foreign_keys=[Follow.followed_id],
    #                             backref=db.backref('followed', lazy='joined'),
    #                             lazy='dynamic',
    #                             cascade='all, delete-orphan')
    # comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    # def add_self_follows():
    #     for user in User.query.all():
    #         if not user.is_following(user):
    #             user.follow(user)
    #             db.session.add(user)
    #             db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.role_str == "Admin":  # set to admin
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.level = self.role.permissions
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = self.gravatar_hash()
        # self.follow(self)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        return_value = s.dumps({"confirm": self.id}).decode("utf-8")
        return return_value

    # def confirm(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     return True

    # def generate_reset_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    # TODO need modification
    # def reset_password(token, new_password):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     user = User.query.get(data.get('reset'))
    #     if user is None:
    #         return False
    #     user.password = new_password
    #     db.session.add(user)
    #     return True

    # def generate_email_change_token(self, new_email, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps(
    #         {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    # def change_email(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     if data.get('change_email') != self.id:
    #         return False
    #     new_email = data.get('new_email')
    #     if new_email is None:
    #         return False
    #     if self.query.filter_by(email=new_email).first() is not None:
    #         return False
    #     self.email = new_email
    #     self.avatar_hash = self.gravatar_hash()
    #     db.session.add(self)
    #     return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # def gravatar_hash(self):
    #     return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # def gravatar(self, size=100, default='identicon', rating='g'):
    #     url = 'https://secure.gravatar.com/avatar'
    #     hash = self.avatar_hash or self.gravatar_hash()
    #     return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
    #         url=url, hash=hash, size=size, default=default, rating=rating)

    # def follow(self, user):
    #     if not self.is_following(user):
    #         f = Follow(follower=self, followed=user)
    #         db.session.add(f)

    # def unfollow(self, user):
    #     f = self.followed.filter_by(followed_id=user.id).first()
    #     if f:
    #         db.session.delete(f)

    # def is_following(self, user):
    #     if user.id is None:
    #         return False
    #     return self.followed.filter_by(
    #         followed_id=user.id).first() is not None

    # def is_followed_by(self, user):
    #     if user.id is None:
    #         return False
    #     return self.followers.filter_by(
    #         follower_id=user.id).first() is not None

    @property
    # def followed_posts(self):
    #     return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
    #         .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            # 'url': url_for('api.get_user', id=self.id),
            "id": self.id,
            "username": self.username,
            "userType": self.role_str,
            "documentTypeName": self.documentTypeName,
            "documentNumber": self.documentNumber,
            "phoneNumber": self.phoneNumber,
            "level": self.role_id,
            "introduce": self.introduce,
            "cityName": self.cityName,
            "createTime": self.createTime,
            "modifyTime": self.modifyTime
            # 'posts_url': url_for('api.get_user_posts', id=self.id),
            # 'followed_posts_url': url_for('api.get_user_followed_posts',
            #   id=self.id),
            # 'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self):
        s = Serializer(
            current_app.config["SECRET_KEY"],
        )
        return_value = s.dumps({"id": self.id})

        return return_value

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            print(current_app.config["TOKEN_EXPIRE"])
            data = s.loads(token, max_age=current_app.config["TOKEN_EXPIRE"])
        except:
            return None
        return User.query.get(data["id"])

    @staticmethod
    def from_js(json_post):
        username = json_post.get("username")
        password = json_post.get("password")
        role_str = json_post.get("role")
        realName = json_post.get("realName")
        documentTypeName = json_post.get("documentTypeName")
        documentNumber = json_post.get("documentNumber")
        phoneNumber = json_post.get("phoneNumber")
        role_id = json_post.get("level")
        introduce = json_post.get("introduce")
        cityName = json_post.get("cityName")
        # role_id = json_post.get("level")

        if password is None or username is None:
            return None

        user = User(
            username=username,
            role_str=role_str,
            realName=realName,
            documentNumber=documentNumber,
            documentTypeName=documentTypeName,
            phoneNumber=phoneNumber,
            role_id=role_id,
            introduce=introduce,
            cityName=cityName,
        )
        user.password = password
        return user

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class FindG(db.Model):
    __tablename__ = "findG"
    id = db.Column(db.Integer, primary_key=True)  # 寻味道请求标识
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 发布者标识
    type = db.Column(db.Unicode(32))  # 寻味道请求类型
    name = db.Column(db.Unicode(64))  # 寻味道请求名称
    description = db.Column(db.UnicodeText)  # 寻味道请求描述
    people = db.Column(db.Integer, default=0)  # 已响应人数
    peopleCount = db.Column(db.Integer)  # 想要响应的总人数
    price = db.Column(db.Integer)  # 最高单价
    endTime = db.Column(db.DateTime)  # 请求结束时间
    # photo = db.Column(db.UnicodeText, nullable=True)
    createTime = db.Column(db.DateTime, default=datetime.now)
    modifyTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    state = db.Column(db.Unicode(32))
    photos = db.Column(db.String(128))  # 储存图片的散列值，使用md5加密。用空格分割，最多存储3个。
    author = db.relationship("User", backref=db.backref("posts"))
    successPosts = db.relationship("Success", backref="FindGPosts")

    def to_json(self):
        if self.photos is None:
            photos=None
        else:
            photos=self.photos.split()
        json_findG = {
            "id": self.id,
            "userId": self.userId,
            "typeName": self.type,
            "name": self.name,
            "description": self.description,
            "people": self.people,
            "peopleCount": self.peopleCount,
            "price": self.price,
            "endTime": self.endTime,
            # "photo": self.photo,
            "createTime": self.createTime,
            "modifyTime": self.modifyTime,
            "stateName": self.state,
            "photos": photos,
        }
        return json_findG

    # @staticmethod
    # def from_js(json_post):
    #     id = json_post.get("id")

    def __repr__(self):
        return "<FindG %r>" % self.name


class PleEat(db.Model):  # 请品鉴表
    __tablename__ = "pleEat"
    id = db.Column(db.Integer, primary_key=True)  # 品鉴响应标识
    findG_id = db.Column(db.Integer, db.ForeignKey("findG.id"))  # 味道请求标识
    # findG_name = db.Column(db.Unicode(64),db.ForeignKey("findG.name"))    # 味道请求名称
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 响应用户标识
    description = db.Column(db.UnicodeText)  # 响应描述
    createTime = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    modifyTime = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 修改时间
    state = db.Column(db.Integer,default=0)  # 状态
    FindGpost = db.relationship("FindG", backref=db.backref("PleEats"))

    def to_json(self):
        js_pleEat = {
            "id": self.id,
            "findG_id": self.findG_id,
            # "findG_name": self.findG_name,
            "userId": self.userId,
            "description": self.description,
            "createTime": self.createTime,
            "modifyTime": self.modifyTime,
            "state": self.state,
        }
        return js_pleEat


Success_Commentor = db.Table(
    "success_commenter",
    db.Column("success_id", db.Integer, db.ForeignKey("success.id")),
    db.Column("commentor_id", db.Integer, db.ForeignKey("users.id")),
)


class Success(db.Model):  # "寻味道"成功明细表

    __tablename__ = "success"
    id = db.Column(db.Integer, primary_key=True)
    findGId = db.Column(db.Integer, db.ForeignKey("findG.id"))  # 请求标识
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))  # 发布用户标识
    user1 = db.relationship("User", backref="published", foreign_keys=[userId])
    userId2 = db.Column(db.Integer, db.ForeignKey("users.id"))
    commentors = db.relationship(
        "User",
        secondary=Success_Commentor,
        backref=db.backref("commentor", lazy="dynamic"),
        lazy="dynamic",
    )
    date = db.Column(db.DateTime, default=datetime.now)  # 达成日期
    fee = db.Column(db.Integer)  # 发布者支付中介费
    fee2 = db.Column(db.Integer)  # 响应者支付中介费
    cityName = db.Column(db.Unicode(64))
    type = db.Column(db.Unicode(32))  # 寻味道请求类型

    def __init__(
        self,
        id,
        userid1,
        commentorIds,
    ) -> None:
        self.findGId = id
        self.user1 = User.query.filter_by(id=userid1).first()
        print(commentorIds)
        for commentorId in commentorIds:
            self.commentors.append(User.query.filter_by(id=commentorId).first())
        self.cityName = self.user1.cityName

    #    self.type = self.findGPost.type

    def __repr__(self):
        return f"Success {self.user1.username} {self.id}"


class FeeSummary(db.Model):
    # 根据每天，城市，类别划分计算总的钱

    __tablename__ = "feeSummary"
    id = db.Column(db.Integer, primary_key=True)
    cityName = db.Column(db.Unicode(64))
    totalFee = db.Column(db.Integer, default=0)
    Date = db.Column(db.DateTime)
    type = db.Column(db.Unicode(32))  # 寻味道请求类型
    modTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    count = db.Column(db.Integer,default=0)

    def __init__(self, cityName, Date, type):
        if (
            FeeSummary.query.filter_by(cityName=cityName, Date=Date, type=type).first()
            is not None
        ):
            raise Exception("already exist")
        else:
            self.cityName = cityName
            self.Date = Date
            self.type = type
            self.sum_all_fees()

    def to_json(self):
        tmp = {
            "name": self.type,
            "money": self.totalFee,
            "count": self.count,
            "date": self.date,
        }
        return tmp

    def sum_all_fees(self):
        # FIXME 待测试
        tickets = (
            Success.query.filter_by(cityName=self.cityName, type=self.type)
            .filter(Success.date >= self.Date)
            .filter(Success.date < self.Date + relativedelta(days=+1))
        ).all()
        sum = 0
        for ticket in tickets:
            sum += ticket.fee
            sum += ticket.fee2
        self.totalFee = sum
        self.count = len(tickets)
        db.session.commit()

    @staticmethod
    def create_fee_summary():
        # FIXME：待测试
        all_summary = FeeSummary.query.all()
        all_city = User.query.filter(User.posts).all()
        all_city = [user.city for user in all_city]
        all_type = FindG.query.with_entities(FindG.type).distinct().all()
        all_type = [type[0] for type in all_type]
        all_dates = FindG.query.with_entities(FindG.modifyTime).distinct().all()
        all_dates = [date[0] for date in all_dates]
        unique_dates = []
        feesums = []
        for date in all_dates:
            tmp = datetime(date.year, date.month, date.day)
            if tmp not in unique_dates:
                unique_dates += [tmp]
        for type, city, date in product(all_type, all_city, all_dates):
            posts = (
                Success.query.filter_by(type=type, cityName=city)
                .filter(Success.date >= date)
                .filter(Success.date < date + relativedelta(days=+1))
            )
            costsum = 0
            for post in posts:
                costsum += post.fee
                costsum += post.fee2
            feesum = FeeSummary(city, date, type)
            feesum.totalFee = costsum
            feesum.count = len(posts)
            feesums += [feesum]
        for summary in all_summary:
            db.session.delete(summary)
        db.session.add_all(feesums)
        db.session.commit()


# class Post(db.Model):
#     __tablename__ = 'posts'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     body_html = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     comments = db.relationship('Comment', backref='post', lazy='dynamic')

#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
#                         'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
#                         'h1', 'h2', 'h3', 'p']
#         target.body_html = bleach.linkify(bleach.clean(
#             markdown(value, output_format='html'),
#             tags=allowed_tags, strip=True))

#     def to_json(self):
#         json_post = {
#             'url': url_for('api.get_post', id=self.id),
#             'body': self.body,
#             'body_html': self.body_html,
#             'timestamp': self.timestamp,
#             'author_url': url_for('api.get_user', id=self.author_id),
#             'comments_url': url_for('api.get_post_comments', id=self.id),
#             'comment_count': self.comments.count()
#         }
#         return json_post

# @staticmethod
# def from_json(json_post):
#     body = json_post.get('body')
#     if body is None or body == '':
#         raise ValidationError('post does not have a body')
#     return Post(body=body)


# db.event.listen(Post.body, 'set', Post.on_changed_body)


# class Comment(db.Model):
#     __tablename__ = 'comments'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     body_html = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     disabled = db.Column(db.Boolean)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
#                         'strong']
#         target.body_html = bleach.linkify(bleach.clean(
#             markdown(value, output_format='html'),
#             tags=allowed_tags, strip=True))

#     def to_json(self):
#         json_comment = {
#             'url': url_for('api.get_comment', id=self.id),
#             'post_url': url_for('api.get_post', id=self.post_id),
#             'body': self.body,
#             'body_html': self.body_html,
#             'timestamp': self.timestamp,
#             'author_url': url_for('api.get_user', id=self.author_id),
#         }
#         return json_comment

#     @staticmethod
#     def from_json(json_comment):
#         body = json_comment.get('body')
#         if body is None or body == '':
#             raise ValidationError('comment does not have a body')
#         return Comment(body=body)


# db.event.listen(Comment.body, 'set', Comment.on_changed_body)
