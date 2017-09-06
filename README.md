# Computer Wallpapers Catalog App
This project is an app developed for Udacity Full Stack Web Developer Nanodegree. The goal for this project is to develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items. Develop a RESTful web application using the Python framework Flask along with implementing third-party OAuth authentication. Properly use the various HTTP methods available and how these methods relate to CRUD (create, read, update and delete) operations.

## About
This app is a python project which uses the Flask framework to display a catalog of wallpapers using a SQL database. The website displays all the categories and all the wallpapers in each category. Using OAuth2.0, users are authenticated and authorized to add, edit or delete categories and wallpapers.

## Requirements
* VirtualBox 5.1
* Vagrant 1.9.1
* Python 2.7.13
* Postgresql 9.5.8
* OAuth 2.0
* Flask Framework

## Installation

1. **VirtualBox** - To successfully run this app, you must install VirtualBox Application. [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. **Vagrant** - You will need to install Vagrant to share the folder to your virtual machine. [Download Vagrant](https://www.vagrantup.com/downloads.html)

3. **fsnd-virtual-machine.zip** - Download [fsnd-virtual-machine.zip](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip) to build a vagrant virtual machine.

4. Unzip fsnd-virtual-machine.zip.

5. In the fsnd-virtual-machine directory, change directory to the vagrant directory

6. Once you are in the vagrant directory, start the Vagrant VM with the `vagran up` command

7. The download will start. It is a big file, be patient. Once the installation of your virtual machine has completed, you can connect to your new virtual machine using SSH with the following command: `vagrant ssh`

8. Download or clone this Computer Wallpapers Catalog App. Be sure to place this repository inside the /vagrant directory.

## Run The App
To successfully run this app, please execute the following python commands inside the /vagrant/catalog directory

1. Sets up the SQL database - `python database_setup.py`
2. Initialize the mocked data - `python database_init.py`
3. Starts the application - `python application.py`
4. Open your host machine browser to access the application using http://localhost:8000


## OAuth2.0
This app uses Google OAuth2.0 Client Ids to authenticate and authorize registered users to administer their own submissions. Follow the following steps to setup Google OAuth2.0 Client Id. Please Note. Google frequently updates their interfaces, as of September 2017, these are the steps I performed to create a Google OAuth2.0 Client Id:

1. Go to [Google Dev Console](https://console.developers.google.com)
2. You will need to Login or Signup to a google account.
3. Once you are signed in to Google Dev Console, you will be taken to the API dashboard.
4. On the left menu, click "Credentials"
5. In the Credentials Page, you will see a blue drop down menu titled: Create credentials
6. From the Create credentials menu, select OAuth Client Id
7. For Application Type, Select "Web Application"
8. Name: Name the application wallpaper-app
9. In the Restrictions section populate the following fields with the following information:

    **Authorized JavaScript origins:**

      <em>http://localhost:8000</em>

    **Authorized redirect URIs**

      <em>http://localhost:8000/login</em>

      <em>http://localhost:8000/gconnect</em>

10. Hit create button
11. After you have created your Client Id, you will be taken back to the credentials page. Under OAuth 2.0 client IDs section, you will see you newly created client ID
12. Click the download button on the far right of the wallpaper-app Client Id - This will be a .json file. You will need to rename this file to client_secrets.json and place it in the root directory of this repository ( /vagrant/catalog )
13. Open the wall_login.html file. You can find this file in this app's templates directory. Once you have the wall_login.html file, populate your Client Id in the settings: data-clientid="" (you can find this on line 26 of the wall_login.html file)
14. Save your changes and run the application with python command: `python application.py`


## JSON Endpoints
This application uses JSON endpoints which are available publicly. The following are examples of the 'animal' category and 'Tigers' Wallpaper

Displays all categories currently in the database<br>
JSON: `/JSON/categories/`<br>
Example: http://localhost:8000/JSON/categories/

Displays all wallpapers currently in the database<br>
JSON: `/JSON/wallpapers/`<br>
Example: http://localhost:8000/JSON/wallpapers/

Displays all the wallpapers in a particular category<br>
JSON: `/JSON/categories/<path:category_name>/`<br>
Example: http://localhost:8000/JSON/categories/Animal/

Displays a specific wallpaper in its category<br>
JSON: `/JSON/categories/<path:category_name>/<path:item_name>/`<br>
Example: http://localhost:8000/JSON/categories/Animal/Tigers/

