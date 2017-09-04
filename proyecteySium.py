__author__ = 'gadh'
from flask import Flask, render_template, request, redirect, url_for,session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,ThngsProjs, Types,Things,Projects,Students
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField,SubmitField,IntegerField,ValidationError,SelectField,PasswordField
from wtforms.widgets import TextArea

# import flask_psycopg2
app = Flask(__name__)
Bootstrap(app)


app.secret_key = 'development key'

engine = create_engine('postgresql-triangular-48756')
# engine = create_engine('sqlite:///try.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbSession = DBSession()

Guides = ['Sol', 'Yifaat', 'Dana', 'Gad']

class NewProj(FlaskForm):
    name = StringField('name', validators=[DataRequired])
    teur=StringField(u'Description', validators=[DataRequired],widget=TextArea())
    submit = SubmitField("Define Group")

def myFieldCheck(field):
    if field.data<50 or field.data>100:
        raise ValidationError('Field must be between 50 and 100')

class makeGrade(FlaskForm):
    Guides = ['Sol', 'Yifaat', 'Dana', 'Gad']
    guide = SelectField(choices=zip(Guides,Guides))
    grade = IntegerField('Grade', validators=[myFieldCheck])
    submit = SubmitField("Grade Project")

class Login(FlaskForm):
    guide = StringField('Guide',validators=[DataRequired])
    password = PasswordField('Password',validators=[DataRequired])
    submit = SubmitField("Check Password")

def makeQuery():
    rep=dbSession.query(Projects.name,Students.name,Things.name).\
        join(Students,ThngsProjs).\
        filter(Things.id==ThngsProjs.idThings).\
        all()
    try:
        lst=[]
        stuSet=set()
        thingSet=set()
        prev=rep[0][0]
        for r in rep:
            cur=r[0]
            if cur==prev:
                stuSet.add(r[1])
                thingSet.add(r[2])
            else:
                lst.append(prev)
                lst.append(stuSet)
                lst.append(thingSet)
                prev=cur
                stuSet=set()
                thingSet=set()
        lst.append(cur)
        lst.append(stuSet)
        lst.append(thingSet)
    except IndexError:
        pass
    return lst

@app.route('/')
def start():
    lst=makeQuery()
    return render_template('report.html',rep=lst)

@app.route('/fillThings')
def fillThings():
    'Include types of things'
    try:
        dbSession.query(Types).delete()
        dbSession.query(Things).delete()
        dbSession.commit()
    except:
        dbSession.rollback()
        return 'Types were not deleted'
    robot=Types(id=1,name='robot')
    lego=Types(id=2,name='lego')
    tablet=Types(id=3,name='tablet')
    for i in robot,lego,tablet:
        dbSession.add(i)
    dbSession.commit()
    legoNames=('Arafat1','Bibi2','Sara3','OHazan4','MAtias5','Bugi6','DBlat7','Tayson8','GGadot9','NBenet10','YLapid11')
    for l in range(len(legoNames)):
        sug=Things(id=l,name=legoNames[l],types=lego)
        dbSession.add(sug)
        dbSession.commit()
    for l in range(len(legoNames),len(legoNames)+6):
        r=Things(id=l,name='r%s' %str(l-len(legoNames)+1) ,types=robot)
        dbSession.add(r)
        dbSession.commit()
    for l in range(len(legoNames)+6,len(legoNames)+12):
        t=Things(id=l,name='t%s' %str(l-(len(legoNames)+5)) ,types=tablet)
        dbSession.add(t)
        dbSession.commit()
    return 'Done'

@app.route('/fillStudent')
def fillStudent():
    f=open('engStudents.csv','r')
    txt=f.read()
    lines=txt.split('\n')
    f.close()
    count=1
    for l in lines[:-1]:
        _,first,last=l.split(',')
        # print count,first+' '+last
        try:
            dbSession.add(Students(id=count,name=first+' '+last)) #Hebrew try fix later
            dbSession.commit()
        except:
            dbSession.rollback()
        count+=1
    q=dbSession.query(Students).all()
    output = ''
    for i in q:
        output += str(i.id)+' '+i.name+'<br>'
    return output
    # return 'Students were created in DB'

@app.route('/fillProject',methods=['GET','POST'])
def fillProjects():
    form=NewProj()
    if request.method == 'POST':
        name=form.name.data
        teur=form.teur.data
        project = Projects(name=name,teur=teur,guide='cimlab',grade=55)
        try:
            dbSession.add(project)
            dbSession.commit()
        except:
            dbSession.rollback()
        project=dbSession.query(Projects).filter(Projects.name==name).one()
        # print project
        return redirect(url_for('newGroup',pName=name,pDesc=teur,id=project.id))
    else:
        return render_template('newProject.html',form=form)

def mySplit(myLst):
    mystr=str(myLst)
    res=mystr.split(',')
    newRes=[]
    for r in res:
        indx=r.find('\\')
        newRes.append(r[3:indx])
    return newRes

@app.route('/newGroup/<string:pName>/<string:pDesc>/<int:id>',methods=['GET','POST'])
def newGroup(pName,pDesc,id):
    if request.method == 'POST':
        vals=request.form.getlist('talmid')
        lst=mySplit(vals)
        for l in lst:
            try:
                for s in dbSession.query(Students).filter(Students.name.startswith(l[:5])):
                    s.projectId=id
                dbSession.commit()
            except:
                dbSession.rollback()
        # print 'PName=',pName,'id=',id
        return redirect(url_for('newGear',vals=vals,pName=pName,id=id))
    else:
        students=dbSession.query(Students).all()
        return render_template('newGroup.html',pName=pName,pDesc=pDesc,students=students)

