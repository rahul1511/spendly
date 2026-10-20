---
description: Create a single dummy user in database
allowed-tools : Read, Bash(python3:*)
---
Read the database/db.py to understand the users table
Schema and get_db() helper:

The write and run a python  script using Bash that :
    1-Generate a realistic random Indian User name using your own knowledge of common indian names across the regions:
        -Email : Derived from the name with a 2-3 digit number suffix (ed: rahul.kumar@45@gmail.com)
        - password : "password123" hashed with werkzeug's generate a password hash
        - created_at: current datetime

    2- Generate the new email if email already exists in user table, until the new unique email found.
    3- Insert the user into the database using the same get_db() pattern found in db.py
    4- Print the confirmation:
        - id
        - name
        - email

        