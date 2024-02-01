# Voting App for Meal

## Overview
This Flask-based web application where users can register, log in, vote for meals, and view the current highest-voted meal. The application also includes an admin panel for managing restaurants and menus.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/dattar321/Voting-app-for-meal.git
    cd Voting-app-for-meal
    ```

2. **Create a virtual environment:** (optional)
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:** (optional)
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. **Open a Python shell:**
    ```bash
    python
    ```

2. **Inside the Python shell, create the database:**
    ```python
    from your_app import db
    db.create_all()
    exit()
    ```
## Database Schema

### Employee Table

- **Columns:**
    - `id`: Integer, Primary Key
    - `username`: String(20), Unique, Not Null
    - `password`: String(80), Not Null

### Restaurant Table

- **Columns:**
    - `id`: Integer, Primary Key
    - `name`: String(50), Unique, Not Null
    - `streak`: Integer, Default: 0

- **Relationships:**
    - One-to-Many with `Menu` table (Backref: `restaurant.menus`)

### Menu Table

- **Columns:**
    - `id`: Integer, Primary Key
    - `date`: Date, Default: Current Date
    - `name`: String(80), Unique, Not Null
    - `vote`: Integer, Default: 0
    - `description`: String(255), Not Null
    - `restaurant_id`: Integer, Foreign Key (References: `restaurant.id`), Not Null

- **Relationships:**
    - One-to-Many with `Vote` table (Backref: `menu.votes`)
    - Many-to-One with `Restaurant` table (Backref: `menu.restaurant`)

### MenuHistory Table

- **Columns:**
    - `id`: Integer, Primary Key
    - `datetime`: DateTime, Default: Current Datetime
    - `menu_id`: Integer, Foreign Key (References: `menu.id`), Not Null
    - `restaurant_id`: Integer, Foreign Key (References: `restaurant.id`), Not Null

- **Relationships:**
    - Many-to-One with `Menu` table (Backref: `menu_history.menu`)
    - Many-to-One with `Restaurant` table (Backref: `menu_history.restaurant`)

### Vote Table

- **Columns:**
    - `id`: Integer, Primary Key
    - `datetime`: DateTime, Default: Current Datetime, Not Null
    - `menu_id`: Integer, Foreign Key (References: menu.id), Not Null
    - `restaurant_id`: Integer, Foreign Key (References: restaurant.id), Not Null

## Relationships

- **`Employee` and `MenuHistory`:**
    - No direct relationship between these tables.

- **`Employee` and `Restaurant`:**
    - No direct relationship between these tables.

- **`Employee` and `Menu`:**
    - No direct relationship between these tables.

- **`Menu` and `MenuHistory`:**
    - No direct relationship between these tables.

## Database File

- The SQLite database file is created based on the `app.py` configuration.

## Usage

1. **Run the application:**
    ```bash
    python your_app.py
    ```

2. **Open your web browser and go to [http://localhost:5000](http://localhost:5000)**

3. **Register a new account, log in, and start voting!**

## Admin Panel

To access the admin panel:

1. Log in with admin credential.
2. Navigate to [http://localhost:5000/admin](http://localhost:5000/admin)
3. Manage restaurants and menus..

## Scheduled Task

The application has a scheduled task that resets votes every 24 hours, ensuring a fresh start for the voting system.

## Future Scope

- Implement user roles and permissions for better admin control.
- Add review system to menu
- By keeping track of the vote we can find the overall demand of the employees
