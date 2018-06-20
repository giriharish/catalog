from flask import Flask, render_template, redirect
from flask import request, url_for, flash, jsonify
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import User, Base, Company, Models
app = Flask(__name__)
engine = create_engine('sqlite:///carmodels.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# This is to read client id from client secrets.json file
CLIENT_ID = json.loads(open('client_secrets.json', 'r ').read())[
    'web']['client_id']

# This function triggers when we request url localhost:5000
# This will create a unique to code to handle fake requests
# This will return rendered login template to the client


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# This function call occurs when client send their access token
# This will verify the state token generated in login funtion


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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

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
    # After getting information from user it will
    # store data in login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check for user in database if user exists
    # Stores the user id in login session else
    # Create user with details and the stores the user_id
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    print "done!"
    return output

# This is to logout the user


@app.route('/logout')
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print('User name is: ')
    print login_session['username']
    print(login_session['access_token'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect('/')
    else:
        response = make_response(json.dumps(
            'Failed to revoke token delete cookies and re login.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# This function is to insert user data into database and return userid
def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    session.close()
    return user.id

# This function takes emails and checks whether user exits
# if exits return user id else return none


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except:
        return None

# This function shows all companies to client


@app.route('/')
def ShowCompanies():
    session = DBSession()
    companies = session.query(Company).all()
    latestmodels = session.query(Models).filter_by(year=2018).all()
    session.close()
    return render_template('main.html', companies=companies,
                           log_sess=login_session, LModels=latestmodels)

# This function is to view all models in a company


@app.route('/company/<int:c_id>/')
def showCompanyModels(c_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    models = session.query(Models).filter_by(company_id=c_id).all()
    session.close()
    return render_template('showComModels.html',
                           company=company,
                           models=models,
                           log_sess=login_session)


@app.route('/company/new/', methods=['POST', 'GET'])
def CreateCompany():
    if 'username' in login_session:
        if request.method == 'POST':
            session = DBSession()
            newc = Company(name=request.form['cname'],
                           user_id=login_session['user_id'])
            session.add(newc)
            session.commit()
            session.close()
            flash('New Company added')
            return redirect('/')
        else:
            return render_template('addCompany.html', log_sess=login_session)
    else:
        flash('login to proceed')
        return redirect('/login')

# This function is to create new model


@app.route('/company/<int:c_id>/model/new', methods=['POST', 'GET'])
def CreateModel(c_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == company.user_id:
            if request.method == 'POST':
                newModel = Models(name=request.form['Mname'],
                                  description=request.form['description'],
                                  price=request.form['mprice'],
                                  cc=request.form['cc'],
                                  image=request.form['mimage'],
                                  year=request.form['myear'],
                                  colors=request.form['mcolors'],
                                  company_id=c_id,
                                  user_id=login_session['user_id'])
                session.add(newModel)
                session.commit()
                session.close()
                flash('%s added' % request.form['Mname'])
                return redirect(url_for('showCompanyModels', c_id=c_id))
            else:
                company = session.query(Company).filter_by(id=c_id).one()
                session.close()
                return render_template('addmodel.html',
                                       comp=company,
                                       log_sess=login_session)
        else:
            flash('You are not autherized add model ')
            return redirect('/')
    else:
        flash('login to proceed')
        return redirect('/login')

# this function is to edit company name


@app.route('/company/<int:c_id>/edit', methods=['POST', 'GET'])
def editCompany(c_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == company.user_id:
            if request.method == 'POST':
                getcomp = session.query(Company).filter_by(id=c_id).one()
                getcomp.name = request.form['cname']
                session.add(getcomp)
                session.commit()
                session.close()
                flash('Company name modified')
                return redirect('/')
            else:
                company = session.query(Company).filter_by(id=c_id).one()
                session.close()
                return render_template('editCompany.html',
                                       comp=company,
                                       log_sess=login_session)
        else:
            flash('You are not autherized to edit company')
            return redirect('/')
    else:
        flash('login to proceed')
        return redirect('/login')

# This function is to edit model


@app.route('/company/<int:c_id>/model/<int:model_id>/edit',
           methods=['POST', 'GET'])
def editModel(c_id, model_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == company.user_id:
            if request.method == 'POST':
                model = session.query(Models).filter_by(id=model_id).one()
                model.name = request.form['Mname']
                model.year = request.form['myear']
                model.price = request.form['mprice']
                model.cc = request.form['cc']
                model.image = request.form['mimage']
                model.colors = request.form['mcolors']
                model.description = request.form['description']
                session.add(model)
                session.commit()
                session.close()
                flash("Model edited")
                return redirect(url_for('viewModel',
                                        c_id=c_id,
                                        model_id=model_id))
            else:
                model = session.query(Models).filter_by(id=model_id).one()
                session.close()
                return render_template('editModel.html',
                                       model=model,
                                       log_sess=login_session)
        else:
            flash('You are not autherized to edit model')
            return redirect('/')
    else:
        flash('login to proceed')
        return redirect('/login')

# This function is to delete company


@app.route('/company/<int:c_id>/delete', methods=['POST', 'GET'])
def deleteCompany(c_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == company.user_id:
            if request.method == 'POST':
                company = session.query(Company).filter_by(id=c_id).one()
                c = session.query(Models).filter_by(company_id=c_id).all()
                for cm in c:
                    session.delete(cm)
                session.delete(company)
                session.commit()
                flash('Company deleted')
                session.close()
                return redirect('/')
            else:
                company = session.query(Company).filter_by(id=c_id).one()
                session.close()
                return render_template('CdeletePrompt.html',
                                       comp=company,
                                       log_sess=login_session)
        else:
            flash('You are not autherized to delete')
            return redirect('/')
    else:
        flash('login to proceed')
        return redirect('/login')

# This function is to delete model based on id


@app.route('/company/<int:c_id>/model/<int:model_id>/delete',
           methods=['POST', 'GET'])
def deleteModel(c_id, model_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == company.user_id:
            if request.method == 'POST':
                session = DBSession()
                model = session.query(Models).filter_by(id=model_id).one()
                session.delete(model)
                session.commit()
                flash("Model deleted")
                session.close()
                return redirect(url_for('showCompanyModels', c_id=c_id))
            else:
                session = DBSession()
                model = session.query(Models).filter_by(id=model_id).one()
                session.close()
                return render_template('deleteModel.html',
                                       model=model,
                                       log_sess=login_session)
        else:
            flash('You are not autherized to delete model')
            return redirect('/')
    else:
        flash('login to proceed')
        return redirect('/login')

# This function will renders the details of model


@app.route('/company/<int:c_id>/model/<int:model_id>/')
def viewModel(c_id, model_id):
    session = DBSession()
    model = session.query(Models).filter_by(id=model_id).one()
    session.close()
    return render_template('viewModel.html',
                           model=model,
                           log_sess=login_session)

# This api end point returns Company details along its model details


@app.route('/json')
def createjson():
    session = DBSession()
    companies = []
    company = session.query(Company).all()
    for c in company:
        models = []
        modls = session.query(Models).filter_by(company_id=c.id).all()
        for m in modls:
            models.append(m.serialize)
        ob = {
            'id': c.id,
            'name': c.name,
            'models': models
        }
        companies.append(ob)
        session.close()
        print(jsonify(companies))
    return jsonify(companies=companies)

# This will return company models


@app.route('/company/<int:c_id>/json')
def companyModelsjson(c_id):
    session = DBSession()
    company = session.query(Company).filter_by(id=c_id)
    modls = session.query(Models).filter_by(company_id=c_id).all()
    session.close()
    return jsonify(CompanyModels=[i.serialize for i in modls])

# This will return the model details as json


@app.route('/company/<int:c_id>/model/<int:model_id>/json')
def Modelsjson(c_id, model_id):
    session = DBSession()
    modl = session.query(Models).filter_by(id=model_id).one()
    session.close()
    return jsonify(Model=modl.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
