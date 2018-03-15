# IMPORTS FOR WEB FUNCTIONALITY
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash

# IMPORTS FOR DATABASE CONNECTION AND OPERATIONS
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

# [Anti Forge] Imports needed
from flask import session as login_session
import random
import string

# IMPORTS FOR GOOGLE CONNECT RESPONSE
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Flow from client secrets stores client information in JSON file,
# this gets the JSON file
CLIENT_ID = json.loads(
    # client_secrets.json is from google dev website!
    # It's important to use the same APPname here as in Google
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the
# database and represents a "staging zone" for all the objects
# loaded into the database session object. Any change made against
# the objects in the session won't be persisted into the database
# until you call session.commit(). If you're not happy about the
# changes, you can revert all of them back to the last commit by
# calling session.rollback()
session = DBSession()


# [User Authentication] - Start
# [Anti Forge] - Code needed to generate state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# [Google Oauth] - Server Side function for google connect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token the client sent to the server matches the one
    # server sent to the client
    if request.args.get('state') != login_session['state']:
        # If they don't match it replies ith an error indicating
        # there's a missmatch between the tokens
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        # If there's no error it can proceed
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain one time authorization code from the server
    code = request.data

    try:
        # Upgrade the authorization code into a credentials
        # object generating one time code
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
          json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists. If it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    output += ' 150px;-webkit-border-radius:'
    output += ' 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
# This part is used to disconnect the session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # print 'In gdisconnect access token is %s', access_token
    # print 'User name is: '
    # print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Saving username for later
    user = login_session['username']
    # print 'result is '
    # print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash('User %s Successfully disconnected' % (user))
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid.
        flash('Failed to revoke token for given user.', 400)
        return redirect(url_for('showCatalog'))


# User Helper Functions
# Returns User ID if exists on the database based on email address
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Getting user object with all the info from the database
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# This class creates a user on the database related to login_session parameter
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# [JSON APIs] To view Catalog Information one for items one for categories
@app.route('/catalog/categories/JSON')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/catalog/<category_name>/items/JSON')
def showItemsJSON(category_name):
    items = session.query(Item).all()
    iCat = session.query(Category).filter_by(name=category_name).one()
    result = [i.serialize for i in items if i.category_id == iCat.id]
    return jsonify(Items=result)


# [Page Building] - Start
# Show Catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.id))
    items = session.query(Item).order_by(desc(Item.id)).limit(5)
    # If user is not in the userlist, returns public html file
    if 'username' not in login_session:
        return render_template('catalogpublic.html',
                               categories=categories, items=items)
    return render_template('catalog.html', categories=categories,
                           items=items,
                           login_session=login_session)


# Show Items in Category
@app.route('/catalog/<category_name>/items/')
def showCategoryItems(category_name):
    # Queries the database for categories and items
    categories = session.query(Category).order_by(asc(Category.id))
    itemCategory = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
      category_id=itemCategory.id).all()
    # If user is not in the userlist, returns public html file
    if 'username' not in login_session:
        return render_template('itemspublic.html', categories=categories,
                               items=items, category_name=category_name)
    return render_template('items.html', categories=categories,
                           items=items, category_name=category_name,
                           login_session=login_session)


# Add Item in Catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    # Checking the user is logged in, if not user is redirected to login screen
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # If Category doesn't exist, doesn't create Item
        try:
            itemCategory = session.query(Category).filter_by(
              name=request.form['category']).one()
        except:
            flash('Category does not exist!')
            return render_template('newitem.html', login_session=login_session)
        # Creates Item
        # Getting username for adding it to the table
        uname = login_session['username']
        itemUser = session.query(User).filter_by(name=uname).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=itemCategory.id,
                       user_id=itemUser.id)
        session.add(newItem)
        flash('New Item %s Successfully Created' % (newItem.name))
        session.commit()
        # return render_template('newitem.html')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html',
                               login_session=login_session)


# Edit Item in catalog
@app.route('/catalog/<category>/<item>/edit', methods=['GET', 'POST'])
def editItem(category, item):
    itemCategory = session.query(Category).filter_by(
      name=category).one()
    itemInfo = session.query(Item).filter_by(
      name=item).filter_by(category_id=itemCategory.id).one()
    # If user is not in the userlist, returns public html file
    if 'username' not in login_session:
        return render_template('catalogpublic.html')
    # If the user saves the changes:
    uname = login_session['username']
    itemUser = session.query(User).filter_by(
      name=uname).one()
    if request.method == 'POST':
        # Checking if the user who's editing is the user who created the item
        if itemUser.id != itemInfo.user_id:
            flash('Only the user who created the item can edit it')
            return render_template('edititem.html',
                                   category=itemInfo.category.name,
                                   item=itemInfo,
                                   login_session=login_session)
        if request.form['name']:
            itemInfo.name = request.form['name']
        if request.form['description']:
            itemInfo.description = request.form['description']
        session.add(itemInfo)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showItemInfor', category=itemInfo.category,
                                item=itemInfo.name,
                                login_session=login_session))
    else:
        return render_template('edititem.html',
                               category=itemInfo.category.name, item=itemInfo,
                               login_session=login_session)


# Delete Item in catalog
@app.route('/catalog/<category>/<item>/delete', methods=['GET', 'POST'])
def deleteItem(category, item):
    # Checking the user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    uname = login_session['username']
    itemCategory = session.query(Category).filter_by(
      name=category).one()
    itemToDelete = session.query(Item).filter_by(
      name=item).filter_by(category_id=itemCategory.id).one()
    # taking username of the loged user
    itemUser = session.query(User).filter_by(
      name=uname).one()
    if itemUser.id != itemToDelete.user_id:
        flash('Only the user who created the item can delete it')
        return render_template('itemInfo.html',
                               category=itemToDelete.category.name,
                               item=itemToDelete,
                               login_session=login_session)
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s has been successfully deleted' % itemToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteitem.html',
                               category=itemToDelete.category.name,
                               item=itemToDelete, login_session=login_session)


# Show Item information
@app.route('/catalog/<category>/<item>/')
def showItemInfor(category, item):
    # Using try because there can be items with same name
    # and different categories, if this happens, the except
    # takes the correct item from the category. Query economy!
    try:
        itemInfo = session.query(Item).filter_by(name=item).one()
    except:
        itemCategory = session.query(Category).filter_by(
          name=category).one()
        itemInfo = session.query(Item).filter_by(
          name=item).filter_by(category_id=itemCategory.id).one()
    # If user is not in the userlist, returns public html file
    if 'username' not in login_session:
        return render_template('iteminfopublic.html',
                               category=category, item=itemInfo)
    return render_template('iteminfo.html', category=category,
                           item=itemInfo, login_session=login_session)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
