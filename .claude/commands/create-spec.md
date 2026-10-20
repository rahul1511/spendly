--- 
description : Create a specs file for the next  expanse-tracker feature 
argument-hint : :Step number and feature name eg: 2 registration"
allowed-tools : Read, Write, Glob
---

You are a Senior software architecture, Planning a new feature Specification for the expense-tracker Project , Follow the repository's  CLAUDE.md instructions and conventions.

Use the user input as the feature request:


User Input : $ARGUMENTS
##  Step-1 : Check working directory is clean
Run `git status` and check for uncommitted, unstaged , or untracked files. if any exists, Stop immediately and tell the user to commit or stash changes before proceeding.
DO NOT CONTINUE until the working directory is clean.

## Step-2 " Parse the arguments

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
4.`branch_name` - format: `feature/<feature_slug>`
    Example : `feature/registration`

    if the step number or feature cannot be determined confidently from $ARGUMENTS, ask the user to clarify before continuing.Do not guess.

## Step 3 : Check Branch Name 
Run `git branch` in shell mode , to list the existing branches. if the `branch_name` is already taken , append a number:
    Examples: `feature/registration-01`, `feature/registration-02`

## Step 4: Switch to main and take latest pull

RUN
```
git checkout main
git pull origin main
```
In shell Mode

## Step 5: Create and switch the feature branch
RUN:
```
git checkout -b <branch_name>
```
In shell mode

## Step 6: Research the codebase
Read the sources before drafting the specification 
    - CLAUDE.md - roadmap, project conventions and schema guidance.
    - app.py - existing routes and schema behavior and functions
    - database/db.py - Current database schema and database access patterns. 
    - Existing file under: .claude/specs/ identify related works and avoid duplication.
    - Relevant template, static assets, tests and other implementation files needed to understand the feature.

Use Glob to find relivenet files, then  read the files that inform the specification. DO not assume a file's content based on its name

Check the roadmap in Claude.md , if requested step is already marked complete, warn the user and stop without creating or changing any spec.

Ground the specification in repository evidence. if a requirement or existing behavior cannot be confirmed list it under OPen Question rather than presenting an assumption as fact.

## Step 7; Write the specs
Generate a spec document with this exact structure:

# Spec: <Feature Title>
     
## Overview
    One paragraph explain what the feature does and why it  belongs to the  expense-tracker roadmap.

## Depends on 
List prerequisite roadmap steps by number and title. If there are none, write None.

## Open Questions

List decisions or requirements that need confirmation. ask the user with your suggestion , after approval only proceed, Include only genuine unknowns. If none, write None.


## Routes
For Each new or changed route, include :
    - HTTP method and path
    -Purpose
    -Access level (public or logged-in)
    - Relevant inputs and expected outcomes 
    
If no new routes are needed: Write "Now new routes".

## Database Changes
Add new tables, columns, indexes, constraints  or migrations.
Verify proposed changes against `database/db.py` for existing database patterns ,before writing the specs.

if there is no database changes: write "No database changes."

## Template
- Create: list of new templates with their path.
- Modify: list of existing templates and the required changes purpose, without changing any existing feature if using the same template. if required ask to user and take confirmation.
- Describe relevant UI states, validation messages, and error or success feedback.

If no template or UI changes are required, say so.

## File to create
If no template or UI changes are required, say so.

Files to Create

List each new file and its purpose. Do not repeat files already listed under Templates and UI unless they need additional explanation.

If no files need to be created, write None.

## File to changes
List each existing file and explain why it must change.

If no existing files need to be modified, write None.



## New Dependency
Any newList any new Python or other package dependencies and explain why each is required. 

If none are needed, write No new dependencies.

## Rules for implementations
Include only rules relevant to this feature. Follow repository instructions and, where applicable, include these project constraints:

Always Include:
    - Do not use SQLAlchemy or another ORM.
    - Use parameterized SQL queries; never build queries by interpolating user input.
    - For authentication features, hash passwords with Werkzeug’s password-hashing utilities.
    - Use existing CSS variables; do not hardcode color hex values.
    - Extend the project’s base.html template for new pages.
    - Apply SOLID principles where useful without adding unnecessary complexity.

    Add any feature-specific constraints supported by the repository or user request. Do not invent project conventions.

## Definition of Done

Write a specific, checkable checklist covering the expected behavior, validation, error cases, and relevant security or access-control requirements. Each item must be verifiable through the application or an appropriate test.

Do not claim that tests have been run unless they were actually run.

## Step 8: Save the specs
Save the completed specification to :
Save the spec to : `.claude/specs/<step_number>-<feature_slug>.md`

Create or modify only this specification file. Do not implement the feature or edit application files.

Before saving, confirm that the target filename does not duplicate an existing specification. If it does, stop and tell the user instead of overwriting it.


## Step 9 :  Report the user
After saving, respond in this format:

Spec file: .claude/specs/<step-number>-<feature-slug>.md
Title: <Feature Title>

Review the spec at .claude/specs/<step-number>-<feature-slug>.md, then use Claude Code’s Plan mode `shift+tab(double)`to plan implementation.

Do not print the full specification in chat unless the user explicitly asks for it.


