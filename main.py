from flask import Flask, request, jsonify, Response, redirect, url_for
from flask_restx import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import base64
from base64 import b64encode
# Importing Python functools module which contains the reduce() function
import functools
from flask_mail import Mail, Message
from flask import Flask, after_this_request, make_response, jsonify, render_template, send_file,session 
import subprocess

# Importing Python module which contains the add() function
import operator

# from YOLO_Video import frame_detect

app = Flask(__name__) # Instantiation of Flask object.
app.config.SWAGGER_UI_OAUTH_APP_NAME = 'tol'
api = Api(app,title=app.config.SWAGGER_UI_OAUTH_APP_NAME)        # Instantiation of Flask-RESTX object.

############################
##### BEGIN: Database #####
##########################
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1:3306/uastol2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'dannn'
app.config['MAIL_SERVER']= 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'danangjananf@gmail.com'
app.config['MAIL_PASSWORD'] = 'ihlzoorhvykswksd'
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = SQLAlchemy(app) # Instantiation of Flask-SQLAlchemy object.

class User(db.Model):
    id       = db.Column(db.Integer(), primary_key=True, nullable=False)
    email    = db.Column(db.String(32), unique=True, nullable=False)
    name     = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
##########################
##### END: Database #####
########################

###########################
##### BEGIN: Sign Up #####
#########################
parser4Reg = reqparse.RequestParser()
parser4Reg.add_argument('email', type=str, help='Email', location='json', required=True)
parser4Reg.add_argument('name', type=str, help='Name', location='json', required=True)
parser4Reg.add_argument('password', type=str, help='Password', location='json', required=True)
parser4Reg.add_argument('re_password', type=str, help='Retype Password', location='json', required=True)

@api.route('/signup')
class Registration(Resource):
    @api.expect(parser4Reg)
    def post(self):
        # BEGIN: Get request parameters.
        args        = parser4Reg.parse_args()
        email       = args['email']
        name        = args['name']
        password    = args['password']
        rePassword  = args['re_password']
        # END: Get request parameters.

        # BEGIN: Check re_password.
        if password != rePassword:
            return {
                'messege': 'Password must be the same!'
            }, 400
        # END: Check re_password.

        # BEGIN: Check email existance.
        user = db.session.execute(db.select(User).filter_by(email=email)).first()
        if user:
            return "This email address has been used!"
        # END: Check email existance.

        # BEGIN: Insert new user.
        user          = User() # Instantiate User object.
        user.email    = email
        user.name     = name
        user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()
        # END: Insert new user.

        return {'messege': 'Successful!'}, 201

#########################
##### END: Sign Up #####
#######################

###########################
##### BEGIN: Sign In #####
#########################
SECRET_KEY      = "WhatEverYouWant"
ISSUER          = "myFlaskWebservice"
AUDIENCE_MOBILE = "myMobileApp"

parser4LogIn = reqparse.RequestParser()
parser4LogIn.add_argument('email', type=str, help='Email', location='json', required=True)
parser4LogIn.add_argument('password', type=str, help='Password', location='json', required=True)

@api.route('/signin')
class LogIn(Resource):
    @api.expect(parser4LogIn)
    def post(self):
        # BEGIN: Get request parameters.
        args        = parser4LogIn.parse_args()
        email       = args['email']
        password    = args['password']
        # END: Get request parameters.

        if not email or not password:
            return {
                'message': 'Please fill your email and password!'
            }, 400

        # BEGIN: Check email existance.
        user = db.session.execute(
            db.select(User).filter_by(email=email)).first()

        if not user:
            return {
                'message': 'The email or password is wrong!'
            }, 400
        else:
            user = user[0] # Unpack the array.
        # END: Check email existance.

        # BEGIN: Check password hash.
        if check_password_hash(user.password, password):
            payload = {
                'user_id': user.id,
                'email': user.email,
                'aud': AUDIENCE_MOBILE, # AUDIENCE_WEB
                'iss': ISSUER,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours = 2)
            }
            tup = email,":",password
            #toString
            data = functools.reduce(operator.add, tup)
            byte_msg = data.encode('ascii')
            base64_val = base64.b64encode(byte_msg)
            code = base64_val.decode('ascii')
            token = jwt.encode(payload, SECRET_KEY)
            msg_title = "TOKEN MASUK APLIKASI KAMU!"
            msg = Message(msg_title, sender = 'cheatdetec@gmail.com', recipients = [email])
            msg.body = token
            mail.send(msg)
            return {
                'title': 'Code Terkirim ke Email',
                'token': token,
                'code' : code
            }, 200
        else:
            return {
                'message': 'Wrong email or password!'
            }, 400
        # END: Check password hash.

