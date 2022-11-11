# 环境相关

flask run之前务必设置：

```
    set FLASK_APP=findGourmet.py
    set FINDG_ADMIN=admin@admin.com

```

数据库中的数据

| username | password | usertype
|---|---|---|
| john | mynameisJohn | is admin | 
| marry | mynameisMarry | not admin |
| 一个中文名字 |  | not admin |
| 一个中文管理员用户 |  | admin |

为用户添加密码的方法（shell）

```
flask shell

user=User.query.filter_by(username="target_username").first()
user.password="Target_Password"

db.session.commit()
```

关于model中时间的用法
<https://blog.csdn.net/aobian2884/article/details/101404395>

Postman 使用方法：<https://blog.csdn.net/legend818/article/details/117364048>

如果发现奇怪的403报错，可能是端口被占用，使用-p 8888更换大一些的端口

一个作弊的Token:"cheatToken" 会将当前的人物设置为第一个管理员
请将Token写在Postman- authorization-basicauth中

在使用Token登录时，请务必将password设置为空

数据库中间件分页方法
<https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_350days.html>