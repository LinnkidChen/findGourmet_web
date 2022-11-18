# please set environment variable FLASK_APP=findGourmet.py

import os
import click
from flask_migrate import Migrate
from app import create_app, db

# from app.models import User, Follow, Role, Permission, Post, Comment
from app.models import User, Role, Permission, FindG, PleEat

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

# save time to set User as FindG.user when operating database commandshell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, FindG=FindG, PleEat=PleEat)
