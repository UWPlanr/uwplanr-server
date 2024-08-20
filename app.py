from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from pymongo import ReturnDocument
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from constants import COLLECTIONS, FACULTY_TO_COLLECTION, FACULTIES
import certifi
import os

load_dotenv()

app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app, tlsCAFile=certifi.where())

# Checks the connection to MongoDB
@app.route("/check_mongodb")
def check_mongodb():
    try:
        collection = mongo.db.your_collection_name
        document = collection.find_one()
        if document:
            return jsonify({ "message": "MongoDB connected successfully" })
        else:
            return jsonify({ "message": "MongoDB is not connected or collection is empty" })
    except Exception as error:
        return jsonify({ "error": str(error) })

# Inserts a course
@app.route("/insert_data", methods=["POST"])
def insert_data():
    try:
        data = request.get_json()
        if data["faculty"] in FACULTIES:
            mongo.db[FACULTY_TO_COLLECTION[data["faculty"]]].insert_one(data)
        else:
            return jsonify({ "error": "invalid json, faculty not found" })
        return jsonify({ "message": "Data inserted successfully" })
    except Exception as error:
        return jsonify({ "error": str(error) })

# Finalizes a course to be used on the frontend
@app.route("/finalize_course", methods=["PATCH"])
def finalize_course():
    try:
        data = request.get_json()
        updated_data = {
            "prereqs": data["prereqs"],
            "coreqs": data["coreqs"],
            "antireqs": data["antireqs"],
            "termsOffered": data["termsOffered"],
            "minLevel": data["minLevel"],
            "finalized": True,
        }
        course = mongo.db[FACULTY_TO_COLLECTION[data["faculty"]]].find_one_and_update({ "code": data["code"] }, { "$set": updated_data }, projection={"_id": False}, return_document=ReturnDocument.AFTER)
        return jsonify({"course": course}), 200
    except Exception as error:
        return jsonify({ "error": str(error) }), 500

# Returns all courses from a single faculty
@app.route("/grab_courses_faculty/<faculty>", methods=["GET"])
def grab_courses_faculty(faculty):
    try:
        courses = list(mongo.db[faculty].find({}))
        return jsonify({ "courses": courses })
    except Exception as error:
        return jsonify({ "error": str(error) }), 500

# Returns a the first document from the first faculty collection with a non_finalized document
@app.route("/grab_random_course", methods=["GET"])
def grab_random_course():
    try:
        for faculty in FACULTIES:
            course = mongo.db[FACULTY_TO_COLLECTION[faculty]].find_one({ "finalized": False }, projection={"_id": False})
            if course:
                return jsonify({ "course": course })
            else:
                continue
        return jsonify({ "course": {} })
    except Exception as error:
        return jsonify({ "error": str(error) }), 500
    
@app.route("/grab_course/<faculty>/<code>", methods=["GET"])
def grab_course(faculty, code):
    try:
        course = mongo.db[FACULTY_TO_COLLECTION[faculty]].find_one({ "code": code }, projection={"_id": False})
        if course:
            return jsonify({ "course": course })
        else:
            return jsonify({ "course": {} })
    except Exception as error:
        return jsonify({ "error": str(error) }), 500

# Returns all courses from all faculties
@app.route("/grab_all_courses", methods=["GET"])
def grab_all_courses():
    try:
        courses = []
        for collection in COLLECTIONS:
            faculty_courses = list(mongo.db[collection].find({}, projection={"_id": False}))
            courses = courses + faculty_courses
        return jsonify({ "courses": courses })
    except Exception as error:
        return jsonify({ "error": str(error) }), 500
    
# Returns number of finalized courses
@app.route("/finalized_courses_count", methods=["GET"])
def finalized_courses_count():
    try:
        total = 0
        for collection in COLLECTIONS:
            count = mongo.db[collection].count_documents({ "finalized": True })
            total += count
        return jsonify({ "finalized": total })
    except Exception as error:
        return jsonify({ "error": str(error) }), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)