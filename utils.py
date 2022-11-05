import jwt 
import datetime
import traceback
secrete = "65e05c62082704288773d38c6532782e"

def get_jwt(user_id):
    payload={"user_id":user_id,
            "site":"what todo"
            }
    token = jwt.encode(payload, secrete, algorithm = "HS256")
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, secrete, algorithms = "HS256")
        return payload
    except:
        traceback.print_exc()
        return False    