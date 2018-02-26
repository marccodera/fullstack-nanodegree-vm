# IMPORTS FOR WEB FUNCTIONALITY
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

# IMPORTS FOR DATABASE CONNECTION AND OPERATIONS
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

# [Anti Forge] Imports needed
from flask import session as login_session
import random, string

# IMPORTS FOR GOOGLE CONNECT RESPONSE
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show Catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(Item.id).limit(5)
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    return render_template('catalog.html', categories = categories,
                           items = items)

# Show Items in Category
@app.route('/catalog/<category_name>/items/')
def showCategoryItems(category_name):
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.name))
    itemCategory = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = itemCategory.id).all()
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    return render_template('items.html', categories = categories,
                           items = items)


# Add Item in Catalog
@app.route('/catalog/new/', methods=['GET','POST'])
def newItem():
    # Checking the user is logged in, if not, user is redirected to login screen
    # if 'username' not in login_session:
    #     return redirect('/login')
    response = 'new item'
    return response


# Edit Item in catalog
@app.route('/catalog/<item>/edit', methods=['GET','POST'])
def editItem(item):
    response = 'edit item'
    return response

# Delete Item in catalog
@app.route('/catalog/<item>/delete', methods=['GET','POST'])
def deleteItem(item):
    response = 'delete item: '
    return response


# Show Item information
@app.route('/catalog/<category>/<string:item>/')
def showItemInfor(category, item):
    response = 'show item information'
    return response



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
