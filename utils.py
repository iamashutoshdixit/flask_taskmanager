import jwt 
import datetime
import traceback
import random
import string
import smtplib
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

def get_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    result_str = ''.join(random.choice(characters) for i in range(length))
    return result_str



def mail_password(rescivermail,password):
    
    SUBJECT="Automated password mail"
    TEXT=f"this is an automated mail\n Your new password {password}"
 
    s = smtplib.SMTP ('smtp.gmail.com', 587)

    s.starttls()

    s.login("csashutoshdixit17@gmail.com", "qltzzoatvjxrlfng")

    message = f'Subject: {SUBJECT}\n\n{TEXT}'

    s.sendmail("csashutoshdixit17@gmailcom", rescivermail, message)
    print("mail send")

mail_password("ecetushar22@gmail.com","jgjhhggkjhjhgjgvkjh")