@app.route('/newGear/<string:vals>/<string:pName>/<int:id>',methods=['GET','POST'])
def newGear(vals,pName,id):
    lst=mySplit(vals)
    rhivim=[]
    if request.method=='POST':
        dvarim=request.form.getlist('davar')
        # print dvarim
        for d in dvarim:
            thingInProj=ThngsProjs(idThings=d,idProj=id)
            try:
                dbSession.add(thingInProj)
                for s in dbSession.query(Things.name).filter(Things.id=='%s' %d):
                    rhivim.append(s)
                dbSession.commit()
            except:
                dbSession.rollback()
        return render_template('sikum.html',dvarim=rhivim,pName=pName,vals=vals,lst=lst)
    else:
        things=dbSession.query(Things.id,Things.name,Types.name).\
            filter(Types.id==Things.typeId).all()
        return render_template('newGear.html',vals=vals,lst=lst,pName=pName,things=things)

@app.route('/editProject/<string:projectName>',methods=['GET','POST'])
def editProject(projectName):
    editedProject = dbSession.query(Projects).filter_by(name=projectName).one()
    if request.method=='POST':
        name=request.form["shem"]
        descr=request.form["teur"]
        members=request.form.getlist("talmid")
        equipment=request.form.getlist("davar")
        editedProject.name=name
        editedProject.teur=descr
        try:
            dbSession.add(editedProject)
            dbSession.commit()
        except:
            dbSession.rollback()
        men=dbSession.query(Students).filter(Students.projectId==editedProject.id).all()
        for m in men:
            m.projectId=None
            try:
                dbSession.add(m)
                dbSession.commit()
            except:
                dbSession.rollback()
        for m in members:
            talmid=dbSession.query(Students).filter(Students.id==m).one()
            talmid.projectId=editedProject.id
            try:
                dbSession.add(talmid)
                dbSession.commit()
            except:
                dbSession.rollback()
        tmps=dbSession.query(ThngsProjs).filter(ThngsProjs.idProj==editedProject.id).all()
        for t in tmps:
            try:
                dbSession.delete(t)
                dbSession.commit()
            except:
                dbSession.rollback()
        for e in equipment:
            davar=ThngsProjs(idThings=e,idProj=editedProject.id)
            try:
                dbSession.add(davar)
                dbSession.commit()
            except:
                dbSession.rollback()
        return redirect(url_for('start'))
    else:
        students=dbSession.query(Students).filter(Students.projectId==editedProject.id).all()
        talmidim=dbSession.query(Students).all()
        things=dbSession.query(Things).filter(Things.id==ThngsProjs.idThings).\
            filter(ThngsProjs.idProj==editedProject.id).all()
        dvarim=dbSession.query(Things).all()
        return render_template('editProject.html',projects=editedProject,students=students,things=things,talmidim=talmidim,dvarim=dvarim)

def graded():
    ids=dbSession.query(ThngsProjs.idProj).all()
    zihui=dbSession.query(Students.projectId).all()
    projects = dbSession.query(Projects).filter(Projects.id.in_(ids)). \
                filter(Projects.id.in_(zihui)).all()
    return projects

@app.route('/secret-page',methods=['GET','POST'])
def secret_page():
    form=Login()
    if request.method=='POST':
        if form.guide.data in Guides and form.password.data=='Randomally':
            projects=graded()
            return render_template('secret_page.html',projects=projects)
        else:
            msg='Wrong User or wrong Password please type again'
            return render_template('login.html',form=form,msg=msg)
    else:
        msg=''
    return render_template('login.html',form=form,msg=msg)

@app.route('/gradeProject/<string:projectName>',methods=['GET','POST'])
def gradeProject(projectName):
    gradedProject = dbSession.query(Projects).filter_by(name=projectName).one()
    # form = makeGrade()
    if request.method=="POST":
        guide = request.form.get("morim")
        grade = request.form["grade"]
        # print (guide,grade)
        gradedProject.guide = guide
        gradedProject.grade = int(grade)
        try:
            dbSession.add(gradedProject)
            dbSession.commit()
        except:
            dbSession.rollback()
        projects=graded()
        return render_template('summary.html',projects=projects)
    else:
        return render_template('grade.html',guides=Guides,projectName=projectName)

@app.route('/gradeProject/<int:projectId>',methods=['GET','POST'])
def deleteProj(projectId):
    if request.method=='POST':
        res=dbSession.query(Projects).filter(Projects.id==projectId).one()
        id=res.id
        try:
            dbSession.delete(res)
            dbSession.commit()
        except:
            dbSession.rollback()
        res=dbSession.query(ThngsProjs).filter(ThngsProjs.idProj==id).all()
        try:
            dbSession.delete(res)
            dbSession.commit()
        except:
            dbSession.rollback()
        res=dbSession.query(Students).filter(Students.projectId==projectId).all()
        for r in res:
            r.projectId=None
            try:
                dbSession.add(r)
                dbSession.commit()
            except:
                dbSession.rollback()
        return redirect(url_for('start'))
    else:
        project=dbSession.query(Projects).filter(Projects.id==projectId).one()
        return render_template('delete.html',project=project)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    # app.run()
