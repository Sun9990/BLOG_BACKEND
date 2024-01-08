from pickle import TRUE
from flask import Flask
from pymongo import MongoClient
from flask_cors import CORS
from bson.json_util import dumps
from flask import Response, request
from bson import ObjectId
import datetime as dt

app = Flask(__name__)
CORS_ALLOW_ORIGIN = "*,*"
CORS_EXPOSE_HEADERS = "*,*"
CORS_ALLOW_HEADERS = "content-type,*"
CORS(app, origins=CORS_ALLOW_ORIGIN.split(","), allow_headers=CORS_ALLOW_HEADERS.split(
    ","), expose_headers=CORS_EXPOSE_HEADERS.split(","), supports_credentials=True)

def connect_db():
    client = MongoClient('mongodb://localhost:27017')
    db = client['Users']
    blog = db['blog']
    return blog

@app.route('/get_blog', methods=['GET'])
def get_blog():
    data = fetch_data()
    print(data)
    json_obj = dumps(data,indent = 2)
    print(json_obj)
    return json_obj
def fetch_data():
    blog = connect_db()
    data = blog.aggregate([
        {
           "$project" :{"_id":1,"title":1,"desc":1,"current_time":1,"updated_time":1}
        }
    ])
    return data

@app.route('/get_blog_details/<id>', methods=['GET'])
def get_blog_details(id):
    data = fetch_blog_details(id)
    print(data)
    json_obj = dumps(data, indent=2)
    print(json_obj)
    return json_obj
def fetch_blog_details(id):
    blog = connect_db()
    data = blog.aggregate([
        {
            "$match" :{ "_id": ObjectId(id)}
        },
        {
            "$project": {"_id":1,"title":1,"desc":1,"current_time":1,"updated_time":1}
        }
    ])
    return data

@app.route('/add_blog', methods = ['POST'])
def add_blog():
    params = request.get_json()
    title = params['title']
    desc = params['desc']
    current_time_original = dt.datetime.now()
    current_time = current_time_original.strftime("%d/%m/%Y, %H:%M:%S")
    updated_time_original =  dt.datetime.now()
    updated_time = updated_time_original.strftime("%d/%m/%Y, %H:%M:%S")
    blog = connect_db()
    blog.insert_one({"title": title,"desc": desc,"current_time": current_time,"updated_time": updated_time})
    return Response(
        response = dumps({
            "data" : [{"title": title,
                      "desc": desc,
                      "current_time": current_time,
                      "updated_time": updated_time
                    }],
            "message" : "Data inserted successfully"
                }),
            status= 200,
            mimetype = "application/json"
    )

@app.route('/delete_blog/<id>', methods = ['DELETE'])
def delete_blog(id):
    blog = connect_db()
    blog.delete_one({'_id': ObjectId(id)})
    return Response(
        response = dumps({
            "message" : "Data deleted successfully"
        }),
        status = 200,
        mimetype = "application/json"
    )

@app.route('/update_blog/<string:id>', methods = ['PUT'])
def update_blog(id):
    params = request.get_json()
    # title = params['title']
    # desc = params['desc']
    data = params['data']
    print(data)
    updated_time_original = dt.datetime.now()
    updated_time = updated_time_original.strftime("%d/%m/%Y, %H:%M:%S")
    blog = connect_db()
    blog.update_one(filter={"_id":ObjectId(id)}, 
                    update={"$set":{"title":data['title'], "desc":data['desc'], "updated_time": updated_time}}        
                    )
    return Response(
       response = dumps({
           "message" : "Data updated successfully"
       }),
       status = 200,
       mimetype = "application/json"
   ) 

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')