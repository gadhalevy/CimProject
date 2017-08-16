from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,ThngsProjs, Types,Things,Projects,Students


engine = create_engine('sqlite:///nisayon.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class NewProj(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    teur=StringField(u'Description', widget=TextArea(),validators=[DataRequired()])
    submit = SubmitField("Define Group")

