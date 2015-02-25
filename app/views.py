from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager,login_user,logout_user,current_user,login_required
from flask import Flask,render_template,url_for,request,redirect,jsonify,session
import os

from PIL import Image,ImageDraw,ImageFont

import datetime
from mongoengine import *
from werkzeug import secure_filename
 


app=Flask(__name__)
app.config['MONGODB_SETTINGS']={'db':'jokecloud'}
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set([  'png', 'jpg', 'jpeg', 'gif'])

app.secret_key="akshaybjijjpbuop19"
db=MongoEngine(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='home'
app.debug = True

#//////////////////////////HANDLING ERROR PAGES///////////////////////////////////////////////////////////////

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'),404

#///////////////////////////////////////////////////////////database////////////////////////////////////////
class User(db.Document):
    name=StringField()
     
    mailid=StringField()
    pwd=StringField()

    def is_authenticated(self):
	return True

    def is_active(self):
	return True

    def is_anonymous(self):
	return False
	
    def get_id(self):
	print(self.mailid)
	return self.mailid

    def __repr__(self):
	return '<User %r>' %(self.username)


class post(db.Document):
    user=ReferenceField('User')
    header=StringField(max_length=50,required=True)
    #description=StringField(max_length=100,required=True)
    img_path=StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    meta = {
        'ordering': ['-created_at']    }
    width=IntField()
    height=IntField()
    vote=IntField(default=0)
    allowed=BooleanField(default=False)

class Awesome(db.Document):
    post=ReferenceField('post')
    user=ReferenceField('User')
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#/////////////////////////////////////////////////////////////////////////////////
WIDTH=500
HEIGHT=380
#/////////////////////////////////////LOGIN///////////////////////////////??#

@login_manager.user_loader
def load_user(mail):
    t= User.objects(mailid=mail).first()
    print(t)
    return t


#/////////////////////////////////////upload //////////////////////////////////#
@app.route('/upload')
@login_required
def upload():

    return render_template('upload.html')    

#////////////////////////////////checking file extensions ///////////////////////
def allowed_file(filename):
    return '.' in filename and  filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#///////////////////////////////////////////////////////////////////////////////
@app.route('/upload',methods=['POST'])
@login_required
def upload_post():
        title=request.form['title']
        file=request.files['file']
        #description=request.form['description']
        #top_text=request.form['top_text']
        
        if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
             # Move the file form the temporal folder to
        # the upload folder we setup
                

                path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
        # Redirect the user to the uploaded_file route, which
        # will basically show on the browser the uploaded file
        #return redirect(url_for('uploaded_file',
          #                      filename=filename))
        mail=session['email']
        print(mail)
        user=User.objects(mailid=mail).first()
        a=post()
        a.user=user
        print(user.name)
        a.allowed=False
        a.header=title
        a.width=WIDTH
        a.height=HEIGHT
        a.img_path=path
        a.published_date= datetime.datetime.now()
        a.save()


       

        return redirect(url_for('uptest'))
        return 'saved'+ title+ ' '+path+' '+description


@app.route('/uploadtest')
@login_required
def uptest():
    

    
    counter=int(request.args.get('option','0'))
    print(request.args.get('option',''))
    page=0
    per_page=100
    #if request.args:
    #c=counter+5
    #if c <= post_count:
    #    p=post.objects[counter:counter+5].all()
    #else:
    #    p=post.objects[counter:post_count].all()
    #return jsonify(result=p)
    #p=post.objects.paginate(page=counter,per_page=5)    
        
        #p=post.objects(allowed=False).skip(page).limit(per_page).all()
       # page=10*counter
    #return jsonify(result=p)
        #return render_template ("home.html",images=p) 


    user=User.objects(id=current_user.id).first()
    posts=post.objects(user=user).first()

    awesome=Awesome.objects(post=posts).first()
    print('test')
    print(awesome)
    if awesome is None:
        print('None')
        posts_liked=None
    else:
        posts_liked=awesome
        print('liked')
        print(posts_liked)
    p=post.objects(allowed=True).all()
    #p1=post.objects.paginate(page=0,per_page=5)
    t=post.objects(allowed=True).order_by('-vote').limit(6
        ).all()
    #return jsonify(result=p)
    return render_template ("home.html",images=p,user=current_user,awesome=posts_liked,trending=t)

@app.route('/uploadtest',methods=['POST'])
@login_required
def uptest_post():

    content=request.json
    print(content['id'])
    p=post.objects(pk=content['id'])
    p.update_one(inc__vote=1)

    user=User.objects(id=current_user.id).first()

    awesome=Awesome()
    awesome.user=user
    awesome.post=p.first()
    awesome.save()
    print('awesome created')
    obj=post.objects(pk=content['id']).first() 

    obj.reload()
    print(obj.vote)
    return str(obj.vote) 

@app.route('/admin')
@login_required
def admin():

    p=post.objects(allowed=False).all()

    return render_template ("admin_test.html",images=p)
    return render_template ("admin.html")

@app.route('/admin',methods=['POST'])
@login_required
def admin_post():
    content=request.json
    print(content['id'])
    id=content['id']
    print('id')
    print(id)
    #p.allowed=True
    p=post.objects(pk=content['id'])
    p.update_one(set__allowed=True)



    print(p.allowed)
    p1=post.objects(pk=id).first()
    p.reload()
    return '''<html> <h1>addded</h1></html>'''

@app.route('/admin',methods=['POST'])

def loginadmin():
    password=request.form['password']
    if password =="akshayjokecloud":
        return render_template("admin.html")

    return render_template('''<html> <body><h1>Error in Login .Retry.</h1></body></html>''')

@app.route('/')
@app.route('/home')
def home():
    obj=post.objects.first()
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login():
    if request.form['email'] and request.form['pwd']:
        mailid=request.form['email']
        password=request.form['pwd']
        obj=User.objects.filter(Q(mailid=mailid) & Q(pwd=password)).first() 
         
        
        if obj:
            print('User is found')
            login_user(obj)
	    session['email']=mailid
            return redirect(url_for('uptest'))
        else:
            return render_template('login.html',error="Email or Password is wrong")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))

@app.route('/register')
def registerGET():
    return render_template("register.html")

@app.route('/register',methods=['POST'])
def register():
    if request.form['email'] and request.form['pwd']:
        mail=request.form['email']
        obj=User.objects(mailid=mail).first()
        if obj:
            return ("Error. Already Registered")
        else:
            p=User()
            p.name=request.form['name']
            p.mailid=request.form['email']
            session['email']=mail 
            p.pwd=request.form['pwd']
            p.save()
            return redirect(url_for('uptest'))



@app.route('/search')
@app.route('/search/<int:id>')
def search(id=0):
    return render_template('search.html')

@app.route('/testid')
def testid():
    p=post.objects.all()

    for a in p:
        print(a.pk)
    return "testid"


if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")





 
