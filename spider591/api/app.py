from flask import Flask, request
from flask_caching import Cache
import urllib.parse

from api import result
from api import mongoDB


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.before_request
def before_request():

    result.write_log('info', "User requests info, path: {0}, method: {1}, ip: {2}, agent: {3}"
                     .format(str(request.path), str(request.method), str(request.remote_addr), str(request.user_agent)))


@app.after_request
def after_request(response):
    resp = response.get_json()

    if resp is not None:
        code, status, description = resp["code"], resp["status"], resp["description"]
        response_info = "Server response info, code: {0}, status: {1}, description: {2}"

        if code == 500:
            result.write_log('warning', response_info.format(code, status, description))
        else:
            result.write_log('info', response_info.format(code, status, description))

    return response


@app.errorhandler(400)
def method_400(e):
    return result.result(400, "the browser (or proxy) sent a request that this server could not understand")


@app.errorhandler(404)
def method_404(e):
    return result.result(404, "requested URL was not found on the server")


@app.errorhandler(405)
def method_405(e):
    return result.result(405, "http method is not allowed for the requested URL")


@app.errorhandler(500)
def method_500(e):
    return result.result(500, "something has gone wrong on the restful api server")

def cache_key():
    args = request.args
    key = request.path + '?' + urllib.parse.urlencode([
        (k, v) for k in sorted(args) for v in sorted(args.getlist(k))
    ])
    #print(key)
    return key

@app.route("/rent591")
@cache.cached(timeout=5 * 60, key_prefix=cache_key)

def rent():
    params = request.args.to_dict()

    field_type = {
        'sex_limited': int,
        'phone_number': str,
        'city_name': str,
        'owner_sex': int,
        'owner_type': int,
        'owner_last_name': str
    }

    for p in params.keys():
        if p not in field_type.keys():
            return result.result(400, f"'{p}' is not a valid param.")
        try:
            params[p] = field_type[p](params[p])
        except Exception:
            return result.result(400, f"value of param '{p}' is not valid.")

    res = mongoDB.gen_rent_data(**params)
    return result.result(200, res, "The list of rent data.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)