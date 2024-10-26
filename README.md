# 🚀 Rule Engine Project

This is a **Django-based web application** for managing and combining rules using an **Abstract Syntax Tree (AST)**. Users can create, edit, delete, and combine rules using operators like `AND` and `OR`. The project leverages the flexibility of Python and Django to provide an interface for rule management and complex logical operations.

## 📋 Features

- **List Rules**: Displays all existing rules with their string representations and ASTs.
- **Edit Rules**: Allows editing rule strings in the interface and updates the database.
- **Delete Rules**: Provides the option to select multiple rules and delete them.
- **Combine Rules**: Users can select multiple rules and combine them using logical operators (`AND` or `OR`).
- **AST Representation**: The system stores rules in AST form for easy manipulation and evaluation.

## 📚 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## ⚙️ Requirements

Make sure you have the following installed:

- **Python 3.x**
- **Django 3.x or higher**

## 📦 Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-repo/rule-engine-project.git
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

## 🛠️ Usage

### List Rules
- Access the rule list at `/list-rules/` to view all existing rules along with their names, rule strings, and AST representations.

### Edit Rules
1. On the rule list page, click the **Edit** button next to the rule you wish to modify.
2. In the inline form, update the rule string as needed.
3. Click **Save** to apply your changes to the database.

### Delete Rules
1. On the rule list page, select the rules you want to delete using the checkboxes.
2. Click **Delete Selected Rules** to remove the selected rules from the system.

### Combine Rules
1. Navigate to `/combine-rules/` to access the rule combination form.
2. Select multiple rules from the available list to combine.
3. Choose a logical operator (`AND` or `OR`) for combining the selected rules.
4. Click **Combine Rules** to generate the combined rule string and view the result.

## 🌐 API Endpoints

- **`GET /list-rules/`**: 
  - **Description**: Retrieve a list of all available rules with their string and AST representations.
  
- **`POST /edit-rule/<int:rule_id>/`**: 
  - **Description**: Edit an existing rule identified by `rule_id`. Requires the updated rule string in the request body.

- **`POST /delete-rules/`**: 
  - **Description**: Delete selected rules. The request should include the IDs of the rules to be deleted.

- **`POST /combine-rules/`**: 
  - **Description**: Combine selected rules using logical operators. Requires the selected rule IDs and the chosen operator (AND/OR) in the request body.


## 📁 Folder Structure

![Folder Structure Zoomed Out](https://github.com/user-attachments/assets/70daba42-edf9-4afb-95a4-dc2ee5567b05) <!-- Use a zoomed-out version of the image -->

---

## 📸 Screenshots

### Overview

This section provides visual insights into the various functionalities of the application, illustrating the interface for rule management.

| Rule Table | Create Rule | Combine Rules | Evaluate Rules |
|------------|-------------|---------------|----------------|
| ![Rule Table](https://github.com/user-attachments/assets/7aa6848e-393d-4753-8756-87d27996e6e9) | ![Create Rule](https://github.com/user-attachments/assets/99f15f41-633f-46ff-9044-515f24e038cf) | ![Combine Rules](https://github.com/user-attachments/assets/79e5b005-de28-4817-8e62-f9a64591f1c2) | ![Evaluate Rules](https://github.com/user-attachments/assets/91e57be4-6034-439c-aa2b-62108bd6bc45) |
| *Overview of all existing rules, displaying their names, conditions, and actions for quick management.* | *User interface for creating new rules, allowing users to define conditions and actions seamlessly.* | *Feature to combine multiple rules for complex evaluations, providing flexibility in rule management.* | *Interface for evaluating combined rules against specific data inputs, with instant feedback on the results.* |

---

## 🚀 Features
- **Dynamic Rule Management:** Seamlessly create, combine, and evaluate rules.
- **User-Friendly Interface:** Intuitive design for easy navigation.
- **Real-Time Evaluation:** Instant feedback on rule evaluations.

## 🤝 Contribution

We welcome contributions from the community! If you would like to contribute to this project, please follow these steps:

1. **Fork the Repository**: Click on the "Fork" button at the top right corner of this page to create a personal copy of the repository.
2. **Create a New Branch**: Make a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/YourFeatureName


### Notes:
- Ensure that you have a `LICENSE` file in your repository that contains the full text of the MIT License.
- Adjust any wording in the Contribution section as necessary to fit your project's workflow or guidelines.
