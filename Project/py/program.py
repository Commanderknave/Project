#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify, render_template, session, redirect, url_for
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_session import Session

from functools import wraps
import json
import requests
from datetime import datetime
import hashlib
import DB_CONFIG
from DB_UTIL import db_access

app = Flask(__name__, template_folder="../templates")
api = Api(app)
CORS(app=app)

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = DB_CONFIG.APP_HOST
app.secret_key = DB_CONFIG.SECRET_KEY
Session(app)

app.config['MAIL_SERVER']="smtp.unb.ca"
app.config['MAIL_PORT']=25
mail=Mail(app)

#region Decorators

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrapper

    def sanitize_input(input_string):
        return input_string.replace("'", "''")
#endregion

#region Functions

def get_ip():
    return request.remote_addr

#endregion





#region User Management

class Register(Resource):
    def get(self):
        return make_response(render_template('register.html'))
    def post(self):
        rejectionReason=""

        #Data
        data=request.json
        name=data['username']
        email=data['email']
        password=data['user_password']

        #Pre-DB validation
        if len(name)>30 or not name.isalnum():
            rejectionReason+="Your username is either over the character limit(30)\n"
            rejectionReason+="Or your username did not only contain alphanumerics (a-Z,0-9)\n"
        elif len(name)<4:
            rejectionReason+="Your username is under the character limit(4)\n"
        if len(password)>255 or not password.isalnum():
            rejectionReason+="Your password is either over the character limit(255)\n"
            rejectionReason+="Or your password did not only contain alphanumerics (a-Z,0-9)\n"
        elif len(password)<8:
            rejectionReason+="Your password is under the character limit(8)\n"
        if rejectionReason:
            return make_response(jsonify({"response": rejectionReason}),400)

        #Add user in user table
        sqlProc='registerUser'
        password_hash=hashlib.sha512(password.encode("UTF-8")).hexdigest()
        sqlArgs = [name,password_hash,]
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
            #Most common case is duplicate email.
            sqlProc='deleteUser'
            sqlArgs=[new_user_id,]
            db_access(sqlProc,sqlArgs)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)

        #Email User
        message=Message(
            subject="Validate your Games Wishlist account",
            sender="awesomeinc@unb.ca",
            recipients=[email]
        )
        message.body=f"To validate your account please go to https://cs3103.cs.unb.ca:8037/validate/{str(email_hash)}"
        mail.send(message)

        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(Register, '/register')

class EmailSent(Resource):
    def get(self):
        return make_response(render_template('emailSent.html'))
api.add_resource(EmailSent, "/emailSent")

class Validate(Resource):
    def get(self,email_hash):
        return make_response(render_template('validate.html'))
    def post(self,email_hash):
        sqlProc='validateUser'
        sqlArgs = [email_hash,]
        rows,count = db_access(sqlProc,sqlArgs)
        if count==0:
            return make_response(jsonify({"response": "Forbidden Access"}), 403)
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(Validate, "/validate/<string:email_hash>")

class Login(Resource):
    def get(self):
        return make_response(render_template('login.html'))
    def post(self):
        rejectionReason=""

        #Data
        data=request.json
        username=data['username']
        password=data['user_password']
        password_hash=hashlib.sha512(password.encode("UTF-8")).hexdigest()

        #Check if a user with the name exists
        sqlProc='fetchUserByName'
        sqlArgs=[username,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            rejectionReason+="No such user with that username"
            return make_response(
                jsonify({"response": "User Not Found", "reason": rejectionReason}), 404)

        #Check for existing user
        sqlProc='loginUser'
        sqlArgs=[username,password_hash]
        try:
            rows,count=db_access(sqlProc, sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        #No such user
        if count !=1:
            rejectionReason+="Credentials may be invalid or this user is not yet validated"
            return make_response(
                jsonify({"response": "User Not Found", "reason": rejectionReason}), 404)

        #There is a user and they're validated
        user=rows[0]
        ip = get_ip()
        print(ip)
        session['user_id'] = user['user_id']
        session['ip'] = ip
        return make_response(jsonify({"response": "Operation Successful", "user_id": user['user_id']}), 200)
api.add_resource(Login, "/login")

class Logout(Resource):
    @login_required
    def get(self):
        if not 'user_id' in session:
            return make_response(jsonify({"response": "User is not logged in"}), 404)
        session.pop('user_id')
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(Logout, "/logout")

class FetchUser(Resource):
    def get(self,user_id):
        sqlProc='fetchUser'
        sqlArgs=[user_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "User Not Found"}), 404)
        value=json.dumps({"response": rows[0]}, default=str, indent=4)
        return make_response(render_template("view.html", value=value))
