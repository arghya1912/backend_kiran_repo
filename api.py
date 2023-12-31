from flask import Flask, request, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote
from flask_cors import CORS
from datetime import datetime
import sqlite3
import pytz
import string
import re
import random
import smtplib
app = Flask(__name__)
api = Api(app)


# *database configuration ->

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('instance/sqlite.db')
    except sqlite3.error as e:
        print(e)
    return conn


# *defining the tables ->

class login_table(db.Model):
    user_id = db.Column(db.String(200), primary_key=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)


class car_details_table(db.Model):
    agreement_no = db.Column(db.String(500), primary_key=True)
    branch = db.Column(db.String(250), nullable=False)
    customer_name = db.Column(db.String(500), nullable=False)
    bkt_grp = db.Column(db.String(200), nullable=False)
    make = db.Column(db.String(700), nullable=False)
    registration_no = db.Column(db.String(200), nullable=False)
    chasis_no = db.Column(db.String(200), nullable=False)
    engine_no = db.Column(db.String(200), nullable=False)


class search_history(db.Model):
    argument = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), primary_key=True)

app.app_context().push()


##############################################################################################################
# *GET, POST, SEARCH for the login table ->

task_post_args1 = reqparse.RequestParser()
task_post_args1.add_argument('user_id', type = str, help="User_ID is Required", required = True)
task_post_args1.add_argument('password', type = str, help = "Password is Required", required = True)



resource_fields1 = {
    'user_id': fields.String,
    'password': fields.String,
}   

class login_table_post(Resource):
    @marshal_with(resource_fields1)
    def post(self):
        args = task_post_args1.parse_args()
        obj = login_table(
            user_id=args['user_id'],
            password=args['password']
        )
        db.session.add(obj)
        db.session.commit()
        return obj, 200 


class login_table_get(Resource):
    def get(self):
        tasks = login_table.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"user_id": task.user_id, "password": task.password}
        return todos
    

class login_table_search(Resource):
    def get(self, user_id, password):
        tasks = login_table.query.filter_by(user_id = user_id).first()
        #<email?password>
        if tasks is not None:
            if tasks.password == password:
                return {"user_id": True, "password": True}
            else:
                return {"user_id": True, "password": False}
        else:
            return {"user_id": False, "password": False}
        
###############################################################################################################

#* GET, POST, SEARCH for the car_details_table ->

task_post_args2 = reqparse.RequestParser()
task_post_args2.add_argument('agreement_no', type = str, help="Agreement_no is Required", required = True)
task_post_args2.add_argument('branch', type = str, help = "Branch is Required", required = True)
task_post_args2.add_argument('customer_name', type = str, help = "Customer Name is Required", required = True)
task_post_args2.add_argument('bkt_grp', type = str, help = "Bkt_Grp is Required", required = True)
task_post_args2.add_argument('make', type = str, help = "Make is Required", required = True)
task_post_args2.add_argument('registration_no', type = str, help = "Registration Number is Required", required = True)
task_post_args2.add_argument('chasis_no', type = str, help = "Chasis Number is Required", required = True)
task_post_args2.add_argument('engine_no', type = str, help = "Engine Number is Required", required = True)


resource_fields2 = {
    'agreement_no': fields.String,
    'branch': fields.String,
    'customer_name': fields.String,
    'bkt_grp': fields.String,
    'make': fields.String,
    'registration_no': fields.String,
    'chasis_no': fields.String,
    'engine_no': fields.String,
}

class car_details_table_post(Resource):
    @marshal_with(resource_fields2)
    def post(self):
        args = task_post_args2.parse_args()
        obj = car_details_table(
            agreement_no=args['agreement_no'],
            branch=args['branch'],
            customer_name=args['customer_name'],
            bkt_grp=args['bkt_grp'],
            make=args['make'],
            registration_no=args['registration_no'],
            chasis_no=args['chasis_no'],
            engine_no=args['engine_no']
        )
        db.session.add(obj)
        db.session.commit()
        return obj, 200 


class car_details_table_get(Resource):
    def get(self):
        tasks = car_details_table.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {
                "agreement_no": task.agreement_no, 
                "branch": task.branch,
                "customer_name": task.customer_name,
                "bkt_grp": task.bkt_grp,
                "make": task.make,
                "registration_no": task.registration_no,
                "chasis_no": task.chasis_no,
                "engine_no": task.engine_no,
                }
        return todos


@app.route('/registration_no/<reg_no>', methods=['GET'])
def fetch_reg_no(reg_no):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM car_details_table WHERE registration_no LIKE ?",
              ('%' + reg_no[-4:],))
    result = c.fetchall()
    answer = []

    for row in result:
        answer.append({
            'agreement_no': row[0],
            'branch': row[1],
            'customer_name': row[2],
            'bkt_grp': row[3],
            'make': row[4],
            'registration_no': row[5],
            'chasis_no': row[6],
            'engine_no': row[7]
        })

    if answer:
        return answer
    else:
        return []




@app.route('/chasis_no/<chasis_no>', methods=['GET'])
def fetch_chasis_no(chasis_no):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM car_details_table WHERE chasis_no=(?)", (chasis_no,))
    result = c.fetchall()
    answer = []

    for row in result:
        answer.append({
            'agreement_no': row[0],
            'branch': row[1],
            'customer_name': row[2],
            'bkt_grp': row[3],
            'make': row[4],
            'registration_no': row[5],
            'chasis_no': row[6],
            'engine_no': row[7]
        })

    if answer:
        return answer
    else:
        return []
    


@app.route('/engine_no/<engine_no>', methods=['GET'])
def fetch_engine_no(engine_no):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM car_details_table WHERE engine_no=(?)", (engine_no,))
    result = c.fetchall()
    answer = []

    for row in result:
        answer.append({
            'agreement_no': row[0],
            'branch': row[1],
            'customer_name': row[2],
            'bkt_grp': row[3],
            'make': row[4],
            'registration_no': row[5],
            'chasis_no': row[6],
            'engine_no': row[7]
        })

    if answer:
        return answer
    else:
        return []




# * for search_history table ->
    
task_post_args3 = reqparse.RequestParser()
task_post_args3.add_argument('argument', type = str, help="Argument is Required", required = True)
task_post_args3.add_argument('user_id', type = str, help = "User_id is Required", required = True)
task_post_args3.add_argument('created_at', type = str, help = "Date is Required")


resource_fields3 = {
    'argument': fields.String,
    'user_id': fields.String,
    'created_at': fields.DateTime
}   

class search_history_post(Resource):
    @marshal_with(resource_fields3)
    def post(self):
        args = task_post_args3.parse_args()
        obj = search_history(
            argument=args['argument'],
            user_id=args['user_id'],
            created_at=args['created_at']
        )
        db.session.add(obj)
        db.session.commit()
        return obj, 200

@app.route('/search_history/<args>', methods=['GET'])
def fetch_search_history(args):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, created_at FROM search_history WHERE argument=(?)", (args,))
    result = c.fetchall()

    answer = []

    for row in result:
        answer.append({
            'user_id': row[0],
            'created_at': row[1]
        })

    if answer:
        return answer
    else:
        return []
#############################################################################################################




api.add_resource(login_table_post, '/login_post')
api.add_resource(login_table_get, '/login_get')
api.add_resource(login_table_search, '/check_login/<user_id>/<password>')

api.add_resource(car_details_table_post, '/car_details_post')
api.add_resource(car_details_table_get, '/car_details_get')

api.add_resource(search_history_post, '/search_history_post')
##############################################################################################################


db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

CORS(app, resources={r"/*": {"origins": "*"}})

