from datetime import datetime
from TallyApp import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get((int)(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(20),nullable=False)
    datas=db.relationship('Data',backref='owner',lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Data(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    category=db.Column(db.Integer,nullable=True)
    date_added=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    notes=db.Column(db.String(100),nullable=True)
    cost=db.Column(db.Integer,nullable=False)
    option=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"Data('{self.category}','{self.date_added}','{self.notes}')"
