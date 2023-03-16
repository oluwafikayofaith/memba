import os,random,string,json,requests
from flask import render_template,request,session,flash,redirect,url_for
#from sqlalchemy import or_
#from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash,check_password_hash
from membapp import app,db
from membapp.models import User,Party,Topics,Contact,Comments,Lga,State,Donation,Payment
from membapp.forms import ContactForm

#generating random names
def generate_name():
    filename = random.sample(string.ascii_lowercase,10)#this will return a list
    return ''.join(filename)#join every member of the list filename together

#creating routes
@app.route('/load_lga/<stateid>',methods=['GET'])
def load_lga(stateid):
    lgas=db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send="<select class='form-control border-success'>"
    for s in lgas:
        data2send= data2send+"<option>"+s.lga_name+"</option>"
    data2send=data2send+"</select>"
    return data2send


@app.route('/check_username',methods=['POST','GET'])
def check_username():
    if request.method == 'GET':
        return 'Please complete form normally'
    else:
        email=request.form.get('email')
        data=db.session.query(User).filter(User.user_email==email).first()
        if data == None:
            sendback={'status':1,'feedback':'Email is available,please register'}
            return json.dumps(sendback)
        else:
            sendback={'status':0,'feedback':'You have register already,click here to <a href="user_login">login</a>'}
            return json.dumps(sendback)


@app.route('/')
def home():
    #return app.config['SERVER_ADDRESS'] checking for config object
    #contact=ContactForm
    #connent to the end point to get list of properties in json format
    #convert to python dict and pass it to our template
    try:
        response=requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson=json.loads(response.text)
        else:
            rspjson= dict()
    except:
            rspjson={}
    return render_template('user/home.html',rspjson=rspjson)


@app.route("/donate",methods=["POST","GET"])
def donate():
    if session.get('user') != None:
        deets= User.query.get(session.get('user'))
    else:
        deets=None    
    if request.method =='GET':
        return render_template('user/donation_form.html',deets=deets)
    else:
        #retrieve the form data and insert into Donation table
        amount = request.form.get('amount')
        fullname = request.form.get('fullname')
        d = Donation(don_donor=fullname,don_amt=amount,don_userid=session.get('user'))
        db.session.add(d); db.session.commit()
        session['donation_id'] = d.don_id
        #Generate the ref no and keep in session
        refno = int(random.random()*100000000)
        session['reference'] = refno
        return  redirect("/confirm") 
 
@app.route('/confirm',methods=['POST','GET'])
def confirm():
    if session.get('donation_id')!= None:
        if request.method =='GET':  
            donor = db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html',donor=donor,refno=session['reference'])
        else:
            p = Payment(pay_donid=session.get('donation_id'),pay_ref=session['reference'])
            db.session.add(p)
            db.session.commit()
            don = Donation.query.get(session['donation_id'])#details of the donation
            donor_name = don.don_donor
            amount = don.don_amt * 100
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
            data={"amount":amount,"reference":session['reference'],"email":donor_name}
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson= json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm')
    else:
        return redirect('/donate')
    

@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid ==None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
        verifyurl= "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']== True:
            #payment was successful
            return rspjson
        else:
            #payment was not successful
            return "payment was not successful"

@app.route('/signup')
def user_signup():
    data = db.session.query(Party).all()
    return render_template('user/signup.html',data=data)

@app.route('/login',methods=['POST','GET'])
def user_login():
    if request.method =='GET':
        return render_template("user/login.html")
    else:
        #retrieve the form data
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        #run a query to know if the username exists on the db
        deets=db.session.query(User).filter(User.user_email==email).first()
        #compared the password coming from the form with hashed pwd in db
        if deets != None:
            pwd_indb= deets.user_pwd
        #if the pwd chech above is right,we should log them in
        #by keeping their details(user_id) in session['user']
            chk=check_password_hash(pwd_indb,pwd)
            if chk:
                id= deets.user_id
                session['user']=id
                return redirect (url_for("dashboard"))
            else:
                flash("invalid password")
                return redirect(url_for('user_login'))
        else:
            flash('invalid credential')
            return redirect(url_for('user_login'))
        

@app.route("/register", methods=['POST'])
def register():
    party=request.form.get('partyid')
    email=request.form.get('email')
    pwd=request.form.get('pwd')
    hashed_pwd=generate_password_hash(pwd)
    if party !='' and email !='' and pwd !='':
        u=User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid=party)
        db.session.add(u)
        db.session.commit()
        userid=u.user_id
        session['user']=userid
        return redirect(url_for('dashboard'))
    else:
        flash('You must complete all the fields to signup')
        return redirect(url_for('user_signup'))
    
@app.route('/dashboard')
def dashboard():
    #protect this route so that only logged in user can gget here
    if session.get('user') != None:
        #retrieve the details of the logged in user
        id=session['user']
        deets=db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)
    else:
        return redirect(url_for('user_login'))
    

@app.route('/logout')
def user_logout():
    #pop the session and redirect to home page
    if session.get('user')!=None:
        session.pop('user',None)
    return redirect('/')

