# IMPORTS FOR WEB FUNCTIONALITY
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

# IMPORTS FOR DATABASE CONNECTION AND OPERATIONS
from sqlalchemy import create_engine, asc, desc
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
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Show Catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.id))
    items = session.query(Item).order_by(desc(Item.id)).limit(5)
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    return render_template('catalog.html', categories = categories,
                           items = items)

# Show Items in Category
@app.route('/catalog/<category_name>/items/')
def showCategoryItems(category_name):
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.id))
    itemCategory = session.query(Category).filter_by(
      name = category_name).one()
    items = session.query(Item).filter_by(
      category_id = itemCategory.id).all()
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    return render_template('items.html', categories = categories,
      items = items, category_name = category_name)


# Add Item in Catalog
@app.route('/catalog/new/', methods=['GET','POST'])
def newItem():
    # Checking the user is logged in, if not, user is redirected to login screen
    # if 'username' not in login_session:
    #     return redirect('/login')

    # After implementing user control uncomment this!!!!!!!
    # itemUser = session.query(User).filter_by(
    #  name = username).one()
    if request.method == 'POST':
        # If Category doesn't exist, doesn't create Item
        try:
            itemCategory = session.query(Category).filter_by(
              name = request.form['category']).one()
        except:
            flash('Category does not exist!')
            return render_template('newitem.html')
        # Creates Item
        newItem = Item(name = request.form['name'],
          description = request.form['description'],
          category_id = itemCategory.id, 
          user_id = 1)
        session.add(newItem)
        flash('New Item %s Successfully Created' % (newItem.name))
        session.commit()
        #return render_template('newitem.html')
        return redirect(url_for('showCatalog'))
    else:
       return render_template('newitem.html')


# Edit Item in catalog
@app.route('/catalog/<category>/<item>/edit', methods=['GET','POST'])
def editItem(category, item):
    itemCategory = session.query(Category).filter_by(
      name = category).one()
    itemInfo = session.query(Item).filter_by(
      name = item).filter_by(category_id = itemCategory.id).one()
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    if request.method == 'POST':
        if request.form['name']:
            itemInfo.name = request.form['name']
        if request.form['description']:
            itemInfo.description = request.form['description']
        session.add(itemInfo)
        session.commit() 
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showItemInfor', 
          category =itemInfo.category, item = itemInfo.name))
    else:
        return render_template('edititem.html', 
          category = itemInfo.category.name, item = itemInfo)

# Delete Item in catalog
@app.route('/catalog/<item>/delete', methods=['GET','POST'])
def deleteItem(item):
    response = 'delete item: '
    return response


# Show Item information
@app.route('/catalog/<category>/<item>/')
def showItemInfor(category, item):
    # Using try because there can be items with same name
    # and different categories, if this happens, the except
    # takes the correct item from the category. Query economy!
    try:
        itemInfo = session.query(Item).filter_by(name = item).one()
    except:
        itemCategory = session.query(Category).filter_by(
          name = category).one()
        itemInfo = session.query(Item).filter_by(
          name = item).filter_by(category_id = itemCategory.id).one()
    # If user is not in the userlist, returns public html file
    # if 'username' not in login_session:
    #     return render_template('publiccatalog.html', categories = categories)
    return render_template('iteminfo.html', category = category,
                           item = itemInfo)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
