# Servizo Setup Guide

A comprehensive guide to setting up the Servizo backend.



## Project Overview

**Servizo** is a service marketplace platform with:
- User authentication (customers, providers, admins)
- Service management and booking system
- Real-time chat between users
- Stripe payment integration
- Admin dashboard and financial reporting


## Prerequisites

| Component     | Version | Purpose          |
|---------------|---------|------------------|
| Python        | 3.8+    | Backend runtime  |
| MySQL Server  | Latest  | Database         |
| SQL Workbench | Latest  | SQL GUI          |
| pip           | Latest  | Package manager  |



## Installation (Assuming Windows as OS)

### Extract Project
Unzip the project files to your desired location.


### Install Dependencies through VS or whatever IDE terminal (must have python installed)

cd ServizoProject
cd backend
py -m pip install -r requirements.txt


## Database Setup

### Start MySQL
Ensure MySQL service is running (must be installed as pre requisite).


### Import Database through VSCode or IDE terminal

mysql -u root -p < servizo.sql

or if this doesnt work

Get-Content servizo.sql | mysql -u root -p



### Verify
Confirm `servizo` database exists with all tables through SQL Workbench.


## Configuration

| Setting               |         Default Value                 | Purpose             |
|-----------------------|------------------------------------   |---------------------|
| FLASK_SECRET_KEY      | Provided in config.py                 | Session security    |
| DB_HOST               | localhost                             | Database host       |
| DB_USER               | root                                  | Database user       |
| DB_PASSWORD           | 1234                                  | Database password   |
| DB_NAME               | servizo                               | Database name       |
| STRIPE_SECRET_KEY     | Provided test key in config.py        | Stripe API secret   |
| STRIPE_PUBLIC_KEY     | Provided test key in config.py        | Stripe public key   |
| STRIPE_WEBHOOK_SECRET | Provided test key in config.py        | Webhook security    |
| LOGGING_LEVEL         | INFO                                  | Log level           |



### Custom Configuration 
set DB_PASSWORD= your password      (change existing password according to your Db in config.py)


## Running the Application in the IDE terminal

python app.py

or right click in terminal, run python, run python file in terminal

Access at: `http://localhost:5000`



## Usage Guide

### User Roles

| Role             | Access        | Key Abilities                    |
|------------------|---------------|----------------------------------|
| Customer         | Immediate     | Book services, chat, pay         |
| Service Provider | After approval| Manage services, accept bookings |
| Admin            | Full system   | User management, reports         |


### Workflow
1. Customer registers → Immediate access
2. Provider registers → Admin approval required  
3. Service booking → Browse, book, and pay
4. Communication → Real-time chat
5. Payments → Secure Stripe processing
6. Admin oversight → Platform management


## Troubleshooting

| Issue                      | Solution                                      |
|----------------------------|-------------------------------------------    |
| Database connection fails  | Check MySQL service and config.py credentials |
| Payment errors             | Verify Stripe API keys in configuration       |
| Port 5000 occupied         | Change port or free it up                     |
| Package install fails      | Ensure Python 3.8+ and latest pip             |
| Import errors              | Verify all requirements installed             |



### Help Resources
- Flask documentation
- MySQL connection guides  
- Stripe API documentation

