from app import app, db, lm
from flask import Flask, redirect, url_for, render_template, request, session, flash, abort, jsonify, json, Response
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, Document, Key, KeyTagDoc
from oauth import OAuthSignIn
from flask_cloudy import Storage
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from datetime import datetime, date
from sets import Set
# ...
# Update the config 
app.config.update({
    "STORAGE_PROVIDER": "LOCAL", # Can also be S3, GOOGLE_STORAGE, etc... 
    "STORAGE_KEY": "",
    "STORAGE_SECRET": "",
    "STORAGE_CONTAINER": UPLOAD_FOLDER,  # a directory path for local, bucket name of cloud
    "STORAGE_SERVER": True,
    "STORAGE_SERVER_URL": "/files",
    "STORAGE_ALLOWED_EXTENSIONS": ALLOWED_EXTENSIONS
}) 

app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1694373074164463',
        'secret': 'b81a86062d08bac28b3397465b498e9e'
    }
    }

# Setup storage
storage = Storage()
storage.init_app(app) 

# class JSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if hasattr(obj, 'isoformat'): #handles both date and datetime objects
#             return obj.isoformat()
#         else:
#             return json.JSONEncoder.default(self, obj)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
    
@app.route('/')
@app.route('/admin')
def index():
    return render_template('admin.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route("/documents", methods=["GET"])
def documents_handler():
    if request.method == 'GET':
        # RETURN ALL DOCUMENTS IN DATABASE
        key_ids = []
        keywords = []
        missing = []
        doc_ids = []
        documents = []
        if request.args.get('keywords'):
            keywords = request.args.get('keywords').split(',')
        typereq = request.args.get('doc_type')
        print keywords
        if keywords :
            for key in keywords :
                #print key
                key_check = db.session.query(Key).filter(Key.key.like('%'+key+'%')).all()
                #print key_check
                for i in key_check :
                    print i
                    if i.id not in key_ids :
                        key_ids.append(i.id)
                    else :
                        missing.append(i.key)

            for key_id in key_ids :
                result = db.session.query(KeyTagDoc).filter_by(key_id=key_id).all()
                for i in result :
                    print str(i.key_id) + ' ' + str(i.doc_id)
                    if i.doc_id not in doc_ids :
                        doc_ids.append(i.doc_id)

            if typereq :
                for doc_id in doc_ids :
                    document = db.session.query(Document).filter_by(id = doc_id).filter_by(doctype = typereq).first()
                    if document :
                        documents.append(document)

                if documents:
                    return jsonify(documents = [i.serialize for i in documents])
                else :
                    return "fail"
            else :
                for doc_id in doc_ids :
                    document = db.session.query(Document).filter_by(id = doc_id).one()
                    documents.append(document)
                return jsonify(documents = [i.serialize for i in documents])
        else :
            return "fail"

@app.route("/documents/by_title", methods=["GET"])
def documents_handler():
    if request.method == 'GET':
        # RETURN ALL DOCUMENTS IN DATABASE SEARCHED BY TITLE
        if request.args.get('title'):
            title = request.args.get('title')
        typereq = request.args.get('doc_type')
        if typereq :
            documents = db.session.query(Document).filter(Document.title.like('%'+title+'%')).filter_by(doctype = typereq).all()
            if documents:
                return jsonify(documents = [i.serialize for i in documents])
            else :
                return "fail"
        else :
            documents = db.session.query(Document).filter(Document.title.like('%'+title+'%').all()
            if documents:
                return jsonify(documents = [i.serialize for i in documents])
            else :
                return "fail"

@app.route("/admin/documents", methods=["GET", "POST", "DELETE"])
def all_documents_handler():
    if request.method == 'GET':
        # RETURN ALL DOCUMENTS IN DATABASE
        documents = db.session.query(Document).all()
        return jsonify(documents = [i.serialize for i in documents])
    
    elif request.method == 'POST':
        # MAKE A NEW RESTAURANT AND STORE IT IN DATABASE
        file = request.files.get("file")
        file_upload = storage.upload(file)
        #title = request.form.get('doc_title')
        filename = file_upload.name
        doctype = file_upload.extension
        size = file_upload.size
        url = file_upload.url
        upload_on = datetime.now()
        downloads = 0
        title = request.form.get('title')
        author = request.form.get('author')
        document = Document(title=title, author=author, doctype=doctype, size=int(size), downloads=int(downloads), path=url, filename=filename, upload_on=upload_on)
        db.session.add(document)
        db.session.commit()
        
        key_ids = []
        keywords = request.form.get('keywords').split(',')
        for key in keywords :
            
            key_check = db.session.query(Key).filter_by(key=key).first()
            if key_check :
                 key_ids.append(key_check.id)
            else :
                new_key = Key(key = key)
                db.session.add(new_key)
                db.session.commit()
                key_ids.append(new_key.id)

        for key_id in key_ids :
            print key_id + document.id
            pair = KeyTagDoc(key_id=key_id, doc_id=document.id)
            db.session.add(pair)
            db.session.commit()
        
        # pairs = db.session.query(KeyTagDoc).all()
        # return jsonify(pairs = [i.serialize for i in pairs])
        return jsonify(document.serialize)

    elif request.method == 'DELETE':
        #DELETE A SPECFIC DOCUMENT
        num_rows_deleted3 = db.session.query(KeyTagDoc).delete()
        num_rows_deleted1 = db.session.query(Document).delete()
        num_rows_deleted2 = db.session.query(Key).delete()
        num = [num_rows_deleted3, num_rows_deleted2, num_rows_deleted1]
        db.session.commit()
        return "%s, %s, %s Document Deleted" % (num_rows_deleted2,num_rows_deleted3,num_rows_deleted1)
 
@app.route('/admin/documents/<int:id>', methods=["GET", "PUT", "DELETE"])
def document_handler(id):
  document = db.session.query(Document).filter_by(id = id).one()
  if request.method == 'GET':
    #RETURN A SPECIFIC DOCUMENT
    return jsonify(document = document.serialize)
  
  elif request.method == 'PUT':
    #UPDATE A SPECIFIC DOCUMENT
    file = request.files.get("file")
    if file:
        file_upload = storage.upload(file)
        filename = file_upload.name
        document.filename = filename
        doctype = file_upload.extension
        document.doctype = doctype
        size = file_upload.size
        document.size = size
        url = file_upload.url
        document.path = url
    title = request.args.get('title')
    author = request.args.get('author')
    # doctype = request.args.get('doc_type', '')
    # size = request.args.get('doc_size', '')
    upload_on = datetime.now()
    document.doctype = upload_on
    # keywords = request.args.get('keywords')
    if title :
        document.title = title
    if author :
        document.author = author
    db.session.commit()
    key_ids = []
    keywords = request.form.get('keywords').split(',')
    if keywords :    
        for key in keywords :
            
            key_check = db.session.query(Key).filter_by(key=key).first()
            if key_check :
                 key_ids.append(key_check.id)
            else :
                new_key = Key(key = key)
                db.session.add(new_key)
                db.session.commit()
                key_ids.append(new_key.id)

        for key_id in key_ids :
            print key_id + document.id
            pair = KeyTagDoc(key_id=key_id, doc_id=document.id)
            db.session.add(pair)
            db.session.commit()
    # if downloads:
    #     document.downloads = downloads
    #db.session.update(document)
    
    return jsonify(document = document.serialize)

  elif request.method == 'DELETE':
    #DELETE A SPECFIC DOCUMENT
    pairs = db.session.query(KeyTagDoc).filter_by(doc_id=id).all()
    for pair in pairs :
        db.session.delete(pair)
        db.session.commit()
    db.session.delete(document)
    db.session.commit()
    
    return "Document Deleted"

# A download endpoint, to download the file
# @app.route("/download/<path:object_name>")
# def download(object_name):
#     my_object = storage.get(object_name)
#     if my_object:
#         download_url = my_object.download_url()
#         return redirect(download_url)
#     else:   
#         abort(404, "File doesn't exist")

@app.route("/documents/download/<int:id>")
def download(id):
    document = db.session.query(Document).filter_by(id = id).one()
    document.downloads = document.downloads + 1
    #db.session.update(document)
    db.session.commit()
    my_object = storage.get(document.title)
    if my_object:
        resp = Response()
        download_url = my_object.download_url()
        resp.status = '300'
        resp.headers['Redirect'] = download_url
        return resp
    else:   
        abort(404, "File doesn't exist")
