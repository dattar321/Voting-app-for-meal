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

## Architecture

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/6248c4a5-53bb-42c9-9e52-a2876c891626)


## Application Overview


The application starts with a login or register page:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/40b149f3-0f6f-4928-bd5d-b840f0ef5d71)

To register a user, navigate to the register page. If already registered, proceed to the login page: 

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/12d125b2-28ec-409c-a54a-530d0b088dff)


If attempting to register with a username that already exists, the user will stay on the register page. Upon successful registration, the user is redirected to the login page.

After logging in, the home page fetches all available menus from the database to display on the page:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/b0cfd93e-1945-43b1-90fb-568a706bd5ed)


At the top of the page, there is a section displaying today's selected food.A scheduler is implemented to reset the vote count to 0 after a specified period. If no votes are cast during this time, the system intelligently selects a random menu, ensuring a delightful dining experience for users. 
The user's username and logout option are on the top-right corner.

Menus can be selected on this page, and if selected, the card's color will turn green. A "Submit Vote" button is available at the bottom. However, if the user has already voted today, they won't be able to vote again:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/a1d7d46c-37cb-4b05-bd0c-0186ab71c1fc)

After clicking the "Submit" button, the page will appear as follows:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/a8b8e3e1-565b-472a-91b2-a5d1309fe9a6)

To access the admin panel, log in with the following credentials:

- `Username: admin@bs23.com`
- `Password: 123456`

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/b52b5003-30ce-4f1a-ac85-b21ca2d8636e)


Clicking on the admin panel option in the top-right corner will take you to the admin panel:


![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/4fece59c-94ae-4561-adcb-ffc72f7e2f19)

When the "Confirm Meal" button is clicked, it confirms the highest-voted menu to the menu_history database. If the highest-voted food's restaurant has won for three consecutive days.
Once an admin confirms the food selection, the menu for the day becomes immutable.
It will select the second-highest voted food:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/d25f6856-85ed-4b11-90da-9fd4f29e5de8)

As observed from the database, Chicken Grill has the most votes, but the selected food is Alu Vorta Vat because it was the second-highest among other restaurants.

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/0f8e7a9c-d9ba-4b75-a93a-e73a5a5a51bd)


Admins can add a restaurant:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/cea6110b-1721-4a26-9143-d7260a160a7e)

And also add a menu:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/c346cdf9-00c7-40d2-9c48-df9fabdcce03)

Here, the admin selects an existing restaurant from the dropdown, fills out the form, and adds the menu.

Admins or any normal users can log out at any time by clicking log out:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/252deca3-85e0-4c7a-b3a4-11b1f7ffdf13)

Log out will redirect to log in page.
Admins or any normal users can log out at any time:

![image](https://github.com/dattar321/Voting-app-for-meal/assets/42374695/252deca3-85e0-4c7a-b3a4-11b1f7ffdf13)


## Future Scope

- Implement user roles and permissions for better admin control.
- Add review system to menu
- By keeping track of the vote we can find the overall demand of the employees
