import random
import string
import httplib2
import json
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MangaDB, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://godfrey:Per167*Fect@postgresql-rectangular-25232)/manga'

engine = create_engine('postgresql://godfrey:Per167*Fect@localhost:5432/manga')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

secret_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = "Manga"

# validating current loggedin user


def createUser():
    name = login_session['name']
    email = login_session['email']
    picture = login_session['picture']
    provider = login_session['provider']
    newUser = User(name=name, email=email, picture=picture, provider=provider)
    session.add(newUser)
    session.commit()


def check_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# retrieve admin user details

def check_admin():
    return session.query(User).filter_by(
        email='sagar.choudhary96@gmail.com').one_or_none()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'provider' in login_session and login_session['provider'] == 'null':
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/gconnect', methods=['POST'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'),
                               401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data
    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade the
        authorisation code"""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = access_token
    login_session['id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['name'] = data['name']
    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not check_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])


# logout user

@app.route('/logout')
def logout():

    # Disconnect based on provider

    if login_session.get('provider') == 'google':
        gdisconnect()
    return redirect(url_for('index'))


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token

        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


def queryAllManga():
    return session.query(MangaDB).all()


@app.route('/')
@app.route('/manga/')
def index():
    manga = session.query(MangaDB).order_by(MangaDB.name)
    return render_template('home.html', manga=manga, login_session=login_session)


@app.route('/manga/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        mangaItem = MangaDB(name=request.form['name'], authorName=request.form['authorName'],
                            image=request.form['image'], description=request.form['description'],
                            genre=request.form['genre'], user_id=1)
        session.add(mangaItem)
        session.commit()
        flash('Item Successfully Added!')
        return redirect(url_for('index'))
    return render_template('newItem.html')

@app.route('/manga/genre/<string:genre>/')
def sortManga(genre):
    manga = session.query(MangaDB).filter_by(genre=genre).all()
    return render_template('home.html', manga=manga, currentPage='home')


@app.route('/manga/genre/<string:genre>/<string:name>/edit', methods=['GET', 'POST'])
@login_required
def editItem(name, genre):
    manga = session.query(MangaDB).filter_by(name=name, genre=genre).first()

    if request.method == 'POST':
        if request.form['name']:
            manga.name = request.form['name']
        if request.form['authorName']:
            manga.description = request.form['authorName']
        if request.form['image']:
            manga.image = request.form['image']
        if request.form['description']:
            manga.description = request.form['description']
        if request.form['genre']:
            manga.description = request.form['genre']
        session.add(manga)
        session.commit()
        flash('Item Successfully Edited!')
        return redirect(url_for('itemInfo', name=manga.name))
    return render_template('editItem.html', manga=manga)


@app.route('/manga/genre/<string:genre>/<string:name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(name, genre):
    manga = session.query(MangaDB).filter_by(name=name, genre=genre).first()
    if request.method == 'POST':
        session.delete(manga)
        session.commit()
        flash('Item Successfully Been Deleted!')
        return redirect(url_for('index'))
    return render_template('deleteItem.html', manga=manga)


@app.route('/manga/genre/<string:genre>/<string:name>')
def itemInfo(name, genre):
    manga = session.query(MangaDB).filter_by(name=name, genre=genre).first()
    return render_template('itemInfo.html', manga=manga, currentPage='info')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)

