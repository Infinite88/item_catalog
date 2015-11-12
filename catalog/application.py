import random
import string
import httplib2
import json
import requests
from dicttoxml import dicttoxml
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask import make_response
from flask import session as login_session
from flask import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import flask
from flask.ext.seasurf import SeaSurf

app = Flask(__name__)
csrf = SeaSurf(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Project"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@csrf.exempt
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

'''---------- Authenincation----------'''
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;/-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).get(user_id)
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function

# DISCONNECT - Revoke a current user's token and reset their login_session
@csrf.exempt
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials.access_token')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

'''--------- API ENDPOINTS ----------'''
# Show JSON
@app.route('/category/<int:category_id>/item/JSON')
def catalogItemJSON(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category_id)
	return jsonify(CategoryItem=[i.serialize for i in items])

# Converts JSON into XML
@app.route('/category/<int:category_id>/item/XML')
def catalogItemXML(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category_id)
    xml = dicttoxml(i.serialize for i in items)
    return Response(xml, mimetype='text/xml')
    

# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    '''
    Accesses the database and finds the table that correspnds with the
    Category and finds all the entries for it, then returns them
     '''
    categories = session.query(Category).all()
    # return "This page will show all my catagories"
    return render_template('categories.html', categories=categories)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    '''
    This function creates new new category items.
    Looks for a post request and then extracts the name.
    Adds newCategory and commits to the database.
    '''
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'], image=request.form['image'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    '''
    Accesses Category to table and grabs one. 
    '''
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            editedCategory.image = request.form['image']
            return redirect(url_for('showCategories'))
    else:
        return render_template(
            'editCategory.html', category=editedCategory)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    '''
    Deletes category from the database
    '''
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(
            url_for('showCategories', category_id=category_id))
    else:
        return render_template(
            'deleteCategory.html', category=categoryToDelete)


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def showCatalogItem(category_id):
    '''
    Accesses the database and finds the table that correspnds with the
    Category and finds all the entries for it, then returns them.
    '''
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category_id)
    return render_template('items.html', category=category, items=items, category_id=category_id)

@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
@login_required
def newCatItem(category_id):
    '''
    This function creates new new category items.
    Looks for a post request and then extracts the name, description,
    price, and image. Adds newItem and commits to the database.
    '''
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], image=request.form['image'], category_id=category_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template('newitems.html', category_id=category_id) 

@app.route('/category/<int:category_id>/<int:item_id>/edit/', 
            methods=['GET', 'POST'])
@login_required
def editCatItem(category_id, item_id):
    '''
    This functions purpose is to edit category items
    and updating the database.
    inputs:
        :Input_1: Name of the Item
        :Input_2: Description of the item
        :Input_3: Price of the item
        :Input_4: Image of the item
    '''
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            editedItem.image = request.form['image']
            editedItem.description = request.form['description']
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('Item has been edited')
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template(
            'edititem.html', category_id=category_id, item_id=item_id, item=editedItem)

@app.route('/category/<int:category_id>/<int:item_id>/delete/', 
            methods=['GET', 'POST'])
@login_required
def deleteCatItem(category_id, item_id):
    '''
    This function deletes the category item from the database.
    '''
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item has been deleted')
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template('deleteitem.html', category_id=category_id,
                            item_id=item_id, item=itemToDelete)

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)