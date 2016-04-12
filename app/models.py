from app import db
from flask.ext.login import LoginManager, UserMixin
from datetime import datetime

# Key_page = db.Table('Key_page',
#     db.Column('tag_id', db.Integer, db.ForeignKey('key.id')),
#     db.Column('page_id', db.Integer, db.ForeignKey('document.id'))
# )

class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128), index=True, unique=True)
	author = db.Column(db.String(64))
	doctype = db.Column(db.String(5))
	size = db.Column(db.Integer)
	downloads = db.Column(db.Integer)
	path = db.Column(db.String(256), unique=True)
	filename = db.Column(db.String(256), unique=True)
	upload_on = db.Column(db.DateTime, default=datetime.now())
	#tags = db.relationship('Key', backref='documents', lazy='dynamic')
	
	@property
  	def serialize(self):
  		return {'doc_id' : self.id, 'doc_title' : self.title, 'doc_type' : self.doctype, 'doc_size' : self.size, 'doc_downloads' : self.downloads, 'doc_path' : self.path, 'doc_uploaded' : self.upload_on}

  	def __repr__(self):
  		return '<Document ('%r')>' % (self.title)
        
class Key(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(10), unique=True)

	@property
  	def serialize(self):
  		return {'key_id' : self.id, 'key' : self.key}

  	def __repr__(self):
  		return "<Key ('%r')>" % (self.key)

class KeyTagDoc(db.Model):
	 __tablename__ = 'KeyTagDoc'
	 id = db.Column(db.Integer, primary_key=True)
	 key_id = db.Column(db.Integer, db.ForeignKey('key.id'))
	 doc_id = db.Column(db.Integer, db.ForeignKey('document.id'))

	 def __init__(self, key_id, doc_id):
	 	self.key_id = key_id
	 	self.doc_id = doc_id

	 @property
	 def serialize(self):
	 	return {'key_id' : self.key_id, 'doc_id' : self.doc_id}

# class KeyTagDoc(object) :
# 	pass
# class Doument(object) :
# 	pass

# class Key(object):
#     pass
        		        
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
	
