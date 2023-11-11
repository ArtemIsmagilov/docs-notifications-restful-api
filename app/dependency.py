import bson
from bson import ObjectId
from fastapi import HTTPException


def get_object_id(data_id: str):
    try:
        _id = ObjectId(data_id)
    except bson.errors.InvalidId as exp:
        raise HTTPException(
            status_code=422,
            detail='%s is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string' % data_id
        )
    else:
        return _id
