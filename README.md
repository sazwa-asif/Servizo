
<h1>
  <img src="https://github.com/user-attachments/assets/3bbb07ee-5190-4ad1-980b-8e760acaf819" 
       alt="main-logo" 
       width="50" 
       height="50" 
       style="vertical-align: middle; margin-right: 8px;">
  Servizo – Skilled Hands, Smart Service
</h1>

Servizo is a full-stack e-commerce home services platform that connects customers with verified service providers through a secure, transparent, and efficient digital marketplace. The platform follows a customer-driven offer broadcasting model, ensuring fair pricing, accountability, and payment security.



## 🗂️ Project Overview

The home maintenance industry often suffers from trust issues, inconsistent pricing, unreliable scheduling, and insecure payment handling. Servizo addresses these challenges by introducing a centralized digital platform that verifies service providers, allows customers to broadcast service offers, and ensures secure escrow-based transactions.



## ❗Problem Statement

Customer Pain Points

* Difficulty finding verified and trustworthy service technicians
* Unclear and inconsistent service pricing
* Long waiting times and unreliable scheduling
* Payment security and dispute resolution concerns

Service Provider Challenges

* Limited access to a consistent customer base
* Irregular job opportunities
* Payment delays and uncertainties
* Lack of a professional digital platform


## 💡Proposed Solution

* Admin-verified service providers
* Customer broadcasts service requirements with preferred pricing
* Providers accept or reject offers
* Secure escrow-based payment system
* Real-time chat between customers and providers
* Rating and feedback system
* Commission-based revenue model (20%)



## 🎯Target Audience

* Customers: Homeowners, renters, and individuals seeking reliable home services
* Service Providers: Electricians, plumbers, cleaners, technicians, and handymen
* Platform Administrators: System managers and moderators



## 🏗️System Architecture

Servizo follows a three-tier architecture:

Frontend
Responsive web-based user interface for customers, providers, and admins

Backend
Flask-based backend responsible for authentication, business logic, bookings, payments, and APIs

Database
MySQL database for secure and reliable data storage




## 🛠️Tech Stack

Frontend
HTML5, CSS3, JavaScript, Bootstrap

Backend
Python (Flask Framework)

Database
MySQL

Real-Time Communication
Socket.IO

Payment Gateway
Stripe API (Test Mode)

Security
Werkzeug (Password Hashing & Authentication)


## 👥User Roles and Functionalities

Customer

* Register and login
* Broadcast service offers
* Make secure payments
* Chat with service providers
* View booking history
* Submit ratings and feedback

Service Provider

* Register and await admin approval
* View available service offers
* Accept or reject offers
* Chat with customers
* Manage assigned jobs
* Track earnings and ratings

Admin

* Approve or reject service providers
* Manage service categories
* Monitor bookings and payments
* Handle provider payouts and customer refunds
* View commission and revenue reports


## 🚀Core Features

* Multi-role authentication system
* Service and provider management
* Offer broadcasting and acceptance system
* Real-time chat using Socket.IO
* Secure Stripe payment integration
* Escrow-based fund holding
* Booking lifecycle management
* Feedback and rating mechanism
* Admin reporting and analytics dashboard



## 💳 Payment Workflow

1. Customer creates a service offer
2. Service provider accepts the offer
3. Customer completes payment via Stripe
4. Payment is held securely in escrow
5. Job completion is confirmed by both parties
6. Provider receives 80% while the platform retains 20%
7. Refunds are processed by admin in case of disputes or cancellations



## 🔄System Flow

Admin Flow
Login → Approve Providers → Manage Services → Monitor Payments → Generate Reports

Service Provider Flow
Register → Admin Approval → View Offers → Accept Job → Complete Service → Receive Payment

Customer Flow
Register/Login → Create Offer → Payment → Chat → Service Completion → Feedback


## 💸Revenue Model

* Platform Commission: 20%
* Service Provider Earnings: 80%
* Escrow-based payment protection
* Transparent transaction history and commission reporting


## 🖼️Graphical User Interface (GUIs)

## Landing Page

<img width="450" height="700" alt="image" src="https://github.com/user-attachments/assets/a1c4954e-62c4-4189-ba95-a78e483cc5fe" />


## Login Page
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/06abd73e-8d36-4d58-93d8-44058ff0a1ae" />


## Admin Dashboard
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/b2b9b21f-d8f3-4991-9b34-1765e52345ab" />


## Service Provider Dashboard
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/ada5d092-3724-4f35-a529-aa3a0db1e3f5" />


## Customer Dashboard
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/7cb1c98f-df0a-4136-b353-0aee466f4621" />


## Commission Reports (Admin)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/e34525a7-62e7-4312-a7c1-3197d294e094" />

## Manage Service Provider (Admin)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/a01d1633-2aa9-4bb4-9215-1c2c7f0473a9" />


## Manage Services (Admin)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/626ce1a4-2cd7-439b-bfb1-69b9262d35ae" />

## Manage Payments (Admin)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/51f39eed-dc47-4155-8d19-86b8e11e4bd0" />

## View Profile (Service Provider)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/8ec5fccd-317a-4734-b7a3-6d4081a7f7c2" />

## Service Provider (Customer Offers)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/5c0df6d2-5236-4a39-89f0-0813acc753b3" />

## Service Provider (Manage Jobs)
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/8d3c24e3-ff25-480f-b5af-782c62592731" />