@app.route('/profile',methods=["POST","GET"])
def profile():
    id=session.get('user')
    if id == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            allstates=db.session.query(State).all()
            deets=db.session.query(User).get(id)
            allparties=Party.query.all()
            return render_template ('user/profile.html',deets=deets,allstates=allstates,allparties=allparties)
        else:#form was submitted
            fullname=request.form.get('fullname')
            phone=request.form.get('phone')
            #update the db using ORM method
            userobj=db.session.query(User).get(id)
            userobj.user_fullname=fullname
            userobj.user_phone=phone
            db.session.commit()
            flash('profile updated')
            return redirect("/dashboard")
        
@app.route('/contact',methods=['POST','GET'])
def contact_us():
    #instantiate an object of contactform
    contact = ContactForm()
    if request.method == 'GET':
        return render_template('user/contact.html',contact=contact)
    else:
        if contact.validate_on_submit():
            #retrieve form data and insert into db
            email=request.form.get('email')
            msg=contact.message.data
            #upload=contact.screenshot.data#request.files.get('screenshot')
            #insert into database
            cm=Contact(msg_email=email,msg_content=msg)
            db.session.add(cm)
            db.session.commit()
            flash('Thanks for contacting us')
            return redirect(url_for('contact_us'))
        else:#false
            return render_template('user/contact.html',contact=contact)
        
@app.route('/profile/picture',methods=["POST","GET"])
def profile_picture():
    
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file=request.files['pix']
            #to know the file name
            filename= file.filename
            
            allowed=['.png','.jpg','.jpeg']
            if filename !='':
                name,ext=os.path.splitext(filename)
                if ext.lower() in allowed:
                    newname= generate_name()+ext
                    file.save('membapp/static/uploads/'+newname)
                    user=db.session.query(User).get(session['user'])
                    user.user_pix=newname
                    db.session.commit()
                    flash('file uploaded'+file.mimetype)
                    return redirect('/dashboard') 
                else:
                    return "File extension not allowed"
            else:
                flash('please choose a file')
                return redirect('/profile/picture')
            
@app.route('/blog',methods=['POST','GET'])
def blog():
    articles = db.session.query(Topics).filter(Topics.topic_status=='1').all()
    return render_template('user/blog.html',articles=articles)
    
@app.route('/newtopic',methods=['POST','GET'])
def newtopic():
    if session.get('user') != None:
        if request.method=='GET':
            return render_template('user/newtopic.html')
        else:
            content=request.form.get('content')
            if len(content) > 0:
                t=Topics(topic_title=content,topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash('message posted')
                else:
                    flash('OOps, somthing went wrong')
            else:
                flash('you cannot submit an empty post')
            return redirect('/blog')
    else:
        return redirect(url_for('user_login'))
    
@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        usermessage=request.args.get('message')
        userid=request.args.get('userid')
        topicid=request.args.get('topicid')
        com=Comments(comment_text=usermessage,comment_userid=userid,comment_topicid=topicid)
        db.session.add(com)
        db.session.commit()
        commenter= com.commentby.user_fullname
        dateposted=com.comment_date
        sendback= f"{usermessage} <br>by {commenter} on {dateposted}"
        return sendback
    else:
        return 'Comment was not posted,you need to login'

@app.route('/ajaxcontact',methods=['POST'])
def contact_ajax():
    email=request.form.get('email')
    message=request.form.get('message')
    return f"{email} and {message}"

@app.route('/blog/<id>/')
def blog_details(id):
    blog_deets = Topics.query.get(id)
    #blog_deets = db.session.query(Topics).get_or_404(id)
    blog_deets = db.session.query(Topics).filter(Topics.topic_id== id).first()
    return  render_template('user/blog_details.html',blog_deets=blog_deets)

@app.route("/demo")
def demo():
    #data=db.session.query(Party).filter(Party.party_id > 1,Party.party_id < 6).all()
    #data=db.session.query(Party).get(1)
    #data=db.session.query(Party).filter(Party.party_id> 1).filter(Party.party_id <=6).all()
    #data=db.session.query(User).filter(User.user_email==email).filter(User.user_pwd==pwd).first()
    #to get all user in your db table
    #data=db.session.query(User,Party).join(Party).all()
    data=db.session.query(User.user_fullname,Party.party_name,Party.party_contact,Party.party_shortcode).join(Party).all()
    data =  User.query.join(Party).filter(Party.party_name=='APC').add_column(Party).all()
    data =  User.query.join(Party).add_column(Party).all()
    data =  User.query.join(Party).filter(User.user_email=='ikeremadu@gmail.com').add_column(Party).all()
    data =  User.query.join(Party).filter(User.user_email !='ikeremadu@gmail.com').add_column(Party).all()
    data =  User.query.join(Party).filter(User.user_fullname.like('%hello%')).add_column(Party).all()
    data =  User.query.join(Party).filter(User.user_fullname.ilike('%hello%')).add_column(Party).all()
    data =  User.query.join(Party).filter(~User.user_fullname.in_(['timi','tolu','hello'])).add_column(Party).all()
    
    data = db.session.query(Party).filter(Party.party_id==1).first()
    data = db.session.query(User).get(1)
    return render_template("user/test.html",data=data)
