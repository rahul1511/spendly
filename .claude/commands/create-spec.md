--- 
description : Create a specs file for the next  expanse-tracker feature 
argument-hint : :Step number and feature name eg: 2 registration"
allowed-tools : Read, Write, Glob
---

You are a Senior software architecture and developer, Planning a new feature for the expense-tracker , Always follow the rules in CLAUDE.md.


User Input : $ARGUMENTS

## Step-1 " Parse the arguments

FROM the $ARGUMENTS extract:

1. `step number` - Zero-padded to 2 digits:
    2 -> 02, 11->11
2. `feature_title` - human readable title in Title Case
        -Example : "Registration" or "Login and Logout"

3.`feature_slug` - file safe slug
        - Lowercase, kebab-case
        - Only a-z, 0-9 and - , _ allowed
        - maximum 40 characters allowed
        - Example : registration , logion-logout 

    if yuu cannot infer these from $ARGUMENTS, ask the user to clarify before proceedings.

## Step 2: Research the codebase
Read these files before writing the the specs:
    - CLAUDE.md - roadmap, conventions,  schema
    - app.py - existing routes and schema and functions
    - All file in .claude/specs/ - avoid duplicating existing specs

    Check Claude.md to confirm the requested step is not already marked complete. if it is , warn the user and stop.

## Step 3; Write the specs
Generate a spec document with this exact structure:

# Spec <feature_title>
     
## Overview
    One paragraph describing what this feature does and why it exists at this stage of expense-tracker roadmap.

## Depends on 
which previous steps this feature requires to be complete.

## Routes
Every new route needed:
    -METHOD/Path - description - access level (public/logged-in)
    - If no new routes: state "Now new routes".

## Database Changes
Add new tables, columns, or constraints needed
-Always verify against database/db.py before writing this.
if None: state "No database changes."

## Template
- Create: list of new templates with their path.
- Modify: list of existing templates and what changes.

## File to create
Every new file that create to build the feature.

## File to changes
Every file that required changes and why ?


## New Dependency
Any new pip / uv package . if None State :No new Dependencies install " 
- If yes, then why that package , whats the use ?

## Rules for implementations
Specific constraints Claude must follow.
Always Include:
    - NO SOLAlchemy or ORMs Used 
    - Only Parameterized Query allowed, No string formatted
    - Password hashed with werkzeug
    - Use CSS variable - never hardcode hex values
    - All template extend base.html
    - Use Solid Principle , where required only , Do not Over complicate

## Definition of Done

A Specific testable checklist. Each item must be something that can be verified by running the app.

- Include edge case also
]
## Step 4: Save the specs
Once all above mention  step done :
Save the spec to : `.claude/specs/<step_number>-<feature_slug>.md`

## Step 5 :  Report the user
Print a short summary in tis exact format:
 Spec file : .claude/specs/<step_number>-<feature_slug>.md
 Title : <feature_title>

The tell the user:
"Review the spec at .claude/specs/<step_number>-<feature_slug>.md  the enter the plan Mode with `shift+tab` to beguin the implementation."

ALways Remember: Do not print the full Spec in the chat unless not asked exactly to show full spec

