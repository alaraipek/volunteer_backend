from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Define the Review class to manage actions in the 'reviews' table
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    review = db.Column(db.Text, nullable=False)

    def __init__(self, title, review):
        self.title = title
        self.review = review

    def __repr__(self):
        return f"Review(id={self.id}, title={self.title}, review={self.review})"


# Define the function to initialize the database with sample data
def initReviews():
    with db.session() as session:
        # Create some sample reviews
        review1 = Review(title='Product A', review='This is a great product.')
        review2 = Review(title='Service B', review='Excellent service provided.')
        review3 = Review(title='Experience C', review='Had a wonderful experience.')

        # Add reviews to the session and commit changes
        session.add(review1)
        session.add(review2)
        session.add(review3)
        session.commit()
