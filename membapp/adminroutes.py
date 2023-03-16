from flask import render_template, request, redirect, flash, url_for, session
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from membapp import app,db
from membapp.models import Party,Topics

@app.route('/admin/topics')
def all_topics():
    if session.get("loggedin") == None:
        return redirect('/admin/login')
    else:
        posts = db.session.query(Topics).all()
        return render_template("admin/alltopics.html",posts=posts)
    
@app.route('/admin/topic/edit/<id>')
def edit_topic(id):
    if session.get("loggedin") != None:
        topic_deets=Topics.query.get(id)
        return render_template('admin/edit_topics.html',topic_deets=topic_deets)
    else:
        return redirect('/admin/login')

@app.route('/admin/update_topic',methods=['POST'])
def update_topic():
    if session.get("loggedin") != None:
        newstatus=request.form.get('status')
        topicid=request.form.get('topicid')
        #to update in orm
        topicobj = Topics.query.get(topicid)
        topicobj.topic_status=newstatus
        db.session.commit()
        flash('Topic successfully updated')
        return redirect('/admin/topics')
    else:
        return redirect('/admin/login')
    


@app.route('/admin/topic/delete/<id>')
def delete_post(id):
    topicobj = Topics.query.get_or_404(id)
    db.session.delete(topicobj)
    db.session.commit()
    flash('Successfully deleted')
    return redirect(url_for('all_topics'))

@app.route('/admin/',methods=['POST','GET'])
def admin_home():
    if request.method == "GET":
        return render_template('admin/adminreg.html')
    else:
        #to retrieve data coming from the form
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #convert the plain password to hashed value and insert into db
        hashed_pwd = generate_password_hash(pwd)
        #insert into database
        if username != '' or pwd != '':
            query = (f"INSERT INTO admin SET admin_username='{username}', admin_pwd='{hashed_pwd}'")
            db.session.execute(text(query))
            db.session.commit()
            flash("Registration Successful. Login Here")
            return redirect(url_for('admin_login'))
        else:
            flash("Username and password must be applied")
            return redirect(url_for('admin_home'))

@app.route('/admin/login/',methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/adminlogin.html')
    else:
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #write your select query
        query = f"SELECT * FROM admin WHERE admin_username='{username}'"
        result = db.session.execute(text(query))
        total = result.fetchone()
        if total: #the username exists
            pwd_indb = total[2] #hashed pwd from the db
            chk = check_password_hash(pwd_indb,pwd) #returns True or False
            if chk == True:
                session['loggedin']=username
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials')
                return redirect(url_for('admin_login'))  
        else:
            flash('Invalid credentials')
            return redirect(url_for('admin_login'))

@app.route('/admin/dashboard/')
def admin_dashboard():
    if session.get('loggedin') != None:
        return render_template('admin/index2.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    if session.get('loggedin') != None:
        session.pop('loggedin',None)
    return redirect(url_for('admin_login'))

@app.route('/admin/party/',methods=['POST','GET'])
def add_party():
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        if request.method == 'GET':
            return render_template('admin/addparty.html')
        else:
            partyname = request.form.get('partyname')
            code = request.form.get('partycode')
            contact = request.form.get('partycontact')
            #insert into party table using ORM method
            #step1: create an instance of Party obj=Classname(column1=value,column2=value)
            p = Party(party_name=partyname,party_shortcode=code,party_contact=contact)
            #step2: add to session
            db.session.add(p)
            #step3: commit the session
            db.session.commit()
            flash("Party Added")
            return redirect('/admin/parties')

@app.route('/admin/parties/')
def admin_party():
    if session.get('loggedin') != None:
        #fetch from db using ORM method
        data = db.session.query(Party).order_by(Party.party_shortcode.desc()).all()
        return render_template('admin/all_parties.html',data=data)
    else:
        return redirect(url_for('admin_login'))