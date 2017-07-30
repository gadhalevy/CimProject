import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class ThngsProjs(Base):
    __tablename__ = 'thngsprojs'
    idThings = Column(Integer, ForeignKey('things.id'), primary_key=True)
    idProj = Column(Integer, ForeignKey('projects.id'), primary_key=True)

class Types(Base):
    __tablename__ = 'types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class Things(Base):
    __tablename__ = 'things'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    typeId = Column(Integer, ForeignKey('types.id'))
    types = relationship(Types)
    projects=relationship('Projects',secondary='thngsprojs')

class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    teur = Column(String(250), nullable=False)
    things=relationship('Things',secondary='thngsprojs')

class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    projectId = Column(Integer, ForeignKey('projects.id'))
    projects = relationship(Projects)

engine = create_engine('sqlite:///nisayon.db')

Base.metadata.create_all(engine)



