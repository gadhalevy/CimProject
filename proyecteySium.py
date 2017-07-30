__author__ = 'gadh'
from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,ThngsProjs, Types,Things,Projects,Students
import string
app = Flask(__name__)


engine = create_engine('sqlite:///nisayon.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def start():
    return redirect(url_for('fillProjects'))

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
        # session.add(Students(id=count,name=first+' '+last,projectId=1)) #Hebrew try fix later
        try:
            session.add(Students(id=count,name=first+' '+last,projectId=1)) #Hebrew try fix later
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
    if request.method == 'POST':
        name=request.form['pName']
        teur=request.form['pDesc']
        project = Projects(name=name,teur=teur)
        try:
            session.add(project)
            session.commit()
        except:
            session.rollback()
        return redirect(url_for('newGroup',pName=name,pDesc=teur))
    else:
        return render_template('newProject.html')

@app.route('/newGroup/<string:pName>/<string:pDesc>',methods=['GET','POST'])
def newGroup(pName,pDesc):
    if request.method == 'POST':
        vals=request.form.getlist('talmid')
        return redirect(url_for('newGear',vals=vals,pName=pName))
    else:
        students=session.query(Students).all()
        return render_template('newGroup.html',pName=pName,pDesc=pDesc,students=students)

@app.route('/newGear/<string:vals>/<string:pName>',methods=['GET','POST'])
def newGear(vals,pName):
    if request.method=='POST':
        pass
    else:
        print vals
        s1,s2=vals.split(',')
        indx=s1.find('\\')
        s1=s1[3:indx]
        indx=s2.find('\\')
        s2=s2[3:indx]

        return render_template('newGear.html',s1=s1,s2=s2,pName=pName)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

