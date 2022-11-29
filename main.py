from flask import Flask, request
from flask_cors import CORS, cross_origin
import models
from datetime import datetime
import traceback
from passlib.hash import sha256_crypt
import utils
salt="a!#$%sd"

app = Flask(__name__)
cors=CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
def home():
    print(request.headers)
    return "Server is up and running!"

@app.route("/user/signup/", methods = ["POST"])
def signup(db = models.session()):
    try:
        dict_data = request.get_json()
        check_email = db.query(models.User).filter(models.User.email==dict_data["email"]).all()
        if check_email != []:
            db.close()
            return {"detail":"this user is already exits"},400

        unhashed_pass = dict_data["password"] + salt
        password = sha256_crypt.encrypt(unhashed_pass)

        new_user_data = models.User(name = dict_data["name"],
                            user_name = dict_data["email"],
                            email = dict_data["email"],
                            password = password,
                            created_at = datetime.now())


        db.add(new_user_data)
        db.commit()
        db.close()

        return {"message":"user has been registered"}, 201

        
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404


@app.route("/user/login/", methods = ["POST"] )
@cross_origin()
def login(db = models.session()):
    try:
        user_data = request.get_json()
        db_user = db.query(models.User).filter(models.User.email==user_data["email"]).all()
        db.close()
        if db_user == []:
            return {"detail": "user not found" }, 404
        db_user = db_user[0]
        db_password = db_user.password
        # to verify password
        check_password = sha256_crypt.verify(user_data["password"]+salt, db_password)
        print(check_password)
        if check_password == True:
            user_id = db_user.user_id
            jwt_token = utils.get_jwt(user_id)
           
            return {"detail": "login succesfull", "token":jwt_token, "user_name":db_user.name} , 200
        return  {"detail":"invalid password"}, 404
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404

@app.route("/user/updatepassword/", methods=["POST"])
def updatepassword(db=models.session()):
    try:
        auth_headers=request.headers
        
        if "Authorization" not in  auth_headers:
            db.close()
            return {"details":"jwt token missing"}, 400

        auth_token = auth_headers["Authorization"].split(' ')[1]
        print(auth_token)
        user_id=utils.decode_jwt(auth_token)
        
        if user_id is False:
            db.close()
            return {"details":"invalid token"}

        user_id = user_id["user_id"]
        dict_data=request.get_json()

        db_password=db.query(models.User).filter(models.User.user_id==user_id)
        # to check old /new pasword
        old_password=dict_data["old_password"]+salt
        check_password = sha256_crypt.verify(old_password, db_password[0].password)
        print(check_password)
        if check_password==False:
            db.close()
            return {"details":"wrong old password"}
        new_password = sha256_crypt.encrypt(dict_data["new_password"]+salt)
        
        db_password[0].password = new_password
        
        db.commit()
        db.close()
            
        return {"detail": "password succesfull updated"} , 200
         

    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404 

    


@app.route("/task/create/",methods=["POST"])
def create_task(db=models.session()):
    try:
        auth_headers=request.headers
        
        if "Authorization" not in  auth_headers:
            db.close()
            return {"details":"jwt token missing"}, 400

        auth_token = auth_headers["Authorization"].split(' ')[1]
        print(auth_token)
        user_id=utils.decode_jwt(auth_token)
        
        if user_id is False:
            db.close()
            return {"details":"invalid token"}
        
        user_id = user_id["user_id"]
        payload = request.get_json()
        
        task_name = payload["task_name"]
        
        new_task_data = models.Task(
                                    user_id= user_id,
                                    task_name = task_name,
                                    is_deleted = 0,
                                    created_at = datetime.now()
                                    ) 
        db.add(new_task_data)
        db.commit()
        db.close()
        return {"details":"task has been added"}, 201 

         

    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404


