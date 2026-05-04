import logging
from datetime import datetime,timedelta
import json
import bcrypt
from Server.COMM.ServerPRO import DEFAULT_AI_RESPONSE

# prepare Log file
LOG_FILE = '../../LOG.log'
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


def process_for_json_loads(text: str):
    json_str = ""
    try:
        # Strip leading/trailing whitespace
        text = text.strip()

        # Find first [ and last ]
        start = text.find('[')
        end = text.rfind(']')

        if start == -1 or end == -1 or start > end:
            return json.loads(DEFAULT_AI_RESPONSE)

        json_str = text[start:end + 1]
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        write_to_log(f"JSON parsing failed: {str(e)}, extracted: {json_str}")
        return json.loads(DEFAULT_AI_RESPONSE)

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
            write_to_log(f"Processing failed: {str(e)}")
            return json.loads(DEFAULT_AI_RESPONSE)
