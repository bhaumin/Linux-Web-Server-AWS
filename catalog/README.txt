Item Catalog
-------------

This application allows you to view and manage a catalog which comprises of different categories and their items


It contains the following files.
--------------------------------------------

1 - database_setup.py
	This file defines the python entity classes which map to the corresponding database tables.

2 - populate_categories.py
	This file creates some categories in the database.

3 - application.py
	This is the main file which implements the different methods which allow you to manage the catalog.

4 - templates/*.html
	Multiple html templates which render the UI for different functionalities in the browser.

5 - static/styles.css
	This file contains the CSS/Styling for this web application

6 - catalog.db
	This is the database file

7 - README.txt


How to run the application.
----------------------------
You need to have installed python 2.7.6 and SqlAlchemy 0.8.4 in your machine. You also need to install a 3rd party open source library called "dicttoxml" which helps convert a Python dictionary or other native data type into a valid XML string. Location of dicttoxml on github: https://github.com/quandyfactory/dicttoxml


1 - In terminal/cmd, navigate to the directory where the files are located.
2 - Install dicttoxml, by running the command line "pip install dicttoxml" or following the installation instructions on the github page mentioned above.
3 - Run the command line "python database_setup.py" to create and setup the catalog database.
4 - Run the command line "python populate_categories.py" to populate with the categories.
5 - Run the command line "python application.py" which will run the catalog web application on port 8000.
6 - Open the browser and go to "http://localhost:8000/", this will open the catalog application.
7 - You should be able to add/edit/modify the catalog items.
8 - API Endpoints that returns all categories and its items:
	a. JSON: http://localhost:8000/catalog.json
	b. XML: http://localhost:8000/catalog.xml
	c. Atom (Returns the latest 10 items added/modified): http://localhost:8000/catalog.atom


Copyright: Udacity
Author: Bhaumin Shah
Date: Dec 26, 2015
