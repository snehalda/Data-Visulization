from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from pandas.io.json import json_normalize
import pandas as pd


app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'yelp'
COLLECTION_NAME = 'business'
FIELDS = {'business_id': True, 'name': True, 'state': True, 'is_open': True, 'categories': True, '_id': False}
star_FIELDS = { 'stars': 1, '_id': 0}

class JSONObject:
  def __init__( self, dict ):
      vars(self).update( dict )

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/donorschoose/projects")
def donorschoose_projects():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS, limit=100000)
    #df = json_normalize(json.loads(dumps(projects)))
    #print(df)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

@app.route("/yelp/reviewBid/<bid>")
def getReviews(bid):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME]["review"]
    reviews = collection.find({"business_id": bid})
    json_reviews = []
    for review in reviews:
        json_reviews.append(review)
    json_reviews = json.dumps(json_reviews, default=json_util.default)
    connection.close()
    return json_reviews

@app.route("/yelp/restBid/<bid>")
def getRests(bid):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME]["business"]
    reviews = collection.find({"business_id": bid})
    json_business = []
    for review in reviews:
        json_business.append(review)
    json_business = json.dumps(json_business, default=json_util.default)
    connection.close()
    return json_business

@app.route("/yelp/rest/<bid>")
def getBid(bid):
    return render_template("plot1.html", bid=bid)

@app.route("/yelp/reviews/<bid>")
def getReviewsByBid(bid):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME]["review"]
    reviews = collection.find({"business_id":bid},star_FIELDS)

    #print(json_normalize(dumps(reviews)))
   # df = json_normalize(json.loads(dumps(reviews)))
   # print(df)
    #projects = collection.find(projection=FIELDS)
    json_reviews = []
    #count = len(reviews)
    star=0
    cnt=0
    result=0.0
    for review in reviews:
        #jsonobject = json.dumps(review)
        rev=json.loads(str(review).replace("\'", "\""))
        #print(json_normalize(rev))
        star = star+int(rev["stars"])
        cnt=cnt+1
    if cnt!=0:
        result=star/cnt
        #print(result)
    #json_reviews = json.dumps(json_reviews, default=json_util.default)
    connection.close()
    return str(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)