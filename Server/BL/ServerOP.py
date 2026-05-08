import logging
from datetime import datetime,timedelta
import json
import bcrypt
from Server.COMM.ServerPRO import DEFAULT_AI_RESPONSE

MAX_AI_RETRIES=5
MAX_AI_USAGE_AMOUNT=500


# prepare Log file
LOG_FILE = '../Server LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def hash_password(password):
    password=password.encode()
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password, salt).decode()
    return hashed_password

def check_hash(password,hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def write_to_log(msg):
    logging.info(msg)
    print(msg)

def seconds_until_midnight():
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    midnight = datetime.combine(tomorrow, datetime.min.time())
    return (midnight - now).total_seconds()

def process_response(text: str):
        try:
            data = json.loads(text)
            data=data["recipes"]

            #basic structure check
            if not isinstance(data, list):
                raise ValueError("Not a list")

            #validate each recipe
            required_keys = {"type", "time", "name", "description", "difficulty", "nutrition", "data"}
            valid = []
            for r in data:
                if not isinstance(r, dict):
                    continue

                if set(r.keys()) != required_keys:
                    continue

                valid.append(r)

            if not valid:
                raise ValueError("No valid recipes")

            return {"recipes":valid}

        except Exception as e:
            write_to_log(f"[Server_BL] AI Processing failed: {e}")
            return json.loads(DEFAULT_AI_RESPONSE)

#get one ingredient list out of user's lists
def extract_all_ingredients(data):
    ingredients = []
    for key in data.keys():
        for ing in data[key]:
            ingredients.append(ing)
    return ingredients