#########################
##### END: Sign In #####
#######################

#############################
##### BEGIN: Basic Auth ####
###########################
import base64
parser4Basic = reqparse.RequestParser()
parser4Basic.add_argument('Authorization', type=str,
    location='headers', required=True, 
    help='Please, read https://swagger.io/docs/specification/authentication/basic-authentication/')

@api.route('/basic-auth')
class BasicAuth(Resource):
    @api.expect(parser4Basic)
    def post(self):
        args        = parser4Basic.parse_args()
        basicAuth   = args['Authorization']
        # basicAuth is "Basic bWlyemEuYWxpbS5tQGdtYWlsLmNvbTp0aGlzSXNNeVBhc3N3b3Jk"
        base64Str   = basicAuth[6:] # Remove first-6 digits (remove "Basic ")
        # base64Str is "bWlyemEuYWxpbS5tQGdtYWlsLmNvbTp0aGlzSXNNeVBhc3N3b3Jk"
        base64Bytes = base64Str.encode('ascii')
        msgBytes    = base64.b64decode(base64Bytes)
        pair        = msgBytes.decode('ascii')
        # pair is mirza.alim.m@gmail.com:thisIsMyPassword
        email, password = pair.split(':')
        # email is mirza.alim.m@gmail.com, password is thisIsMyPassword
        return {'email': email, 'password': password}
###########################
##### END: Basic Auth ####
#########################

####################################
##### BEGIN: Bearer/Token Auth ####
##################################
parser4Bearer = reqparse.RequestParser()
parser4Bearer.add_argument('Authorization', type=str, 
    location='headers', required=True, 
    help='Please, read https://swagger.io/docs/specification/authentication/bearer-authentication/')

@api.route('/bearer-auth')
class BearerAuth(Resource):
    @api.expect(parser4Bearer)
    def post(self):
        args        = parser4Bearer.parse_args()
        bearerAuth  = args['Authorization']
        # basicAuth is "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6Im1pcnphLmFsaW0ubUBnbWFpbC5jb20iLCJhdWQiOiJteU1vYmlsZUFwcCIsImlzcyI6Im15Rmxhc2tXZWJzZXJ2aWNlIiwiaWF0IjoxNjc5NjQwOTcxLCJleHAiOjE2Nzk2NDgxNzF9.1ZxTlAT7bmkLQDgIvx0X3aWJaeUn8r6LjGDyhfrt3S8"
        jwtToken    = bearerAuth[7:] # Remove first-7 digits (remove "Bearer ")
        # jwtToken is "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6Im1pcnphLmFsaW0ubUBnbWFpbC5jb20iLCJhdWQiOiJteU1vYmlsZUFwcCIsImlzcyI6Im15Rmxhc2tXZWJzZXJ2aWNlIiwiaWF0IjoxNjc5NjQwOTcxLCJleHAiOjE2Nzk2NDgxNzF9.1ZxTlAT7bmkLQDgIvx0X3aWJaeUn8r6LjGDyhfrt3S8"
        try:
            payload = jwt.decode(
                jwtToken, 
                SECRET_KEY, 
                audience = [AUDIENCE_MOBILE], 
                issuer = ISSUER, 
                algorithms = ['HS256'], 
                options = {"require": ["aud", "iss", "iat", "exp"]}
            )
        except:
            return {
                'message' : 'Unauthorized! Token is invalid! Please, Sign in!'
            }, 401
        
        return payload, 200
    
def decodetoken(jwtToken):
    decode_result = jwt.decode(jwtToken,
				SECRET_KEY,
				audience = [AUDIENCE_MOBILE],
				issuer = ISSUER,
				algorithms = ['HS256'],
				options = {"require": ["aud", "iss", "iat", "exp"]})	
    return decode_result

