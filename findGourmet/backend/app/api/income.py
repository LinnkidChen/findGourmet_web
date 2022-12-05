from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth
import json

from ..models import Role, User, db, FindG, PleEat, Success, FeeSummary
from dateutil.relativedelta import relativedelta
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

# @db.event.listens_for(FindG, "after_insert")
# def receive_after_insert(mapper, connection, target):
#     print((mapper))
#     print(connection)
#     print(target.id)
#     print("insert.......")
@db.event.listens_for(Success, "after_insert")
def success_after_insert(mapper, connection, target):
    t_date = target.date
    FS = (
        FeeSummary.query.filter_by(cityName=target.cityName, type=target.type)
        .filter()
        .filter(Success.date >= target.date)
        .filter(Success.date < target.date + relativedelta(days=+1))
        .first()
    )
    if FS is None:
        tmp = FeeSummary(
            target.cityName,
            target.date,
            datetime(t_date.year, t_date.month, t_date.day),
        )
    else:
        FS.totalFee += target.fee
        FS.totalFee += target.fee2


# @db.event.listens_for(Success,"after_update")
@api.route("/income/getIncomeByDayTimeByType/<start>/<end>")
def GetIncByDayByType(start, end):
    pass


@api.route("/income/getIncomeByMonthTimeByType/<start>/<end>")
def GetIncByDayByType(start, end):
    pass


@api.route("/income/getIncomeByDayTimeByLocation/<start>/<end>/<city>")
def GetIncByDayByType(start, end, city):
    pass


@api.route("/income/getIncomeByMonthTimeByLocation/<start>/<end>/<city>")
def GetIncByDayByType(start, end, city):
    pass


# @api.route("/income/getIncomeByDayTimeByType/")
