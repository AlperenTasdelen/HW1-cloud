This e-commerce repository contains the code which utilizes MongoDB, Flask framework and html.
Website's main properties are product browsing,
authenticated user account management and product alert system.
This README provides information about design decisions, URL deployment,
login guide, programming languages, frameworks and other relevant details.

Design Decisions:

Database: MongoDB is main database; due to its flexiblity and
scalability, storing and pulling data is efficient.

Backend: Flask is selected as the backend framework.
Flask is simple, beginner friendly, extensible and
easy to integrate with MongoDB

Frontend: For indexing and page display structure, HTML is
used due to styling and interactivity opportunities.

User Authentication: Basic username, password and e-mail
authentication is provided for registeration.

URL: https://hw1-cloud.onrender.com

Login instructions

Admin Login:
    Email: alperen.tasdelen@metu.edu.tr
    Password: admin

User Login
    Email: (your-cengmail) (only cengmails allowed for registeration)
    Password: (your password)

Register instructions

    Username: 
    Email: (cengmail) (only cengmail allowed)
    Password:
    Phone:

Choice of Programming Language and frameworks
    Programming Language: Python
    Backend Framework: Flask
    Database: MongoDB

User Guide
Browse Products:
    - In homepage, click Products
    - Click on a product to view its details
    - If the owner does not allow displayation of
    own email and phone to the regular users, until
    you sign in to an account you can't display
    these information

Adding Products:
    - Visit profile after registeration
    - Click Add Item
    - Choose the item category to insert
    item informations

View Own Products:
    - You have a full list of own items in profile
    - Whenevet you view your own product, you can
    see item update, delete, activate-deactivate buttons
    under the page

User Account Management:
    - In profile page, Manage Account button
    allows user to change account information

Admin Dashboard:
    - When the user enters the system with admin
    user, profile page has UserList button
    - This list displays all users to delete which
    admin would prefer to delete
    - When admin displays an item, admin is allowed to modification
    - Deleting users also delete items owned by deleted user
    - Admin also has ItemList which allows admin to delete items easily,
    - This list shows all items, activation does not important

Dependencies: Make sure to install all dependencies listed
in 'requirements.txt'

Repository: https://github.com/AlperenTasdelen/HW1-cloud.git

Contact:
Name Surname: Alperen Taşdelen
Email: e2521987@ceng.metu.edu.tr
Student Number: 2521987




