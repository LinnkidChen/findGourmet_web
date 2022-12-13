from datetime import datetime
from itertools import product
from app import db
from app.models import User, Role, Permission, FindG, PleEat, Success, FeeSummary

# userid = [1, 2, 3, 4]
# type = ["家乡小吃", "地方特色小馆", "香辣味", "甜酸味"]
# name = ["A", "B", "C", "D"]
# desc = name
# mylist = []
# time = [datetime.now()]
# # for u,t,n,d,ti in product(userid,type,name,desc,time):
# #     add_fG_fi = {"userId": u,"type":t,"name":n,"description": d,"peopleCount": 3,"endTime": ti}
# #     fg=FindG(**add_fG_fi)
# #     mylist+=[fg]


# fgid = [i for i in range(1, 30)]
# pleeatUid = [5, 6, 7, 8]
# pleDes = ["a", "b", "c", "d"]
# # for u, d, f in product(pleeatUid, pleDes, fgid):
# #     tmp = {"userId": u, "findG_id": f, "description": d}
# #     tmp = PleEat(**tmp)
# #     mylist += [tmp]

# allposts = FindG.query.all()

# for post in allposts:
#     commentor = []
#     for PL in post.PleEats:
#         commentor += [PL.userId]
#     tmp = Success(post.id, post.userId, commentor)
#     mylist += [tmp]
mylist=User.query.all()
for user in mylist:
    if user.role_id==1:
        user.level=1
    else:
        user.level=2
        
# db.session.add_all(mylist)
db.session.commit()
