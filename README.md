# Rule Engine Project

This is a Django-based web application for managing and combining rules using an Abstract Syntax Tree (AST). Users can create, edit, delete, and combine rules using operators like `AND` and `OR`. The project leverages the flexibility of Python and Django to provide an interface for rule management and complex logical operations.

## Features

- **List Rules**: Displays all existing rules with their string representations and ASTs.
- **Edit Rules**: Allows editing rule strings in the interface and updates the database.
- **Delete Rules**: Provides the option to select multiple rules and delete them.
- **Combine Rules**: Users can select multiple rules and combine them using logical operators (`AND` or `OR`).
- **AST Representation**: The system stores rules in AST form for easy manipulation and evaluation.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)

## Requirements

Make sure you have the following installed:

- Python 3.x
- Django 3.x or higher

## Installation

1. **Clone the Repository**:

   ```bash
   [git clone https://github.com/your-repo/rule-engine-project.git](https://github.com/HARIPRASAD27102003/Assignment.git)
   cd rule-engine-project


2. **Create a Virtual Environment**:			

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate

3. **Installation**:

   ```bash
   pip install -r requirements.txt

4. **Run Migrations**:

   ```bash
   python manage.py migrate

5. **Run Application**:

   ```bash
   python manage.py runserver

## Usage

### List Rules
- You can view rule names, rule strings, and their AST representations.

### Edit Rules
- On the rule list page, click the **Edit** button next to the rule.
- Modify the rule string using the inline form.
- Click **Save** to update the rule.

### Delete Rules
- Select rules using checkboxes on the rule list page.
- Click **Delete Selected Rules** to remove them from the system.

### Combine Rules
- Navigate to `/combine-rules/` to access the rule combination form.
- Select multiple rules to combine.
- Choose a logical operator (AND or OR).
- Click **Combine Rules** to generate the combined rule string.

## API Endpoints
- **``**: List all the available rules with their string and AST representations.
- **`/edit-rule/`**: Edit an existing rule.
- **`/delete-rules/`**: Delete selected rules.
- **`/combine-rules/`**: Combine selected rules using logical operators.

## Folder Structure

<img width="510" alt="Screenshot 2024-10-23 at 09 29 14" src="https://github.com/user-attachments/assets/70daba42-edf9-4afb-95a4-dc2ee5567b05">

## ScreenShot

### Rule Table

<img width="1468" alt="Screenshot 2024-10-23 at 09 34 16" src="https://github.com/user-attachments/assets/7aa6848e-393d-4753-8756-87d27996e6e9">

### Create Rule

<img width="1470" alt="Screenshot 2024-10-23 at 09 34 46" src="https://github.com/user-attachments/assets/99f15f41-633f-46ff-9044-515f24e038cf">

### Combine Rules

<img width="1467" alt="Screenshot 2024-10-23 at 09 35 46" src="https://github.com/user-attachments/assets/79e5b005-de28-4817-8e62-f9a64591f1c2">

### Evaluate Rules

<img width="1469" alt="Screenshot 2024-10-23 at 09 36 20" src="https://github.com/user-attachments/assets/91e57be4-6034-439c-aa2b-62108bd6bc45">






