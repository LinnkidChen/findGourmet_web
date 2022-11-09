# 环境相关

flask run之前务必设置：

```
    set FLASK_APP=findGourmet.py
    set FINDG_ADMIN=admin@admin.com

```

数据库中的数据

username :john | password: mynameisJohn | is admin
username :marry | password:mynameisMarry | not admin
Postman 使用方法：https://blog.csdn.net/legend818/article/details/117364048

如果发现奇怪的403报错，可能是端口被占用，使用-p 8888更换大一些的端口
