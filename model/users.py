""" database dependencies to support sqliteDB examples """
import datetime
from random import randrange
from datetime import date, datetime
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

# Define the Event class to manage actions in 'events' table,  with a relationship to 'users' table
class Event(db.Model):
    __tablename__ = 'events'

    # Define the Events schema
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=False, nullable=False)
    description = db.Column(db.String, unique=False)
    address = db.Column(db.String, unique=False)
    zipcode = db.Column(db.Integer, unique=False)
    date = db.Column(db.Date, unique=False)
    agegroup = db.Column(db.String, unique=False)

    # Define a relationship in Schema to userID, many-to-one (many events to one user)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Constructor of a Events object, initializes of instance variables within object
    def __init__(self, title, description, address, zipcode, date, agegroup):
        self.title = title
        self.description = description
        self.address = address
        self.zipcode = zipcode
        self.date = date
        self.agegroup = agegroup

    # Returns a string representation of the Events object, similar to java toString()
    # returns string
    def __repr__(self):
        return "Events(" + str(self.id) + "," + self.title + "," + str(self.userID) + ")"

    # CRUD create, adds a new record to the Events table
    # returns the object added or None in case of an error
    def create(self):
        try:
            # creates a Events object from Events(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Events table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read, returns dictionary representation of Events object
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "userID": self.userID,
            "title": self.title,
            "description": self.description,
            "address": self.address,
            "zipcode": self.zipcode,
            "date": self.date,
            "agegroup": self.agegroup
            #"base64": str(file_encode)   
        }
    
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, dictionary):
        """only updates values with length"""
        for key in dictionary:
            if key == "userID":
                self.userID = dictionary[key]
            if key == "title":
                self.title = dictionary[key]
            if key == "address":
                self.address = dictionary[key]
            if key == "description":
                self.description = dictionary[key]
            if key == "zipcode":
                self.zipcode = dictionary[key]
            if key == "date":
                self.date = datetime.strptime(dictionary[key],'%Y-%m-%d').date()
        db.session.commit()
        return self
    
    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


# Define the User class to manage actions in the 'users' table
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) User represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL
class User(db.Model):
    __tablename__ = 'users'  # table name is plural, class name is singular

    # Define the User schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _dob = db.Column(db.Date)
    _role = db.Column(db.String(20),unique=False, nullable=True)
    
    # Defines a relationship between User record and Events table, one-to-many (one user to many Events)
    events = db.relationship("Event", cascade='all, delete', backref='users', lazy=True)

    # constructor of a User object, initializes the instance variables within object (self)
    def __init__(self, name, uid, password="123qwerty", dob=date.today(),role='User'):
        self._name = name    # variables with self prefix become part of the object, 
        self._uid = uid
        self.set_password(password)
        self._dob = dob
        self._role = role

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name
    
    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid
    
    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # a getter method, extracts email from object
    @property
    def role(self):
        return self._role
        
    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid
    
    @property
    def password(self):
        return self._password[0:10] + "..." # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result
    
    # dob property is returned as string, to avoid unfriendly outcomes
    @property
    def dob(self):
        dob_string = self._dob.strftime('%m-%d-%Y')
        return dob_string
    
    # dob should be have verification for type date
    @dob.setter
    def dob(self, dob):
        self._dob = dob
    
    @property
    def age(self):
        today = date.today()
        return today.year - self._dob.year - ((today.month, today.day) < (self._dob.month, self._dob.day))
    
    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "dob": self.dob,
            "age": self.age,
            "events": [event.read() for event in self.events]
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, dictionary):
        """only updates values with length"""
        for key in dictionary:
            if key == "name":
                self.name = dictionary[key]
            if key == "uid":
                self.uid = dictionary[key]
            if key == "password":
                self.set_password(dictionary[key])
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


"""Database Creation and Testing """


# Builds working data for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        u1 = User(name='Thomas Edison', uid='toby', password='123toby', dob=date(1847, 2, 11))
        u2 = User(name='Nicholas Tesla', uid='niko', password='123niko', dob=date(1856, 7, 10))
        u3 = User(name='Alexander Graham Bell', uid='lex')
        u4 = User(name='Grace Hopper', uid='hop', password='123hop', dob=date(1906, 12, 9))
        u5 = User(name='Abe Lincoln2', uid='abe2', password='123abe', dob=date(1906, 12, 9))
        # Add admin as u5 to make it different than user
        u6 = User(name='Admin', uid='admin', password='123admin', dob=date(1906, 12, 9),role='Admin') 
    
        users = [u1, u2, u3, u4,u5,u6]
        

        # Create a Python array with JSON values
        json_array = [
        '{"title": "FoodBank", "description": "Food Bank", "address": "123 food bank st", "zipcode":"92126", "day":20,"agegroup":"16"}',
        '{"title": "AnimalShelter", "description": "Animal Shelter", "address": "123 Animal shelter st", "zipcode":"92127", "day":21,"agegroup":"18"}',
        '{"title": "CommunityService", "description": "Community Service", "address": "123 community service st", "zipcode":"92128", "day":22,"agegroup":"10"}',
        '{"title": "BeachCleanup", "description": "Beach Cleanup", "address": "123 beach cleanup st", "zipcode":"92129", "day":23,"agegroup":"6"}',
        ]
        events_array = [json.loads(json_str) for json_str in json_array]
        num = 0

        """Builds sample user/note(s) data"""
        for user in users:
            num = num + 1
            try:
                '''add a few 1 to 4 events per user'''
                for events in events_array:
                    title = events["title"]+ str(num)
                    description = events["description"]
                    address = events["address"]
                    zipcode = events["zipcode"]
                    day = events["day"]
                    agegroup = events["agegroup"]
                    user.events.append(Event(title=title, description=description, address=address, zipcode=zipcode, date=date(2024,2,day), agegroup=agegroup ))
                '''add user/event data to table'''
                user.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")
            