@app.route("/task/get/", methods=["GET"])
def get_details(db=models.session()):
    try:
        auth_headers = request.headers
        if "Authorization" not in  auth_headers:
            db.close()
            return {"details":"jwt token missing"}, 400

        auth_token = auth_headers["Authorization"].split(' ')[1]
        print(auth_token)
        user_id=utils.decode_jwt(auth_token)
        
        if user_id is False:
            db.close()
            return {"details":"invalid token"}
        
        user_id = user_id["user_id"]
        user_data = db.query(models.Task).filter(models.Task.user_id==user_id,models.Task.is_deleted==0)
        user_data = user_data.order_by(models.Task.created_at.desc()).all()

        res = []
        
        for i in user_data:
            dict = {}
            dict["task_id"] = i.task_id
            dict["user_id"] = i.user_id
            dict["task"] = i.task_name
            dict["created_at"] = i.created_at
            res.append(dict)
        db.close()    

        return {"detail":"fetched succefully", "data": res }, 200

    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404  

@app.route("/task/edit/", methods=["PUT"])
def task_edit(db=models.session()):
    try:
        auth_headers = request.headers
        if "Authorization" not in  auth_headers:
            db.close()
            return {"details":"jwt token missing"}, 400

        auth_token = auth_headers["Authorization"].split(' ')[1]
        print(auth_token)
        user_id=utils.decode_jwt(auth_token)
        
        if user_id is False:
            db.close()
            return {"details":"invalid token"}
        
        user_id = user_id["user_id"]
        user_data = request.get_json()
        db_task = db.query(models.Task).filter(models.Task.task_id==user_data["task_id"], models.Task.is_deleted==0).all()
        
        #db_user will be a list of len 1 if found
        if db_task==[]:
            db.close()
            return {"detail":"no task found"}, 404

        db_task = db_task[0]
        db_task.task_name = user_data["task_name"]
        db.commit()
        db.close()
        return {"detail":"task has been updated"}, 204
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404 

@app.route("/task/delete/", methods=["DELETE"])
def delete_task(db=models.session()):
    try:
        auth_header = request.headers
        if "Authorization" not in auth_header :
            db.close()
            return {"details":"missing auth token"}, 404
        auth_token = auth_header["Authorization"].split(' ')[1]
        print(auth_token)
        
        user_id=utils.decode_jwt(auth_token)
         
        if user_id is False:
            db.close()
            return {"detalis":"invalid token "}
        user_id = user_id["user_id"]
        user_data = request.args
        db_task =  db.query(models.Task).filter(models.Task.task_id==user_data["task_id"], models.Task.is_deleted==0).all()

        if db_task == []:
            db.close()
            return {"details":"no task found"}

        db_task[0].is_deleted = 1
        db.commit()
        db.close()
        return{"details":"task has been deleted"}
    
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404 

@app.route("/user/update/", methods=["PUT"])
def update_name(db=models.session()):
    try:
        auth_header = request.headers
        if "Authorization" not in auth_header :
            db.close()
            return {"details":"missing auth token"}, 404
        auth_token = auth_header["Authorization"].split(' ')[1]
        print(auth_token)
        
        user_id=utils.decode_jwt(auth_token)
         
        if user_id is False:
            db.close()
            return {"detalis":"invalid token "},404
        user_id = user_id["user_id"]

        user_data = request.get_json()
        
        db_user =  db.query(models.User).filter(models.User.user_id==user_id).all()

        if db_user == []:
            db.close()
            return {"details":"no user found"},404

        db_user = db_user[0]
        db_user.user_name = user_data["user_name"]
        db.commit()
        db.close()
        return {"detail":"user has been updated"}, 204    
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404 

@app.route("/user/forgetpassword/", methods=["PUT"])
def forget_password(db=models.session()):
    try:
        user_data= request.args
        db_email=  db.query(models.User).filter(models.User.email==user_data["email"]).all()
        if db_email == []:
            db.close()
            return {"details":"please signup "}
        new_password=utils.get_random_string(12)
        unhashed_pass = new_password + salt
        password = sha256_crypt.encrypt(unhashed_pass)
        db_email[0].password=password
        db.commit()
        db.close()

        utils.mail_password(user_data["email"],new_password)
        return {"details":"password has been reset"}

    except Exception as e:
        traceback.print_exc()
        err = str(e)
        return {"detail":err}, 404 


if __name__ == "__main__":
    app.run(debug=True)