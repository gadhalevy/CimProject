__author__ = 'gadh'
from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,ThngsProjs, Types,Things,Projects,Students
from flask_bootstrap import Bootstrap
from forms import NewProj
app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'development key'

engine = create_engine('sqlite:///nisayon.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def start():
    rep=session.query(Projects.name,Students.name,Things.name).join(Students,ThngsProjs).\
        filter(Students.projectId!=1).\
        filter(Things.id==ThngsProjs.idThings).\
        all()
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
    return render_template('report.html',rep=lst)

@app.route('/fillThings')
def fillThings():
    'Include types of things'
    try:
        session.query(Types).delete()
        session.query(Things).delete()
        session.commit()
    except:
        session.rollback()
        return 'Types were not deleted'
    robot=Types(id=1,name='robot')
    lego=Types(id=2,name='lego')
    tablet=Types(id=3,name='tablet')
    for i in robot,lego,tablet:
        session.add(i)
    session.commit()
    legoNames=('Arafat1','Bibi2','Sara3')
    for l in range(len(legoNames)):
        sug=Things(id=l,name=legoNames[l],types=lego)
        r=Things(id=l+len(legoNames),name='r%s' %str(l+len(legoNames)) ,types=robot)
        t=Things(id=l+2*len(legoNames),name='t%s' %str(l+2*len(legoNames)) ,types=tablet)
        session.add(sug)
        session.add(r)
        session.add(t)
        session.commit()
    return 'Done'

@app.route('/fillStudent')
def fillStudent():
    session.rollback()
    try:
        damy=Projects(id=1,name='dumy',teur='Stam lhazana')
        session.add(damy)
        session.commit()
    except:
        session.rollback()
    f=open('engStudents.csv','r')
    txt=f.read()
    lines=txt.split('\n')
    f.close()
    count=1
    for l in lines[:-1]:
        id,first,last=l.split(',')
        print count,first+' '+last
        try:
            session.add(Students(id=count,name=first+' '+last)) #Hebrew try fix later
            session.commit()
        except:
            session.rollback()
        count+=1
    q=session.query(Students).all()
    output = ''
    for i in q:
        output += i.name
        output += '</br>'
    return output
    # return 'Students were created in DB'

@app.route('/fillProject',methods=['GET','POST'])
def fillProjects():
    form=NewProj()
    if request.method == 'POST':
        name=form.name.data
        teur=form.teur.data
        project = Projects(name=name,teur=teur)
        try:
            session.add(project)
            session.commit()
        except:
            session.rollback()
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
                for s in session.query(Students).filter(Students.name.startswith(l[:5])):
                    s.projectId=id
                session.commit()
            except:
                session.rollback()
        print 'PName=',pName,'id=',id
        return redirect(url_for('newGear',vals=vals,pName=pName,id=id))
    else:
        students=session.query(Students).all()
        return render_template('newGroup.html',pName=pName,pDesc=pDesc,students=students)

@app.route('/newGear/<string:vals>/<string:pName>/<int:id>',methods=['GET','POST'])
def newGear(vals,pName,id):
    lst=mySplit(vals)
    rhivim=[]
    if request.method=='POST':
        dvarim=request.form.getlist('davar')
        print dvarim
        for d in dvarim:
            thingInProj=ThngsProjs(idThings=d,idProj=id)
            try:
                session.add(thingInProj)
                for s in session.query(Things.name).filter(Things.id=='%s' %d):
                    rhivim.append(s)
                session.commit()
            except:
                session.rollback()
        print 'rhivim=',rhivim
        return render_template('sikum.html',dvarim=rhivim,pName=pName,vals=vals,lst=lst)
    else:
        things=session.query(Things).all()
        return render_template('newGear.html',vals=vals,lst=lst,pName=pName,things=things)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