api.add_resource(FetchUser, "/user/<int:user_id>")

class FetchUserByName(Resource):
    def get(self,username):
        sqlProc='fetchUserByName'
        sqlArgs=[username,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count==0:
            return make_response(jsonify({"response": "No Such User(s)"}), 404)
        return make_response(jsonify({"response": "Operation Successful", "users": rows}), 200)
api.add_resource(FetchUserByName, "/user/<string:username>")

class SearchUser(Resource):
    def get(self):
        return make_response(render_template('searchUser.html'))
api.add_resource(SearchUser, "/user/search")

class ForgotPassword(Resource):
    def get(self):
        return make_response(render_template('forgotPassword.html'))
    def post(self):
        #Get Current user's email
        user_id=session.get('user_id')
        print(user_id)
        sqlProc='getUserEmail'
        sqlArgs=[user_id, ]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "User Not Found"}), 404)

        #Email User
        email=rows[0]['email']
        email_hash=hashlib.sha512(email.encode("UTF-8")).hexdigest()
        message=Message(
            subject="Validate your Games Wishlist account",
            sender="awesomeinc@unb.ca",
            recipients=[email]
        )
        message.body=f"To validate your account please go to https://cs3103.cs.unb.ca:8037/newPassword/{str(email_hash)}"
        mail.send(message)

        #Invalidate account
        sqlProc='invalidateUser'
        sqlArgs=[user_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        
        sqlProc='preValidateUser'
        sqlArgs=[user_id,email,email_hash]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(ForgotPassword, "/user/forgotPassword")

class NewPassword(Resource):
    def get(self,email_hash):
        return make_response(render_template('newPassword.html'))
    def post(self,email_hash):
        user_id=int(session['user_id'])

        #Get New Password
        data=request.json
        newPassword=data['new_password']
        sqlProc='updatePassword'
        password_hash=hashlib.sha512(newPassword.encode("UTF-8")).hexdigest()
        sqlArgs = [user_id, password_hash]
        rows,count = db_access(sqlProc,sqlArgs)
        
        sqlProc='validateUser'
        sqlArgs = [email_hash,]
        rows,count = db_access(sqlProc,sqlArgs)
        if count==0:
            return make_response(jsonify({"response": "Forbidden Access"}), 403)
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(NewPassword, "/newPassword/<string:email_hash>")

class details(Resource):
    pass

#endregion

#region Games

class AddGame(Resource):
    @login_required
    def get(self):
        return make_response(render_template('addGame.html'))
    
    @login_required
    def post(self):
        rejectionReason=""

        #Data
        data=request.json
        steamId=data['game_id']
        response=requests.get(f'https://store.steampowered.com/api/appdetails?appids={steamId}', timeout=10)

        #Do not fucking ask stu
        steam_data=response.json()[steamId]['data']

        #Game details parsing because CORS is a pain in my fucking ass
        game_url='https://store.steampowered.com/app/'+str(steamId)
        steamId=steamId
        game_name=steam_data['name']
        developer=steam_data['developers'][0]
        publisher=steam_data['publishers'][0]
        release_date="1969-12-31"
        if not steam_data['release_date']['date']=="To be announced":
            release_date_string=steam_data['release_date']['date']
            date=datetime.strptime(release_date_string, "%d %b, %Y").strftime("%Y-%m-%d")
            release_date=date
        price=0
        if not steam_data['is_free']:
            #Ex: CDN$ 66.99-> 66.99
            price_data=steam_data.get('price_overview',"N/A")
            if not price_data=="N/A":
                price_data=steam_data['price_overview']['final_formatted']
                if not steam_data['price_overview']['initial_formatted']=="":
                    price_data=steam_data['price_overview']['initial_formatted']
            price=price_data
            #TODO add a fucking price converter.
        game_description=steam_data['short_description']
        thumbnail=steam_data['header_image']

        sqlProc='addGame'
        sqlArgs=[game_url, steamId, game_name, developer, publisher, 
                 release_date, price, game_description, thumbnail]
        try:
            rows,count=db_access(sqlProc, sqlArgs)
        except Exception as e:
            if "Database Error:(1062" in str(e):
                return make_response(jsonify({"response": "Duplicate Steam ID", "steamId": steamId}), 304)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        return make_response(jsonify({"response": "Operation Successful"}), 200)
api.add_resource(AddGame, "/game/addGame")

class WishGame(Resource):
    @login_required
    def get(self,game_id):
        user_id = session.get('user_id')

        sqlProc='fetchGame'
        sqlArgs=[game_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "Game Not Found"}), 404)

        sqlProc='fetchUserWishlist'
        sqlArgs=[int(user_id),]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)

        #User has game(s) in the wishlist
        for game in rows:
            if game['game_id']==game_id:
                return make_response(jsonify({"response": "Game Already Wished"}), 304)

        # Game is not wished
        sqlProc='wishGame'
        sqlArgs=[int(user_id),game_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        return make_response(jsonify({"response": "Operation Successful"}), 200)

    @login_required
    def delete(self,game_id):
        user_id = session.get('user_id')

        # #External user attempting to affect another
        affectedUser=request.json['user_id']
        if not int(user_id)==int(affectedUser):
            return make_response(jsonify({"response": "You cannot edit another's wishlist"}), 403)

        #Verify game exists
        sqlProc='fetchGame'
        sqlArgs=[game_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "Game Not Found"}), 404)

        #Get user's wishlist
        sqlProc='fetchUserWishlist'
        sqlArgs=[int(user_id),]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)

        #Look for the game
        for game in rows:
            #Found game
            if game['game_id']==game_id:
                #If purchased do not allow removal
                if game['purchased']==1:
                    return make_response(jsonify({"response": "Game is purchased"}), 409)

                #Unwish game from user
                sqlProc='unwishGame'
                sqlArgs=[int(user_id),game_id,]
                try:
                    rows,count=db_access(sqlProc,sqlArgs)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"response": "Internal Server Error"}), 500)
                #We could send an email notifying of someone purchasing the game for the user
                return make_response(jsonify({"response": "Operation Successful"}), 200)

        return make_response(jsonify({"response": "You somehow ran out of games to check whilst getting none removed"}), 500)
