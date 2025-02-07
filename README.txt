FLASK WATCH STORE APPLICATION
This project is a Flask-based e-commerce application designed to showcase watches, with functionality for user
reqistration, login, cart management and an admin panel to manage products and users.

Product Browsing:
- All users can browse all the products and view the single products on the index page.
- They can search for the watch model and brand in the search bar, and the watches matching the search will filter as the
  user types.
- The user can filter the watch results by brand.
- The user can also convert the price of the watches to other currencies.

User Authentication:
- Users register and log in as either customers or admins.
- The customers can register on the login page, where there is a link at the bottom to register if you do not have an
 account.
- Admins can only be added by other admins in the admin home page.

- When customers log in, they are directed to the index page, where they can browse products and add them to their cart.
- From the cart, the user can remove the products from the cart and go to a 'checkout' page
- Only logged-in users can add products to their cart.
- When admins log in, they are directed to the admin home page
- Here, they can see a list of all the registered users and all the stored products
- The admins can add products to the database, edit them and delete them in the admin home page
- The admins can add other admins here too

Currency Conversion:
The currency conversion uses an external api (Exchangeratesapi) to convert prices between EUR and the selected currency

Database:
The application uses SQLite for storing user and product data.
The users table stores user details including username, password, email and role.
The watches table stores watch details including name, brand, price stock and more.

