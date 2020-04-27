from flask import Blueprint, request, make_response, jsonify
from . import _Config
import uuid
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from .queries import getusers, gethashtagkeys, gettweetsbyhashtag,\
    gettweetsbykeyword, getsentimentbyday, createtester, getatester,\
    getatesterbyid


Api = Blueprint('api', __name__, url_prefix="/api")


def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = None

        if 'x-access-auth_token' in request.headers:
            auth_token = request.headers['x-access-auth_token']
        if not auth_token:
            return jsonify({"status": "Authentification token is missing"}),\
                   401
        try:
            secret = _Config.SECRET_KEY
            data = jwt.decode(auth_token, secret)
            current_tester = getatesterbyid(data["public_id"])
            return f(current_tester, *args, **kwargs)
        except:
            return jsonify({"status": "Authentification token is invalid"}),\
                   401
    return decorated


@Api.route('/createtester', methods=['POST'])
def create_tester():
    data = request.get_json()
    pid = str(uuid.uuid4())
    status = ''
    hashed_pass = generate_password_hash(data['password'], method='sha256')
    email = data['email']
    accesstoken = data['token']
    status = createtester(pid, email, hashed_pass, accesstoken)
    return status


@Api.route('/testerlogin')
def tester_login():
    auth = request.authorization
    resp = make_response("Could not verify", 401, {
        "WWW-Authenticate": "Basic realm='Login required!'"})
    if not auth or not auth.username or not auth.password:
        return resp
    else:
        exists, tester = getatester(auth.username)
        if exists is False:
            resp = make_response("User doesn't exist", 401, {
                "WWW-Authenticate": "Basic realm='Login required!'"})
            return resp
        elif check_password_hash(tester.password, auth.password):
            secret = _Config.SECRET_KEY
            expiration_date = datetime.datetime.utcnow() +\
                datetime.timedelta(minutes=30)
            auth_msg = {"public_id": tester.public_id,
                        "exp": expiration_date}
            auth_token = jwt.encode(auth_msg, secret)
            token = {"Auth Token": auth_token.decode('utf-8')}
            return jsonify(token)
    return resp


@Api.route('/getallusers', methods=['GET'])
@require_token
def AllUsers(current_tester):
    print(current_tester.public_id)
    return getusers()


@Api.route('/gethashtagkeys', methods=['GET'])
@require_token
def HashtagKeys(current_tester):
    return gethashtagkeys()


@Api.route('/gethashtagsinfo', methods=['GET'])
@require_token
def HashtagsInfo(current_tester):
    return gettweetsbyhashtag()


@Api.route('/getkeywordsinfo', methods=['GET'])
@require_token
def KeywordssInfo(current_tester):
    return gettweetsbykeyword()


@Api.route('/getsentimentbydate', methods=['GET'])
@require_token
def SentimentEvolution(current_tester):
    print(current_tester)
    return getsentimentbyday()