parser4get = reqparse.RequestParser()
parser4get.add_argument(
    'email', type=str, help="Masukan Email Anda", location='json', required=True)
parser4get.add_argument(
    'password', type=str, help="Ubah Password Anda", location='json', required=True)

editPasswordParser =  reqparse.RequestParser()
editPasswordParser.add_argument('current_password', type=str, help='current_password',location='json', required=True)
editPasswordParser.add_argument('new_password', type=str, help='new_password',location='json', required=True)
@api.route('/edit-password')
class Password(Resource):
    @api.expect(parser4Bearer,editPasswordParser)
    def put(self):
        args = editPasswordParser.parse_args()
        argss = parser4Bearer.parse_args()
        bearerAuth  = argss['Authorization']
        cu_password = args['current_password']
        newpassword = args['new_password']
        try:
            jwtToken    = bearerAuth[7:]
            token = decodetoken(jwtToken)
            user = User.query.filter_by(id=token.get('user_id')).first()
            if check_password_hash(user.password, cu_password):
                user.password = generate_password_hash(newpassword)
                db.session.commit()
            else:
                return {'message' : 'Password Lama Salah'},400
        except:
            return {
                'message' : 'Token Tidak valid! Silahkan, Sign in!'
            }, 401
        return {'message' : 'Password Berhasil Diubah'}, 200


editParser = reqparse.RequestParser()
editParser.add_argument('email', type=str, help='email', location='json', required=True)
editParser.add_argument('name', type=str, help='name', location='json', required=True)
editParser.add_argument('Authorization', type=str, help='Authorization', location='headers', required=True)
@api.route('/edit-user')
class EditUser(Resource):
       @api.expect(editParser)
       def put(self):
        args = editParser.parse_args()
        bearerAuth  = args['Authorization']
        email = args['email']
        name = args['name']
        datenow =  datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        try:
            jwtToken    = bearerAuth[7:]
            token = decodetoken(jwtToken)
            # print(token.get)
            user = User.query.filter_by(email=token.get('email')).first()
            user.email = email
            user.name = name
            user.updatedAt = datenow
            db.session.commit()
        except:
            return {
                'message' : 'Token Tidak valid,Silahkan Login Terlebih Dahulu!'
            }, 401
        return {'message' : 'Update User Sukses'}, 200
##################################
##### END: Bearer/Token Auth ####
################################
# @app.route("/realtime")
# def hello_world():
#     return render_template('index.html')

# @app.route("/opencam", methods=['GET'])
# def opencam():
#     print("here")
#     subprocess.run(['python', 'detect.py', '--source', '0', '--weights', 'best.pt'])
#     return "done"

from flask import Flask, render_template, Response, jsonify
import torch
import cv2
from PIL import Image
import mysql.connector
import pandas as pd




def detect_objects():
    # Load the YOLOv5 model with .pt weights
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)

    counter = 0
    threshold = 30

    # Open camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Failed to open the camera")
        return

    while True:
        # Read frame from the camera
        ret, frame = cap.read()

        if ret:
            frame = cv2.flip(frame, 1)

            # Convert frame to PIL Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Perform inference on the image
            results = model(image)

            # Get detection results
            pred_boxes = results.xyxy[0]

            # Draw bounding boxes and labels on the frame
            for *xyxy, conf, cls in pred_boxes:
                x1, y1, x2, y2 = map(int, xyxy)
                label = f'{model.names[int(cls)]} {conf:.2f}'

                if model.names[int(cls)] == 'mobil':
                    counter += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # Add count overlay on the frame
            count_text = f"Count of cars: {counter}"
            cv2.putText(frame, count_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Show the frame
            cv2.imshow('Object Detection', frame)

            # Check for 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break

    # Release the camera and clean up
    cap.release()

    # Print the count of "kosong" labels
    print(f"Count of car: {counter}")

    # Close all OpenCV windows
    cv2.destroyAllWindows()


@app.route('/video_feed')
def video_feed():
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # app.run(ssl_context='adhoc', debug=True)
    # app.run(host='192.168.136.85', port=5000, debug=True)
    app.run(host='192.168.43.182', port=5000, debug=True)
    # app.run(debug=True)
    