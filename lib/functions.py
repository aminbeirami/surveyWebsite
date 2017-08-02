from lib import mySQLCon as mc
from collections import defaultdict
from lib.config import *
import os

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
CLOUDSQL_DATABASE = os.environ.get('CLOUDSQL_DATABASE') 

def connect_to_DB():
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        db = mc.DataBase(CLOUDSQL_CONNECTION_NAME,CLOUDSQL_USER,CLOUDSQL_PASSWORD,CLOUDSQL_DATABASE,'GCSQL')
    else:
        db = mc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE,'LOCAL')
    return db

def fetch_questions_db():
    db = connect_to_DB()
    sql = "SELECT * FROM questions ORDER BY no"
    results = db.query(sql,None)
    listOfIDs = [x for x,y in results]
    listOfFetchedQuestions = [y for x,y in results]
    return [listOfIDs,listOfFetchedQuestions]

def save_questions_to_DB(question):
    db = connect_to_DB()
    sql = "INSERT INTO questions (questiontext) VALUES (%s)" 
    parameters = (question,)
    db.insert(sql,parameters)
    db.commit()

def save_answer_to_DB(sessionKey,questionNo,answer): #should be changed
    db = connect_to_DB()
    sql = "INSERT INTO answers (sessionID,questionNo,answer) VALUES (%s, %s, %s)"
    parameters = (sessionKey,questionNo,answer) 
    db.insert(sql,parameters)
    db.commit()

def split_and_save(sessionKey, answers): #should be changed
    for items in range(len(answers)-1):
        questionNo =  int(answers[items][0])
        if answers[items][1] == "Yes":
            save_answer_to_DB(sessionKey, questionNo, True)
        else:
            save_answer_to_DB(sessionKey, questionNo, False)

def hashing_and_save(user_list):
    db = connect_to_DB()
    sql = "INSERT INTO users(username,password,isadmin) VALUES(%s,%s,%s)"
    parameters = (user_list[0][1],user_list[1][1],False)
    db.insert(sql,parameters)
    db.commit()

def fetch_username_and_password(username,password):
    db = connect_to_DB()
    sql = "SELECT username, isadmin FROM users WHERE username = (%s) AND password = (%s)"
    arguments = (username,password)
    result = db.query(sql,arguments)
    if result:
        if result[0][1] == 1:
            isadmin = True
        else:
            isadmin = False
        return (True,isadmin)
    else:    
        return (False,False)

def pool_of_answers():
    db = connect_to_DB()
    sql = "SELECT questionNo, answer FROM answers WHERE sessionId IN (SELECT DISTINCT sessionId FROM answers GROUP BY sessionId)"
    results = db.query(sql,None)
    return results

def users_answered():
    db = connect_to_DB()
    sql = "SELECT DISTINCT sessionId FROM answers"
    results = db.query(sql,None)
    return results

def questions_statistics():
    Statistics = []
    dataOfAnswers = list(pool_of_answers())
    dataOfQuestions = fetch_questions_db()
    res = defaultdict(list)
    for v, k in dataOfAnswers: res[v].append(k)
    for elements in range(1, len(dataOfQuestions[0])+1):
        p = [res[elements].count(0), res[elements].count(1)]
        Statistics.append({'id':dataOfQuestions[0][elements-1],'text':dataOfQuestions[1][elements-1],'answers':p})
    return Statistics