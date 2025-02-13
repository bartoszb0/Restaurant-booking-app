# Restaurant Reservation System
Final Project for CS50x
#### Video Demo:  <https://www.youtube.com/watch?v=huykymHFN7s&ab_channel=bartek>
#### Description:
The **Restaurant Reservation System** is a web application that allows customers to book tables at a restaurant, manage their reservations, and for admin users, view and manage all reservations. The application is built using **Flask** for the web framework and **SQLite** for the database. It is designed to handle various user roles, including standard users (customers) and admin users (restaurant staff). Admins can view and cancel any reservation, while regular users can only manage their own reservations.

Key features include:
- **User Registration and Authentication**: Users can register, log in, and change their password securely.
- **Reservation Management**: Users can view available tables for a specified date, time, and guest count, then book a table. They can also view, manage, and cancel their own reservations.
- **Admin Features**: Admin users can view all reservations, cancel them, and manage the system efficiently.
- **Date and Time Validation**: The system checks for valid reservation dates, ensures availability, and avoids double booking by managing table slots.

The app uses **SQLAlchemy** for database management, ensuring that reservation data is stored efficiently and can be retrieved for display in real time.

---

## File Structure

### `app.py`

This is the core of the application where routes are defined, logic for reservation management is implemented, and interactions with the database are handled. It contains the following key parts:

- **Session and Database Configuration**: Configures Flask to use sessions for user login states and uses SQLite to store data.
- **User Authentication Routes** (`/login`, `/register`, `/logout`): These routes handle user login, registration, and logout. Passwords are securely hashed and stored.
- **Reservation Routes** (`/view`, `/book`, `/reservations`): These routes handle the viewing of available tables, booking reservations, and displaying user-specific reservations.
- **Admin Routes** (`/all_reservations`): This route allows admin users to view and manage all reservations.
- **Password Change** (`/change_password`): A route that allows users to change their passwords with validation.

### `helpers.py`

This file contains utility functions that support different features of the application, including:

- **Login and Admin Checks**: The `login_required` decorator ensures that only logged-in users can access certain routes, while `admin_required` restricts certain actions to admin users only.
- **Validation Functions**: There are functions that validate form data, such as password complexity checks (`validate()`), reservation dates and times (`validate_date_time_guests()`), and (`validate_reservations()`).
- **Error Handling**: The `error()` function is used to display error messages with a redirection.

### `models.py`

This file defines the database models using SQLAlchemy. It contains the following models:

- **Users**: Stores user information, including `username`, `password_hash`, and `role` (admin or user).
- **Reservations**: Stores reservation information, including `date`, `time`, `guests`, and `user_id`.

### `templates/`

This directory contains the HTML templates used for rendering pages in the web application. These templates include:

- **layout.html**: Layout for all the templates
- **view.html**: The homepage that lets user view available reservations.
- **login.html**: A form for users to log in to the system.
- **register.html**: A form for new users to register an account.
- **reservations.html**: A page showing a list of the current user's reservations. or all reservations for the admin
- **change_password.html**: A form to allow users to change their password.

### `static/`

This directory contains the static files like CSS used to style the web application.

---

## Design Choices and Considerations

### Authentication and Security

The system implements user authentication with hashed passwords using **Werkzeug**'s password hashing utility. This ensures that user credentials are securely stored and protected from unauthorized access. Sessions are used to track logged-in users, and specific routes are protected using decorators like `login_required` to ensure that only authenticated users can access sensitive parts of the application.

### Reservation System Logic

One of the most important aspects of the project was implementing the reservation logic. Reservations are checked for availability before they can be confirmed, preventing double-booking. The system validates the reservation date, time, and guest count to ensure that the restaurant can accommodate the request.

### Admin Features

Admin users have additional privileges that allow them to manage all reservations. This was implemented through role-based authentication, with routes restricted to users with the "admin" role. Admins can view all reservations, cancel them if necessary, and maintain oversight of the entire reservation system.

### Error Handling

The application features basic error handling that guides the user with appropriate messages, especially when a form submission fails due to invalid data (e.g., incorrect password format). This ensures that the user experience is smooth, and issues are communicated clearly.

### Password Management

The password management system includes a strong validation mechanism that enforces secure password formats. Additionally, the `change_password` feature allows users to update their password while ensuring that it meets security requirements, further enhancing account safety.

---

## Conclusion

This **Restaurant Reservation System** provides a robust solution for managing table bookings at a restaurant, with features for both regular users and administrators. It has a secure, easy-to-use interface for customers and efficient management tools for restaurant staff. The project combines essential web development concepts like authentication, database management, and dynamic content rendering to create a functional application that can be expanded and customized for specific needs.
