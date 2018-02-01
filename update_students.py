#!/usr/bin/python

import psycopg2
import csv

TRUNCATE = False  # When set to True, the current table will be cleaned before insertion, but it's very slow..


def extract(path='engStudents.csv'):
    '''
    Loads students from csv
    :param path: path for the csv file
    :return: list of students
    '''
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        lst = list(reader)
    return lst

def transform(lst):
    '''
    Transforms the student list
    :param lst: student list
    :return: list of tuples 
    '''
    return map(lambda x: (x[1]+" "+x[2],x[0]),lst)

def load(lst):
    '''
    Loads the students into Postgres
    :param lst: list of students 
    :return: None
    '''
    # TODO: hide secrets
    conn = psycopg2.connect(host='ec2-107-21-109-15.compute-1.amazonaws.com',database="dbl74bp8g6al84",user="wgbgkgefrjzdgo", password="24339a1a159f7ec5c37bd6aef78ee8dec218f76110ab98aead9631fb1becdf8c")
    print "Opened database successfully"
    cur = conn.cursor()
    if TRUNCATE:
        cur.execute('TRUNCATE TABLE students RESTART IDENTITY;;')
        print "table truncated successfully"
        conn.commit()
    for student in lst:
        # TODO: Fix "insert violates foreign key constraint (projectId)=(2) is not present in table projects"
        #cur.execute('INSERT INTO students (name, "projectId") VALUES(\'{}\',{});'.format(student[0], student[1]))
        cur.execute('INSERT INTO students (name, "projectId") VALUES(\'{}\',NULL);'.format(student[0]))
    conn.commit()
    print "Records created successfully"
    conn.close()


load(transform(extract()))