#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
import hashlib
import DB_CONFIG
from DB_UTIL import db_access

app = Flask(__name__)
api = Api(app)

'''

class NAME(Resource):
    def get(self):
        sqlProc=''
        sqlArgs = []
        result = db_access(sqlProc,sqlArgs)
        return make_response(jsonify({'response': result}), 200)
api.add_resource(NAME, '/PATH')

'''

#region User Management
class Register(Resource):
    def post(self):
        rejectionReason=""
        
        #Data
        data=request.json
        name=data['username']
        password=data['user_password']
        email=data['email']
        
        #Pre-DB validation
        if len(name)>30 or not name.isalnum():
            rejectionReason+="Your username is either over the character limit(30)\n"
            rejectionReason+="Or your username did not only contain alphanumerics (a-Z,0-9)\n"
        elif len(name)<4:
            rejectionReason+="Your username is under the character limit(4)\n"
        if len(password)>255 or not password.isalnum():
            rejectionReason+="Your password is either over the character limit(255)\n"
            rejectionReason+="Or your password did not only contain alphanumerics (a-Z,0-9)\n"
        if rejectionReason:
            return make_response(jsonify({"response": rejectionReason}),400)

        #Add user in user table
        sqlProc='registerUser'
        sqlArgs = [name,password,]
        try:
            rows,count = db_access(sqlProc,sqlArgs)
        except Exception as e:
            if "Database Error:(1062" in str(e):
                return make_response(jsonify({"response": "Duplicate Username"}), 400)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)

        #Add new user in emails table
        new_user_id=rows[0]['user_id']
        sqlProc='preValidateUser'
        email_hash=hashlib.sha512(email.encode("UTF-8")).hexdigest()
        sqlArgs=[new_user_id,email,email_hash]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            #Delete user because of failed prevalidation?
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(Register, '/register')

class Validate(Resource):
    def get(self,id):
        sqlProc='validateUser'
        sqlArgs = [id,]
        rows,count = db_access(sqlProc,sqlArgs)
        if count==0:
            return make_response(jsonify({"response": "No changes applied"}), 200)
        return make_response(jsonify({"response": "User has been validated"}), 200)
api.add_resource(Validate, "/validate/<int:id>")

class fetchUser(Resource):
    def get(self,user_id):
        sqlProc='fetchUser'
        sqlArgs = [id,]
        rows,count = db_access(sqlProc,sqlArgs)
        if count !=1:
            return make_response(jsonify({"response": "User Not Found"}), 404)
        return make_response(jsonify({"response": rows[0]}), 200)
api.add_resource(fetchUser, "/fetchUser/<int:user_id>")

class login(Resource):
    pass

class fetchRecentLogins(Resource):
    pass

class details(Resource):
    pass

#endregion

#region Application Management
#endregion

class Profile(Resource):
    def get(self):
        #sqlProc = ''
        #sqlArgs = []
        #result = db_access(sqlProc,sqlArgs)
        result="You are at your profile"
        return make_response(jsonify({"profile": result}), 200)
api.add_resource(Profile, "/")

if __name__ == "__main__":
   app.run(host=DB_CONFIG.APP_HOST, port=DB_CONFIG.APP_PORT, debug=True)