api.add_resource(WishGame, "/game/wish/<int:game_id>")

class WishList(Resource):
    def get(self,user_id):
        #Verify user exists
        sqlProc='fetchUser'
        sqlArgs=[user_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "User Not Found"}), 404)

        #Get wishlist
        sqlProc='fetchUserWishlist'
        sqlArgs=[user_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        return make_response(jsonify({"response": "Operation Successful", "wishlist": rows}) ,200)
api.add_resource(WishList, "/user/list/<int:user_id>")

class PurchaseGame(Resource):
    @login_required
    def post(self,user_id,game_id):
        #Check if user exists
        sqlProc='fetchUser'
        sqlArgs=[user_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "User Not Found"}), 404)

        #Verify game exists
        sqlProc='fetchGame'
        sqlArgs=[game_id,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count!=1:
            return make_response(jsonify({"response": "Game Not Found"}), 404)
        
        #Look for the game
        sqlProc='fetchUserWishlist'
        sqlArgs=[int(user_id),]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)

        #User has game(s) in the wishlist
        for game in rows:
            if game['game_id']==game_id:
                sqlProc='purchaseGame'
                sqlArgs=[int(user_id),game_id]
                try:
                    rows,count=db_access(sqlProc,sqlArgs)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"response": "Internal Server Error"}), 500)
                #We could send an email notifying of someone purchasing the game for the user
                return make_response(jsonify({"response": "Operation Successful"}), 200)

        #The user had no such game wished
        return make_response(jsonify({"response": "Game Was Not Wished By User"}), 404)
api.add_resource(PurchaseGame, "/game/purchase/<int:user_id>/<int:game_id>")

class SearchGameByName(Resource):
    def get(self,game_name):
        sqlProc='fetchGameByName'
        sqlArgs=[game_name,]
        try:
            rows,count=db_access(sqlProc,sqlArgs)
        except Exception as e:
            print(e)
            return make_response(jsonify({"response": "Internal Server Error"}), 500)
        if count==0:
            return make_response(jsonify({"response": "No Such Game(s)"}), 404)
        return make_response(jsonify({"response": "Operation Successful", "games": rows}), 200)
api.add_resource(SearchGameByName, "/game/<string:game_name>")

class SearchGame(Resource):
    def get(self):
        return make_response(render_template('searchGame.html'))
api.add_resource(SearchGame, "/game/search")
#endregion

#region Stuff lmao

class FetchSession(Resource):
    def get(self):
        print(session)
        if not 'user_id' in session:
            return make_response(jsonify({"response": "User is not logged in"}), 404)
        return make_response(jsonify({"response": "Operation Successful", "sessionId": session['user_id']}), 200)
api.add_resource(FetchSession,"/session")

class Support(Resource):
    def get(self):
        return make_response(render_template('support.html'))
api.add_resource(Support, "/support")

class Home(Resource):
    def get(self):
        return make_response(render_template('root.html'))
api.add_resource(Home, "/")

#endregion

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    app.run(host=DB_CONFIG.APP_HOST, port=DB_CONFIG.APP_PORT, debug=True, ssl_context=context)
