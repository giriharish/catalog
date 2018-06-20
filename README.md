# Catalog
  This is the Udacity Full Stack Web Development project #4
  
  
## About
   This is web application build with python framework flask.This is the informative web app
   which gives information about car models in market
   
   
## Requirements
  - python
  - Flask
  - SQLAlchemy
  - Oauth2client
  - requests
  - Virtualenc
  

  run pip install -r requirements.txt to install all dependencies.
  
## How to run server
  In order to run this server you need to install python(2.7) or higher in your machine(linux/windows).


  It is recommended to use vagrant for testing .This will not effect your machine configurations.
  Here is [documentation](https://www.vagrantup.com/docs/) to install vagrant and [virtual box](https://www.virtualbox.org/wiki/Documentation) 
  
  
  The entry point for this project is project.py
  run this file using
  ```
  $python project.py
  
  ```
  After this if all goes well access your web application from [http://localhost:5000](http://localhost:5000)
## Files in this project
  ```
  catalog
  ├── client_secrets.json
  ├── db_setup.py
  ├── carmodels.db
  ├── static
  │   └── style.css
  ├── templates
  │   ├── addCompany.html
  │   ├── addmodel.html
  │   ├── CdeletePrompt.html
  │   ├── deleteModel.html
  │   ├── editCompany.html
  │   ├── editModel.html
  │   ├── head.html
  │   ├── login.html
  │   ├── main.html
  │   ├── showComModels.html
  │   └── viewModel.html
  ├── project.py
  ├── requirements.txt
  └── README.md
  ```
  - client_secrets.json file contains oauth2 info.
  - db_setup.py is the database setup file which create tables in the sqllite database using sqlalchemy
  - carmodels.db is the sqllite database file
  - static folder contains the static files such as css,javascript,images etc.
  - templates folder contains the html files which is used to render data
  - requirements.txt contains all the require modules
  - Project.py is the main file which contains all routes and logic
## Oauth 
  This application authenticates users using Google Oauth v2 api and stores user data in database.
  More [about](https://developers.google.com/identity/protocols/OAuth2) Google Oauth 
  
  
  For this api to work you need to have client_secrets.json which can downloaded from [Google Api Console](https://console.developers.google.con) 
  Then
  - Create a new project
  - Go to credentials page and update your information
  - Download the client_secret.json file and place it project directory
  
### webpage sample
   - [picture1](https://drive.google.com/file/d/1IzR7bv_VXnCZPzJ5Kx5g73mMK21P9qVx/view?usp=drivesdk)
   - [picture2](https://drive.google.com/file/d/1IzR7bv_VXnCZPzJ5Kx5g73mMK21P9qVx/view?usp=drivesdk)


## Api End points
  - [localhost:5000/json](http://localhost:5000/json)


    This will return all the companies details with its models


  - [local:5000/company/c_id/json](http://localhost:5000/company/1/json)


    This will return json data of company models


  - [local:5000/company/c_id/model/model_id/json](http://localhost:5000/company/4/model/3/json)
  

    This will return json data model data



>The classes used for styling the pages are taken form [w3.csss](https://www.w3schools.com/w3css/).