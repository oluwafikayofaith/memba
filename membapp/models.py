from datetime import datetime
from membapp import db

class Contact(db.Model):
    __tablename__='messages'
    msg_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    msg_email = db.Column(db.String(100),nullable=False)
    msg_content = db.Column(db.Text(),nullable=False)
    msg_date =db.Column(db.DateTime(), default=datetime.utcnow)


class State(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    state_name = db.Column(db.String(100),nullable=False) 
    #set relationship
    lgas = db.relationship("Lga", back_populates="state_deets")

class Lga(db.Model):
    lga_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    lga_name = db.Column(db.String(100),nullable=False)
    lga_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))    
    #set relationships
    state_deets = db.relationship("State", back_populates="lgas")
    #state_deets = db.relationship("State", backref="lgas")
    

class Topics(db.Model):
    topic_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    topic_title = db.Column(db.Text(),nullable=False)
    topic_date =db.Column(db.DateTime(), default=datetime.utcnow)
    topic_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)  
    topic_status =db.Column(db.Enum('1','0'),nullable=False,server_default=('0'))  
    
    #set relationships
    userdeets = db.relationship("User", back_populates="topics_postedbyme")
    all_comments = db.relationship("Comments", back_populates="the_topic",cascade='all,delete-orphan')


class Donation(db.Model):
    don_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    don_amt = db.Column(db.Float, nullable=False) 
    don_donor =db.Column(db.String(200),nullable=True)
    don_userid = db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=True)
    don_date = db.Column(db.DateTime(), default=datetime.utcnow)
    don_status =db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending"))  
    donor = db.relationship('User',backref='mydonations')

class Payment(db.Model):
    pay_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    pay_donid=db.Column(db.Integer,db.ForeignKey("donation.don_id"),nullable=True)
    pay_amount_deducted=db.Column(db.Float) 
    pay_date=db.Column(db.DateTime(), default=datetime.utcnow)
    pay_status=db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending"))  
    pay_ref=db.Column(db.String(100),nullable=True)
    pay_others=db.Column(db.Text(),nullable=True)
    #relationship
    donation_deets = db.relationship('Donation',backref='paydeets')



class Comments(db.Model):
    comment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    comment_text = db.Column(db.String(255),nullable=False)
    comment_date =db.Column(db.DateTime(), default=datetime.utcnow)
    comment_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)  
    comment_topicid =db.Column(db.Integer, db.ForeignKey('topics.topic_id'),nullable=False)  
    
    #set relationships
    commentby = db.relationship("User", back_populates="mycomments")
    the_topic = db.relationship("Topics", back_populates="all_comments")
    
      
class User(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fullname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120)) 
    user_pwd=db.Column(db.String(120),nullable=True)
    user_phone=db.Column(db.String(120),nullable=True) 
    user_pix=db.Column(db.String(120),nullable=True) 
    user_datereg=db.Column(db.DateTime(), default=datetime.utcnow)#default date
    #set the foreign key 
    user_partyid=db.Column(db.Integer, db.ForeignKey('party.party_id'))    
    #set relationships
    party_deets = db.relationship("Party", back_populates="partymembers")
    topics_postedbyme = db.relationship("Topics", back_populates="userdeets")
    mycomments = db.relationship("Comments", back_populates="commentby")
 
class Party(db.Model):
    party_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    party_name = db.Column(db.String(100),nullable=False)
    party_shortcode = db.Column(db.String(120)) 
    party_logo=db.Column(db.String(120),nullable=True)
    party_contact=db.Column(db.String(120),nullable=True)     
    #set relationship
    partymembers = db.relationship("User", back_populates="party_deets")
    
class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=True)
    admin_pwd=db.Column(db.String(200),nullable=True)