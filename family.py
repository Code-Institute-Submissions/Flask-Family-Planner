import os
from flask import Flask, redirect, render_template, request
from random import choice
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_NAME = os.environ.get("MONGODB_NAME")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/login")
def login():
    surname = request.args.get("surname")
    return redirect(surname) 

@app.route("/<surname>")
def get_userpage(surname):
    family_members = load_members_from_mongo(surname)
    return render_template("userpage.html", surname=surname, family_members=family_members)      

@app.route("/<surname>/add_member", methods=["POST"])
def add_member(surname):
    member = request.form.get("member")
    add_member_to_mongo(surname, member)
    return redirect(surname)  
    
@app.route("/<surname>/<family_member>")
def get_family_member(surname, family_member):
    tasks = load_user_tasks_from_mongo(surname, family_member)
    return render_template("member_page.html", tasks=tasks, surname=surname, family_member=family_member)

@app.route("/<surname>/<family_member>/new_task_form")
def render_task_form(surname, family_member):
    return render_template("add_task.html", surname=surname, family_member=family_member)
    
@app.route("/<surname>/<family_member>/submit_form", methods=["POST"])
def add_task(surname,family_member):
    task_name = request.form.get("task_name")
    task_description = request.form.get("task_description")
    due_date = request.form.get("due_date")
    is_urgent = request.form.get("is_urgent")
    task = {"task_name": task_name,
            "task_description": task_description,
            "due_date": due_date,
            "is_urgent": is_urgent
            }
    save_user_tasks_to_mongo(surname, family_member, task)
    return redirect(surname + "/" + family_member)
    
@app.route("/<surname>/<family_member>/<task_id>/delete_task")
def delete_task(surname, family_member, task_id):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        collection = db[surname + "_" + family_member]
        collection.delete_one({ '_id': ObjectId(task_id) })
    return redirect(surname + "/" + family_member)
    
@app.route("/<surname>/<family_member>/<task_id>/edit_task", methods=['GET', 'POST'])
def edit_task(surname, family_member, task_id):
    with MongoClient(MONGODB_URI) as conn:          
        db = conn[MONGODB_NAME]
        item = db[surname+ "_" + family_member].find_one({'_id':ObjectId(task_id)})
    if request.method=="POST":
        item['task_name'] = request.form.get('task_name')
        item['task_description'] = request.form.get('task_description')
        item['due_date'] = request.form.get('due_date')
        item['is_urgent'] = request.form.get('is_urgent')
        with MongoClient(MONGODB_URI) as conn:
            db = conn[MONGODB_NAME]
            db[surname + "_" + family_member].save(item)
            return redirect(surname + "/" + family_member)
    else:
        return render_template("edittask.html", surname=surname, family_member= family_member, task=item)

    
def add_member_to_mongo(surname, family_member):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        db.create_collection(surname + "_" + family_member)
        
def load_members_from_mongo(surname):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        members = db.collection_names()
        return [member.split("_")[1] for member in members if surname == member.split("_")[0]]
            

def load_user_tasks_from_mongo(surname, family_member):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        collection = db[surname + "_" + family_member]
        return collection.find()
        
def save_user_tasks_to_mongo(surname, family_member,task):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        collection = db[surname + "_" + family_member]
        collection.insert(task)




































if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)