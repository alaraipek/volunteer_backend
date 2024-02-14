import json, jwt,re
from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from auth_middleware import token_required

from model.users import Event

event_api = Blueprint('event_api', __name__,
                   url_prefix='/api/events')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(event_api)

class EventAPI:        
    class _CRUD(Resource):  # Event API operation for Create, Read.
        @token_required
        def post(self, current_user): # Create method
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate title
            title = body.get('title')
            if title is None or len(title) < 2:
                return {'message': f'Title is missing, or is less than 2 characters'}, 400
            description = body.get('description')
            if description is None or len(description) < 2:
                return {'message': f'Description is missing, or is less than 2 characters'}, 400
            address = body.get('address')
            if address is None or len(address) < 2:
                return {'message': f'Address is missing, or is less than 2 characters'}, 400
            agegroup = body.get('agegroup')
            if agegroup is None or len(agegroup) < 2:
                return {'message': f'Age Group is missing, or is less than 2 characters'}, 400
            
            # validate zip code
            zipcode = body.get('zipcode')
            if zipcode is None or bool(re.match(r'^\d{5}$', zipcode)) == False :
                return {'message': f'Zip code is missing, or invalid. Zip code must be 5 digits'}, 400
            # look for event date
            date = body.get('date')
            if date is not None:
                try:
                    eventdate = datetime.strptime(date, '%Y-%m-%d').date()
                except:
                    return {'message': f'Event Date format error {date}, must be yyyy-mm-dd'}, 400
                if eventdate <= datetime.now().date():
                    return {'message': f'Event Date cannot be in the past'}, 400
            else:
                return {'message': f'Event Date is missing'}, 400
                

            ''' #1: Key code block, setup Event OBJECT '''
            event = Event(title=title,description=description,address=address, zipcode=zipcode, date=eventdate, agegroup=agegroup)

            # create event in database
            event = event.create()
            # success returns json of event
            if event:
                return jsonify(event.read())
            # failure returns error
            return {'message': f'Error creating {title}'}, 400

        
        def get(self): # Read Method
            events = Event.query.all()    # read/extract all events from database
            json_ready = [event.read() for event in events]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps


        def put(self):
            body = request.get_json() # get the body of the request
            id = body.get('id') # get the UID (Know what to reference)
            data = body.get('data')
            event = Event.query.get(id) # get the player (using the uid in this case)
            event.update(data)
            return f"{event.read()} Updated"
        
        @token_required
        def delete(self, current_user):
            body = request.get_json()
            id = body.get('id')
            event = Event.query.get(id)
            event.delete()
            return f"{event.read()} Has been deleted"
    
    
    class _FILTER(Resource):
        def get(self):
            # Construct a dynamic WHERE clause based on user input
            filters = {}
            title_filter = request.args.get('title')
            if title_filter:
                filters['title'] = title_filter
            description_filter = request.args.get('description')
            if description_filter:
                filters['description'] = description_filter
            address_filter = request.args.get('address')
            if address_filter:
                filters['address'] = address_filter
            zipcode_filter = request.args.get('zipcode')
            if zipcode_filter:
                filters['zipcode'] = int(zipcode_filter)

            # Build the query dynamically
            query = Event.query.filter(Event.userID.is_(None))
            
            for field, value in filters.items():
                if field == 'zipcode':
                    query = query.filter(Event.zipcode == value)
                else:
                    query = query.filter(getattr(Event, field).like(f'%{value}%'))

            # Execute the query
            results = query.all()

            json_ready = [event.read() for event in results]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps              

    class _GETBYID(Resource):
        def get(self, id):
            events = Event.query.filter(Event.userID.is_(id)).all()    # read/extract all events from database
            json_ready = [event.read() for event in events]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps


    # building RESTapi endpoint
    api.add_resource(_CRUD, '/')
    api.add_resource(_FILTER, '/query')
    api.add_resource(_GETBYID, '/get_by_id/<int:id>')
    


    