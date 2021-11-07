# Delivery App Front End

## Pre-requisites
1. Python 3
    
    [Download](https://www.python.org/downloads/) and install python.

2. Postgres
    
    [Download](https://www.postgresql.org/download/) and install Postgres.

3. Source Code

    Clone source code
```bash
git clone https://github.com/WBruss/DeliveryAppBackend.git
```

## Set Up
* Open terminal inside the root directory of the project
* Create [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with the name venv
```bash
python -m venv venv
```
* Activate virtual environment
```bash
venv\Scripts\activate
```
* Install packages in requirements.txt
```bash
pip install -r requirements.txt
```
* Create database in postgres
```bash
CREATE DATABASE delivery_app_test;
```
* Sort the database connection uri in the \_\_init\_\_.py file

        username, password and port default is 5432

* Run the appliaction
```bash
python app.py 
```