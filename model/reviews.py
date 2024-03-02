from flask import Flask, Blueprint, request, jsonify
from flask_restful import Api, Resource
import random
import json

app = Flask(__name__)

reviews_api = Blueprint('reviews_api', __name__, url_prefix='/api/reviews')
api = Api(reviews_api)

review_data = []

def initReviews():
    global review_data
    try:
        with open("carddb.json", "r") as file:
            review_data = json.load(file)
            print("Successfully loaded JSON data:", review_data)
    except FileNotFoundError:
        review_data = []
        print("File not found.")
    except Exception as e:
        print("Error:", e)

class RandomReview(Resource):
    def get(self):
        initReviews()  # Ensure card_data is up to date
        random_review = generateRandomReview()
        return jsonify(random_review)

def generateRandomReview():
    if review_data:
        return random.choice(review_data)
    else:
        return {"error": "No review data available"}

api.add_resource(RandomReview, '/rand')

if __name__ == "__main__":
    app.register_blueprint(reviews_api)
    app.run(debug=True)
