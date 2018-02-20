# IMPORTS FOR WEB FUNCTIONALITY
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

# IMPORTS FOR DATABASE CONNECTION AND OPERATIONS
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# from database_setup import Base, Restaurant, MenuItem, User

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

# Show Catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    response = 'show catalog'
    return response


# Show Items in Category
@app.route('/catalog/<category>/items/')
def showCategoryItems(category):
    response = 'show category items in: %s' % category 
    return response


# Add Item in Catalog
@app.route('/catalog/new/', methods=['GET','POST'])
def newItem():
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
