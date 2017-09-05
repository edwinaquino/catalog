####################
# Required Imports
####################
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os, random, string, datetime, json, httplib2, requests
# Import login_check from login_decorator.py
from login_decorator import login_check

####################
# Flask instance
####################
app = Flask(__name__)



####################
# DB
####################
# Connect to database
engine = create_engine('sqlite:///wallpapers.db')
Base.metadata.bind = engine
# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()

####################
# GConnect CLIENT_ID
####################
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Wallpaper-Website"


####################
# Wallpaper URLs Routing
####################
# Homepage and default Categories
@app.route('/')
@app.route('/wallpapers/')
def displayCategory():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Wallpapers).order_by(desc(Wallpapers.date)).limit(5)
    return render_template('wallpapers.html',
                            categories = categories,
                            items = items)

# Category Wallpapers
# example: http://localhost:8000/wallpapers/Animal/
@app.route('/wallpapers/<path:category_name>/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Wallpapers).filter_by(category=category).order_by(asc(Wallpapers.name)).all()
    print items
    count = session.query(Wallpapers).filter_by(category=category).count()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('wall_categories_public.html',
                                category = category.name,
                                categories = categories,
                                items = items,
                                count = count)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('wall_categories_private.html',
                                category = category.name,
                                categories = categories,
                                items = items,
                                count = count,
                                user=user)

# Show Wallpaper Details
# example: http://localhost:8000/wallpapers/Animal/Tigers/
@app.route('/wallpapers/<path:category_name>/<path:item_name>/')
def showWallpaper(category_name, item_name):
    wallpaper = session.query(Wallpapers).filter_by(name=item_name).one()
    creator = getUserInfo(wallpaper.user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('wallpaper_public.html',
                                wallpaper = wallpaper,
                                category = category_name,
                                categories = categories,
                                creator = creator)
    else:
        return render_template('wallpaper_private.html',
                                wallpaper = wallpaper,
                                category = category_name,
                                categories = categories,
                                creator = creator)

# * LOGIN REQUIRED *
# Add new category
# http://localhost:8000/wallpapers/addcategory
@app.route('/wallpapers/addcategory', methods=['GET', 'POST'])
@login_check
def addCategory():
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        print newCategory
        session.add(newCategory)
        session.commit()
        flash('[OK] New Category Created!')
        return redirect(url_for('displayCategory'))
    else:
        return render_template('wall_category_add.html')

# Edit a category
@app.route('/wallpapers/<path:category_name>/edit', methods=['GET', 'POST'])
@login_check
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(name=category_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    # See if the logged in user is the owner of wallpaper
    creator = getUserInfo(editedCategory.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != wallpaper owner redirect them
    if creator.id != login_session['user_id']:
        flash ("[ERROR] You are not authorized to edit this category.")
        return redirect(url_for('displayCategory'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash('[Edit Completed] - Wallpaper Category Successfully Edited!')
        return  redirect(url_for('displayCategory'))
    else:
        return render_template('wall_category_edit.html',
                                categories=editedCategory,
                                category = category)

# Delete a category
@app.route('/wallpapers/<path:category_name>/delete', methods=['GET', 'POST'])
@login_check
def deleteCategory(category_name):
    categoryToDelete = session.query(Category).filter_by(name=category_name).one()
    # See if the logged in user is the owner of wallpaper
    creator = getUserInfo(categoryToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != wallpaper owner redirect them
    if creator.id != login_session['user_id']:
        flash ("[ERROR] You are not authorized to delete this category.")
        return redirect(url_for('displayCategory'))
    if request.method =='POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('[OK] Category Deleted! '+categoryToDelete.name)
        return redirect(url_for('displayCategory'))
    else:
        return render_template('wall_category_delete.html',
                                category=categoryToDelete)

# Add an wallpaper
@app.route('/wallpapers/add', methods=['GET', 'POST'])
@login_check
def addWallpaper():
    categories = session.query(Category).all()
    if request.method == 'POST':
        newWallpaper = Wallpapers(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category).filter_by(name=request.form['category']).one(),
            date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(newWallpaper)
        session.commit()
        flash('[OK] Wallpaper Added!')
        return redirect(url_for('displayCategory'))
    else:
        return render_template('wallpaper_add.html',
                                categories=categories)

# Edit an wallpaper
@app.route('/wallpapers/<path:category_name>/<path:item_name>/edit', methods=['GET', 'POST'])
@login_check
def editWallpaper(category_name, item_name):
    editedWallpaper = session.query(Wallpapers).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    # See if the logged in user is the owner of wallpaper
    creator = getUserInfo(editedWallpaper.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != wallpaper owner redirect them
    if creator.id != login_session['user_id']:
        flash ("You cannot edit this wallpaper. This wallpaper belongs to %s" % creator.name)
        return redirect(url_for('displayCategory'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedWallpaper.name = request.form['name']
        if request.form['description']:
            editedWallpaper.description = request.form['description']
        if request.form['picture']:
            editedWallpaper.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form['category']).one()
            editedWallpaper.category = category
        time = datetime.datetime.now()
        editedWallpaper.date = time
        session.add(editedWallpaper)
        session.commit()
        flash('[OK] Wallpaper Category Edited!')
        return  redirect(url_for('showCategory',
                                category_name=editedWallpaper.category.name))
    else:
        return render_template('wallpaper_edit.html',
                                wallpaper=editedWallpaper,
                                categories=categories)

# Delete an wallpaper
@app.route('/wallpapers/<path:category_name>/<path:item_name>/delete', methods=['GET', 'POST'])
@login_check
def deleteWallpaper(category_name, item_name):
    itemToDelete = session.query(Wallpapers).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    # See if the logged in user is the owner of wallpaper
    creator = getUserInfo(itemToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != wallpaper owner redirect them
    if creator.id != login_session['user_id']:
        flash ("You cannot delete this wallpaper. This wallpaper belongs to %s" % creator.name)
        return redirect(url_for('displayCategory'))
    if request.method =='POST':
        session.delete(itemToDelete)
        session.commit()
        flash('[OK] Wallpaper Deleted! '+itemToDelete.name)
        return redirect(url_for('showCategory',
                                category_name=category.name))
    else:
        return render_template('wallpaper_delete.html',
                                wallpaper=itemToDelete)


####################
# Login Routing
####################
# Login - Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('wall_login.html', STATE=state)

# GConnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate  token state
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('[ERROR] Unable to upgrade your authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - (Python3 compatible)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # ERROR: If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for this user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Save access token.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Gather user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user exists, if not, make a new user profile
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '<h1>Congratulations</h1>'
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '</h4>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " class="user_profile_img"> '
    if not login_session['username']:
        # in case user does not have a name in their google profile,
        #show their email
        login_session['username'] = login_session['email']
    flash("You're logged in as %s" % login_session['username'])
    return output

#############################
#Functions for User Helper
#############################

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('displayCategory'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

####################
# JSON
####################
@app.route('/JSON')
def allWallpapersJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Wallpapers)\
                    .filter_by(category_id=category_dict[c]["id"]).all()]
        if items:
            category_dict[c]["Wallpaper"] = items
    return jsonify(Category=category_dict)
# Displays all categories currently in the database
@app.route('/JSON/categories/')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])
# All Wallpapers
@app.route('/JSON/wallpapers/')
def itemsJSON():
    items = session.query(Wallpapers).all()
    return jsonify(items=[i.serialize for i in items])
# ALL wallpapers in a particular category
@app.route('/JSON/categories/<path:category_name>/')
def categoryWallpapersJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Wallpapers).filter_by(category=category).all()
    return jsonify(items=[i.serialize for i in items])
# Specific Wallpaper in its category
@app.route('/JSON/categories/<path:category_name>/<path:item_name>/')
def WallpaperJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    wallpaper = session.query(Wallpapers).filter_by(name=item_name,\
                                        category=category).one()
    return jsonify(wallpaper=[wallpaper.serialize])


# url_for static path processor
# remove when deployed
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# Always at end of file !Important!
if __name__ == '__main__':
    app.secret_key = 'DEV_SECRET_KEY'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
