from mongoengine import *
from views import db

class post(db.Document):
	header=StringField(max_length=50,required=True)
	description=StringField(max_length=100,required=True)
	img_path=StringField(required=True)
