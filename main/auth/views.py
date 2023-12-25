from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from main.models import *
from main import jwt#, cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from main.serializers import *
from main.auth import bp


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(username=data.get("username")).first()
    if user:
        if check_password_hash(user.password_hash, data.get('password')):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify(access_token=access_token, refresh_token=refresh_token, role=user.role)
    return jsonify({"msg":"Неверный логин или пароль"})


@bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklisted_token = BlacklistToken(
        user_id = get_jwt_identity(),
        token = jti,
        blacklisted_on = datetime.now()
        )
    db.session.add(blacklisted_token)
    db.session.commit()
    return jsonify({"msg": "Успешно вышел из системы"}), 200


@bp.route('/user-info', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def users():
    user = db.get_or_404(Users, get_jwt_identity())
    id = request.args.get('user_id', None)
    if user.role == 'a':
        if request.method == 'POST':
            data = request.get_json()
            try:
                user = Users(
                    first_name = data.get('first_name'),
                    username = data.get('username'),
                    password = data.get('password'),
                    role = data.get('role', None)
                )
                db.session.add(user)
                db.session.commit()
                return jsonify(msg="Created")
            except AssertionError as err:
                return jsonify(msg=f"{err}")
        elif request.method == 'GET':
            if id is not None:
                user = db.get_or_404(Users, id)
                return jsonify(user_schema.dump(user))
            users = Users.query.all()
            return jsonify(users_schema.dump(users))
        elif request.method == 'PUT' or request.method == 'PATCH':
            data = request.get_json()
            try:
                user = db.get_or_404(Users, id)
                user.first_name = data.get('first_name', user.first_name)
                if data.get('username'):
                    user.username = data.get('username')
                if data.get('password'):
                    user.password = data.get('password')
                user.role = data.get('role', user.role)
                db.session.commit()
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{err}")
        else:
            user = db.get_or_404(Users, id)
            db.session.delete(user)
            db.session.commit()
            return jsonify(msg='Deleted')
    else:
        return jsonify(msg="У вас нет полномочий на это действие")