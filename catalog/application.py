from flask import Flask, render_template, request, redirect, jsonify, \
  url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from werkzeug.contrib.atom import AtomFeed
import dicttoxml
from xml.dom.minidom import parseString
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/catalogApp/catalog/client_secret.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catal0g@localhost/catalog')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = ''.join(
      random.choice(string.ascii_uppercase + string.digits)
      for x in xrange(32)
      )

    login_session['state'] = state

    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('/var/www/catalogApp/catalog/client_secret.json', scope='')
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                   connected.'), 200)
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

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])

    if user_id is None:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
              -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"

    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
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
        response = make_response(json.dumps('Current user not \
                    connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # response = make_response(json.dumps('Successfully \
        #                          disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        # return response
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(json.dumps('Failed to revoke \
                                 token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Get All Categories
def getAllCategories():
    return session.query(Category).order_by(asc(Category.name))


# Get latest X items
def getLatestXItems(item_count):
    """
    getLatestXItems: get the latest X items
    Args:
        item_count (int): specifies the count of items requested
    """
    return session.query(Item) \
            .order_by(desc(Item.date_added)) \
            .limit(item_count)


# Show Catalog
@app.route('/')
def showCatalog():
    categories = getAllCategories()
    latest_items = getLatestXItems(9)
    return render_template('catalog.html', categories=categories,
                           latest_items=latest_items,
                           username=login_session.get('username'))


# Decorator function for checking if user is logged in and
# redirecting to login page if not
def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decoratedFunction


# Checks if the user is authorized to Edit/Delete a given item
def isAuthorized(item_user_id, session_user_id):
    if item_user_id != session_user_id:
        return "<script>function myFunction() { alert('You are not \
            authorized to edit or delete this item. You can only \
            edit or delete your own item.');}</script> \
            <body onload='myFunction()'>"
    else:
        return True


# Show Category Items
@app.route('/catalog/<string:category_name>/items')
def showCategoryItems(category_name):
    """
    showCategoryItems: returns items for requested category
    Args:
        category_name (str): the category to fetch items from
    """
    categories = getAllCategories()
    selected_category = session.query(Category) \
        .filter_by(name=category_name) \
        .one()
    category_items = session.query(Item) \
        .filter_by(cat_id=selected_category.id) \
        .order_by(asc(Item.title)) \
        .all()

    return render_template('categoryItems.html',
                           categories=categories,
                           selected_category=selected_category,
                           item_count=len(category_items),
                           category_items=category_items,
                           username=login_session.get('username'))


# Show Item Details
@app.route('/catalog/<string:category_name>/<string:item_title>')
def showItemDetails(category_name, item_title):
    """
    showItemDetails: returns details of an item
    Args:
        category_name (str): category of the item
        item_title (str): item title
    """
    selected_category = session.query(Category) \
        .filter_by(name=category_name) \
        .one()

    selected_item = session.query(Item) \
        .filter_by(title=item_title, cat_id=selected_category.id) \
        .one()

    return render_template('itemDetail.html',
                           item=selected_item,
                           username=login_session.get('username'))


# Add a new category item
@app.route('/catalog/item/add', methods=['GET', 'POST'])
@loginRequired
def addItem():
    """
    addItem: adds an item
    """
    if request.method == 'POST':
            newItem = Item(
                      title=request.form['title'],
                      description=request.form['description'],
                      cat_id=request.form['category_id'],
                      user_id=login_session['user_id'])
            session.add(newItem)
            flash('New Item %s Successfully Added' % newItem.title)
            session.commit()
            return redirect(url_for('showCatalog'))
    else:
            categories = getAllCategories()
            return render_template('addItem.html', categories=categories,
                                   username=login_session.get('username'))


# Edit a category item
@app.route('/catalog/<string:category_name>/<string:item_title>/edit',
           methods=['GET', 'POST'])
@loginRequired
def editItem(category_name, item_title):
    """
    editItem: edit an item
    Args:
        category_name (str): category of the item to edit
        item_title (str): title of the item to edit
    """
    selected_category = session.query(Category) \
        .filter_by(name=category_name) \
        .one()

    itemToEdit = session.query(Item) \
        .filter_by(title=item_title, cat_id=selected_category.id) \
        .one()

    if isAuthorized(itemToEdit.user_id, login_session['user_id']):
        if request.method == 'POST':
            itemToEdit.title = request.form['title']
            itemToEdit.description = request.form['description']
            itemToEdit.cat_id = request.form['category_id']
            user_id = login_session['user_id']
            session.add(itemToEdit)
            flash('Item %s Successfully Edited' % itemToEdit.title)
            session.commit()
            return redirect(url_for('showItemDetails',
                            category_name=itemToEdit.category.name,
                            item_title=itemToEdit.title))
        else:
            categories = getAllCategories()
            return render_template('editItem.html',
                                   categories=categories,
                                   item=itemToEdit,
                                   username=login_session.get('username'))


# Delete a category item
@app.route('/catalog/<string:category_name>/<string:item_title>/delete',
           methods=['GET', 'POST'])
@loginRequired
def deleteItem(category_name, item_title):
    """
    deleteItem: delete an item
    Args:
        category_name (str): category of the item to delete
        item_title (str): title of the item to delete
    """
    selected_category = session.query(Category) \
        .filter_by(name=category_name) \
        .one()

    itemToDelete = session.query(Item) \
        .filter_by(title=item_title, cat_id=selected_category.id) \
        .one()

    if isAuthorized(itemToDelete.user_id, login_session['user_id']):
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash('Item %s Successfully Deleted' % itemToDelete.title)
            return redirect(url_for('showCatalog'))
        else:
            return render_template('deleteItem.html',
                                   item=itemToDelete,
                                   username=login_session.get('username'))


# JSON API to view Catalog Information
@app.route('/catalog.json')
def catalogJSON():
    categories = getAllCategories()
    return jsonify(Category=[c.serialize for c in categories])


# XML API to view Catalog Information
@app.route('/catalog.xml')
def catalogXml():
    categories = getAllCategories()
    categoriesJson = {'Category': [c.serialize for c in categories]}
    catalog_root = 'Catalog'

    # Convert Json to Xml
    xml = dicttoxml.dicttoxml(categoriesJson, custom_root=catalog_root,
                              attr_type=False)
    dom = parseString(xml)
    return dom.toprettyxml()


# Atom API to view latest 10 items added to the Catalog
@app.route('/catalog.atom')
def catalogAtom():
    feed = AtomFeed('Catalog',
                    feed_url=request.url)

    latest10Items = getLatestXItems(10)
    item_root = 'Item'

    for item in latest10Items:
        feed.add(item.title,
                 item.description,
                 content_type='text',
                 author=item.user.name,
                 url=url_for('showItemDetails',
                             category_name=item.category.name,
                             item_title=item.title),
                 updated=item.date_added)

    return feed.get_response()


if __name__ == '__main__':
    app.secret_key = 'now_for_something_completely_different'
    app.debug = True
    app.run(host='ec2-52-27-252-176.us-west-2.compute.amazonaws.com', port=80)
