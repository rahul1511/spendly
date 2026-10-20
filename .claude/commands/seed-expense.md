---
description : seed a realistic dummy expense for a specific user
argument-hint: "<user_id> <count> <month>"
allowed-tools: Read, Bash(python3:*)
---

Read database/db.py to understand the expense table schema, the db connection pattern, and the database file name.

user input : $ARGUMENTS

# step-1 : parse Arguments
 Extract  from ARGUMENTS:
    - user_id -> integer
    - count -> integer, no. of expense to create
    - months -> integer , How many past month to spread them across

If any arguments missing or not a valid integer , stop and say:
    "Usage: /seed-expense <user_id> <count> <months>
    Example : /seed-expense 1 50 6

# step-2 : Verify user existing
Before generating anything , confirm that the user exists in the user table based on their user_id, if not, stop and say :
    "No user found with id <user_id>.?

# sept-3 : Generate and insert  expense 

Write and run a python script that :
1. Spreads expense randomly across the past <month> 
2. Uses these categories with realistic indian description and amount (₹):
    - Food : 50-80
    - Transportation : 20-500
    - Bills : 200-300
    - Health : 100-200
    - Shopping : 200-5000
    - Other : 50-100
    - Entertainment : 50 - 200

3- Distribute categories roughly proportionally
    (Food Most common, Health and Entertainment least)

4- Use the db connection pattern from db.py - do not hardcode the database filename 
5- Use parameterized query only no string formation in SQL query 
6- Insert all expense in a single transaction and rollback all if any error occurred or any insert fails    

# Step-4 : confirm

Print
 - How many expenses ware inserted
 - The date range by span
 - A sample of inserted record