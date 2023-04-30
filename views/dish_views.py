from flask import Blueprint
from flask import render_template, request, make_response
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
from dto.SessionInfo import SessionInfo
from sqlalchemy import select
import table.Model as DB
import json

bp = Blueprint('dish', __name__, url_prefix='/dish')


@bp.route("/my-dishes", methods=['GET'])
def my_dishes():
    session_value = request.cookies.get('my-session')
    session_value_arr = session_value.split('-')

    stmt = select(DB.DailyDish, DB.DailyDishDetail).join(DB.DailyDishDetail,
                                                       DB.DailyDish.id == DB.DailyDishDetail.daily_dish_id) \
        .filter(
        DB.DailyDish.create_user_id == session_value_arr[0])
        #.add_columns(DB.DailyDishDetail.dishes, DB.DailyDishDetail.id)\

    result = []
    for d in DB.db.session.execute(stmt):
        r = {}
        r['dish_id'] = d.DailyDish.id
        r['dishes'] = d.DailyDishDetail.dishes
        r['create_at'] = str(d.DailyDishDetail.create_at)
        result.append(r)

    return result
