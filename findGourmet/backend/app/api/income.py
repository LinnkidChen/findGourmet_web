from flask import current_app, g, jsonify, request
from flask_httpauth import HTTPBasicAuth
import json

from ..models import Role, User, db, FindG, PleEat, Success, FeeSummary
from dateutil.relativedelta import relativedelta
from . import api
from .errors import bad_request, forbidden, unauthorized
from datetime import datetime
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
def get_date(input):
    try:
        result = datetime.strptime(input, "%Y-%m")  # 2022-01
    except:
        result = datetime.strptime(input, "%Y-%m-%d")

    return result


# @db.event.listens_for(Success, "after_insert")
# def success_after_insert(mapper, connection, target):
#     t_date = target.date
#     FS = (
#         FeeSummary.query.filter_by(cityName=target.cityName, type=target.type)
#         .filter()
#         .filter(Success.date >= target.date)
#         .filter(Success.date < target.date + relativedelta(days=+1))
#         .first()
#     )
#     if FS is None:
#         tmp = FeeSummary(
#             target.cityName,
#             target.date,
#             datetime(t_date.year, t_date.month, t_date.day),
#         )
#     else:
#         FS.totalFee += target.fee
#         FS.totalFee += target.fee2


# @db.event.listens_for(Success,"after_update")
@api.route("income/getIncomeByDayTimeByType/<start>/<end>")
def GetIncByDayByType(start, end):
    start = get_date(start)
    end = get_date(end)
    print(start,end)
    types = current_app.config["TYPES"]
    sumlist = []
    result = []
    i = start
    while i <= end:
        tmplist = []
        for type in types:
            tmps = (
                FeeSummary.query.filter_by(type=type)
                .filter(FeeSummary.Date >= i)
                .filter(FeeSummary.Date < (i + relativedelta(days=+1)))
                .all()
            )
            print("temps",tmps)
            if tmps is None:
                pass
            else:
                citysum = 0
                count = 0
                
                for tmp in tmps:
                    tmp.sum_all_fees()
                    citysum += tmp.totalFee
                    count += tmp.count
                tmplist += [
                        {
                            "name": type,
                            "money": citysum,
                            "count": count,
                            "date": i.strftime("%Y-%m-%d"),
                        }
                    ]
        sumlist += [tmplist]
        print(i)
        i=i+relativedelta(days=1)
    return jsonify(sumlist)


@api.route("income/getIncomeByMonthTimeByType/<start>/<end>")
# TODO need confirm
def GetIncByDayByType1(start, end):
    start = get_date(start)
    end = get_date(end)
    end = end + relativedelta(months=+1)
    types = current_app.config["TYPES"]
    sumlist = []
    result = []
    i = start
    while i <= end:
        tmplist = []
        for type in types:
            tmps = (
                FeeSummary.query.filter_by(type=type)
                .filter(FeeSummary.Date >= i)
                .filter(FeeSummary.Date < (i + relativedelta(months=+1)))
                .all()
            )
            if tmps is None:
                pass
            else:
                citysum = 0
                count = 0
                for tmp in tmps:
                    tmp.sum_all_fees()
                    citysum += tmp.totalFee
                    count += tmp.count
                tmplist += [
                    {
                        "name": type,
                        "money": citysum,
                        "count": count,
                        "date": i.strftime("%Y-%m-%d"),
                    }
                ]
        sumlist += [tmplist]
        i=i+relativedelta(months=1)
    return jsonify(sumlist)


@api.route("income/getIncomeByDayTimeByLocation/<start>/<end>/<city>")
def GetIncByDayByType2(start, end, city):
    start = get_date(start)
    end = get_date(end)
    types = current_app.config["TYPES"]
    sumlist = []
    result = []
    i = start
    while i <= end:
        tmplist = []
        for type in types:
            tmps = (
                FeeSummary.query.filter_by(type=type).filter_by(cityName=city)
                .filter(FeeSummary.Date >= i)
                .filter(FeeSummary.Date < (i + relativedelta(days=+1)))
                .all()
            )
            if tmps is None:
                pass
            else:
                citysum = 0
                count = 0
                for tmp in tmps:
                    tmp.sum_all_fees()
                    citysum += tmp.totalFee
                    count += tmp.count
                tmplist += [
                    {   "city":city,
                        "name": type,
                        "money": citysum,
                        "count": count,
                        "date": i.strftime("%Y-%m-%d"),
                    }
                ]
        sumlist += [tmplist]
        i=i+relativedelta(days=1)
    return jsonify(sumlist)



@api.route("income/getIncomeByMonthTimeByLocation/<start>/<end>/<city>")
def GetIncByDayByType3(start, end, city):
    print(city)
    start = get_date(start)
    end = get_date(end)
    end = end + relativedelta(months=+1)
    types = current_app.config["TYPES"]
    sumlist = []
    result = []
    i = start
    while i <= end:
        tmplist = []
        for type in types:
            tmps = (
                FeeSummary.query.filter_by(type=type).filter_by(cityName=city)
                .filter(FeeSummary.Date >= i)
                .filter(FeeSummary.Date < (i + relativedelta(months=+1)))
                .all()
            )
            if tmps is None:
                pass
            else:
                citysum = 0
                count = 0
                for tmp in tmps:
                    tmp.sum_all_fees()
                    citysum += tmp.totalFee
                    count += tmp.count
                tmplist += [
                    {   "name":type,
                        "location":city,
                        "money": citysum,
                        "count": count,
                        "date": i.strftime("%Y-%m-%d"),
                    }
                ]
        sumlist += [tmplist]
        i=i+relativedelta(months=1)
    return jsonify(sumlist)

# @api.route("/income/getIncomeByDayTimeByType/")
