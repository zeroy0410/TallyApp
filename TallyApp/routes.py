from flask import redirect, render_template,url_for,flash,request,abort,send_file
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from TallyApp.forms import LoginForm, RegistrationForm,DataForm, UploadForm
from TallyApp.models import User,Data
from TallyApp import db,app,bcrypt
from pyecharts.charts import Pie 
import os
import pandas as pd

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('账号注册成功','success')
        return redirect(url_for('login'))
    return render_template("register.html",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('profile'))
        else:
            flash('登录失败，请检查您的用户名和密码', 'danger')
    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

cate=[[],['','餐饮','交通','学习','娱乐','其它'],['','工资','奖金','家人','朋友','其它']]
def getPie(opti):
    addrs=db.session.query(Data.category,func.sum(Data.cost)).filter_by(option=opti,owner=current_user).group_by(Data.category).all()
    lis=[0,0,0,0,0]
    for addr in addrs:
        lis[addr[0]-1]=float("%.2f" % addr[1])
    pie=Pie()
    pie.add("",[list(z) for z in zip(cate[opti][1:6],lis)])
    return pie

@app.route("/profile")
@login_required
def profile():
    op=['','支出','收入']
    datas=Data.query.filter_by(owner=current_user).order_by(Data.date_added.desc()).all()
    Sum=db.session.query(func.sum(Data.cost)).filter_by(owner=current_user).all()
    sum=float(0)
    if Sum[0][0]:
        sum=Sum[0][0]
    for data in datas:
        data.cost=abs(data.cost)
    pie1=getPie(1)
    pie2=getPie(2)
    sum=float("%.2f" % sum)
    return render_template("profile.html",datas=datas,op=op,cate=cate,sum=sum,pie1=pie1.dump_options(),pie2=pie2.dump_options())

@app.route("/data/new/<int:opti>", methods=['GET','POST'])
@login_required
def new_data(opti):
    form = DataForm()
    dic={1:'支出',2:'收入'}
    if opti==1:
        form.category.choices=[(1,'餐饮'),(2,'交通'),(3,'学习'),(4,'娱乐'),(5,'其它')]
    else:
        form.category.choices=[(1,'工资'),(2,'奖金'),(3,'家人'),(4,'朋友'),(5,'其它')]
    if form.validate_on_submit():
        data = Data(option=opti,category=form.category.data,notes=form.notes.data, cost=form.cost.data, date_added=form.date_added.data,owner=current_user)
        if opti==1:
            data.cost=-data.cost
        db.session.add(data)
        db.session.commit()
        flash('记账成功', 'success')
        return redirect(url_for('profile'))
    return render_template('new_data.html',title=f'新的{dic[opti]}',form=form)

@app.route("/data/<int:data_id>/update/<int:opti>", methods=['GET','POST'])
@login_required
def update_data(data_id,opti):
    data = Data.query.get_or_404(data_id)
    if data.owner != current_user:
        abort(403)
    form = DataForm()
    if opti==1:
        form.category.choices=[(1,'餐饮'),(2,'交通'),(3,'学习'),(4,'娱乐'),(5,'其它')]
    else:
        form.category.choices=[(1,'工资'),(2,'奖金'),(3,'家人'),(4,'朋友'),(5,'其它')]
    if form.validate_on_submit():
        data.notes=form.notes.data
        data.cost=form.cost.data
        if opti==1:
            data.cost=-form.cost.data
        data.date_added=form.date_added.data
        data.category=form.category.data
        db.session.commit()
        flash('修改数据成功', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.notes.data=data.notes
        form.cost.data=data.cost
        if opti==1:
            form.cost.data=-data.cost
        form.date_added.data=data.date_added
        form.category.data=data.category
    return render_template('new_data.html', title='修改数据',form=form)

@app.route("/data/<int:data_id>/delete", methods=['GET','POST'])
@login_required
def delete_data(data_id):
    data = Data.query.get_or_404(data_id)
    if data.owner != current_user:
        abort(403)
    db.session.delete(data)
    db.session.commit()
    flash('删除数据成功', 'success')
    return redirect(url_for('profile'))

@app.route("/download",methods=['GET','POST'])
@login_required
def download():
    datas=Data.query.filter_by(owner=current_user).all()
    categories=[]
    noteses=[]
    costs=[]
    date_addeds=[]
    options=[]
    for data in datas:
        categories.append(data.category)
        noteses.append(data.notes)
        costs.append(data.cost)
        options.append(data.option)
        date_addeds.append(data.date_added)
    dic={"收支":options,"分类":categories,"数目":costs,"备注":noteses,"日期":date_addeds}
    df = pd.DataFrame(dic)
    save_pat=os.path.join(app.root_path,'dynamic',str(current_user.id)+'.xlsx')
    df.to_excel(save_pat)
    return send_file(save_pat)
    # return redirect(url_for('profile'))

@app.route("/upload",methods=['GET','POST'])
@login_required
def upload():
    form=UploadForm()
    if form.validate_on_submit():
        save_pat=os.path.join(app.root_path,'dynamic',str(current_user.id)+'temp.xlsx')
        form.file_.data.save(save_pat)
        print(save_pat)
        df=pd.read_excel(save_pat)
        for item in df.itertuples():
            tmp=str(item[5])
            if tmp=='nan':
                tmp=''
            data=Data(option=item[2],category=item[3],cost=item[4],notes=tmp,date_added=item[6],owner=current_user)
            db.session.add(data)
            db.session.commit()
        return redirect(url_for('profile'))
    return render_template('upload.html',form=form,title="上传Excel xslx文件")
