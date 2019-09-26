# mongoDB.py
from pymongo import MongoClient, errors

from api import util
from typing import List
from api import result

# connect to mongoDB's collection, set connection timeout = 3s

class Connection(object):
    conn = None

    def __new__(cls, *args):
        if cls.conn is None:
            cls.conn = MongoClient(util.MONGO_URI, serverSelectionTimeoutMS=3000, connect=False)
        return cls.conn


def connect_collection(db_name, collection):
    result.write_log("info", "Connect to mongoDB, host: {0}, port: {1}, db: {2}, collection: {3}"
                     .format(util.MONGO_HOST, util.MONGO_PORT, db_name, collection))
    return Connection()[db_name][collection]

def store_rents():
    return connect_collection(util.MONGO_DB, util.MONGO_COLLECTION)

def gen_rent_data(**kwargs) -> List[dict]:
    """
    Parameters
    ----------
    sex_limited: int (0/both, 1/male, 2/female)
    phone_number: str
    city: str
    owner_sex: int (1/male, 2/female)
    owner_type: int (0/not home owner, 1/home owner)
    owner_last_name: str

    """
    try:
        if 'owner_type' in kwargs.keys():
            owner_type = kwargs.pop('owner_type')
            if owner_type == 1:
                kwargs['owner_type'] = '屋主'
            else:
                kwargs['owner_type'] = {'$ne': '屋主'}

        if 'owner_last_name' in kwargs.keys():
            owner_last_name = kwargs.pop('owner_last_name')
            kwargs['owner'] = {'$regex': owner_last_name}

        if 'sex_limited' in kwargs.keys():
            sex_limited = kwargs.pop('sex_limited')
            if sex_limited == 1:
                kwargs['sex_limited'] = {"$in":[0,1]}
            elif sex_limited == 2:
                kwargs['sex_limited'] = {"$in":[0,2]}
            elif sex_limited == 0:
                kwargs['sex_limited'] = 0


        data = store_rents().find(kwargs)
        print(kwargs)
        output = []
        for d in data:
            sex_limited = d['sex_limited']
            if sex_limited == 0:
                sex_limited = '男女皆可'
            elif sex_limited == 1:
                sex_limited = '男生'
            else:
                sex_limited = '女生'

            output.append({
                # 'house_id': d['house_id'],
                # 'city_name': d['city_name'],
                'house_type': d['house_type'],
                'house_status': d['house_status'],
                'owner': d['owner'],
                'owner_type': d['owner_type'],
                'phone_number': d['phone_number'],
                'sex_limited': sex_limited
            })

        return output

    except Exception as e:
        result.write_log("critical", "Failed to get data from mongoDB, "'{}'", method: gen_rent_data".format(e))
        return result.result(500, "Failed to get data from mongoDB, "'{}'", method: gen_rent_data".format(e))