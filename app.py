from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
import sqlite3
import io
import requests


app = Flask(__name__)
# setting a secret key for secure sessions
app.secret_key = 'cab55a52341d5763e41fb92c77241b02'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn


# Login route from project deliverable 1
# Login route
@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Get login credentials from the form
        username = request.form['username']
        password = request.form['password']


        # Fetch user from the database using the username
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        # check if user exists
        if user is None:
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login'))

        # Validate password
        if user['password'] != password:
            flash('Incorrect password', category='danger')
            return redirect(url_for('login'))

        # Set session based on user type and redirect accordingly
        session['username'] = user['username']
        if user['role'] == 'admin':
            return redirect(url_for('admin'))
        elif user['role'] == 'customer':
            return redirect(url_for('index'))

    # Render login page
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Get registration details from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = 'customer'  # Default role

        # Validate if the username or email already exists
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        conn.close()

        if existing_user:
            flash('Username or Email already exists. Please choose a different one.', category='danger')
            return redirect(url_for('register'))

        # Insert the new user into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
                     (username, password, email, role))
        conn.commit()
        conn.close()

        flash('Account created successfully! Please log in.', category='success')
        return redirect(url_for('login'))

    # Render the registration page
    return render_template('register.html')


# Logout route
@app.route('/logout')
def logout():
    # Clear the entire session to fully log the user out
    session.clear()
    # Redirect to the login page or home page
    return redirect(url_for('login'))

# Admin home route - requires user to be logged in as an admin
@app.route('/adminhome')
def admin():
    # Check if the user is logged in via session
    if 'username' not in session:
        flash('You must be logged in to access the admin page.', category='danger')
        return redirect(url_for('login'))

    # Get all registered user for the data on the admin page and render template
    conn = get_db_connection();
    users = conn.execute('SELECT * FROM users ').fetchall()
    conn.close()

    # get the logged - in username
    username = session['username']

    # render the admin page with user data
    return render_template('admin_home.html', users=users, username=username)


# Currency conversion function

# Currency conversion function
def get_exchange_rate(base_currency, target_currency):
    api_key = "85a7ddc39aa3b807e052560d40a7ab96"
    url = f"https://api.exchangeratesapi.io/v1/latest?access_key={api_key}&base={base_currency}&symbols={target_currency}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data["rates"].get(target_currency)
        else:
            print("Error in API response:", data.get("error"))
            return None
    except requests.RequestException as e:
        print("HTTP Request failed:", e)
        return None

# Convert currency
def convert_currency(price, from_currency, to_currency):
    if from_currency == to_currency:
        return price
    rate = get_exchange_rate(from_currency, to_currency)
    if rate is not None:
        return round(price * rate, 2)
    return None

# search watches
@app.route('/search_watches', methods=['GET'])
def search_watches():
    search_query = request.args.get('query', '').lower()
    conn = get_db_connection()

    # Query watches based on the search query
    query = 'SELECT id, name, price, brand FROM watches WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ?'
    params = [f'%{search_query}%', f'%{search_query}%']
    watches = conn.execute(query, params).fetchall()
    conn.close()

    # Convert the fetched watches to a list of dictionaries
    watch_list = [{
        'id': watch['id'],
        'name': watch['name'],
        'price': round(watch['price'], 2),
        'brand': watch['brand'],
        'currency': request.args.get('currency', 'EUR')  # Ensure currency is included
    } for watch in watches]

    # debugging
    print(f"Search query: {search_query}, Matches: {watch_list}")
    return jsonify({
        'watches': watch_list,
        'selected_currency': request.args.get('currency', 'EUR')
    })



# Home page to display all watches and users at the moment!
# it currently only shows name and description, but I will add brand and other stuff later
@app.route('/')
def index():
    conn = get_db_connection()
    brand_filter = request.args.get('brand')
    currency = request.args.get('currency', 'EUR')

    # Base query retrieves all watches
    query = 'SELECT id, name, price, brand FROM watches'
    params = []

    # Apply brand filter only if provided
    if brand_filter:
        query += ' WHERE brand = ?'
        params.append(brand_filter)

    # Fetch all watches (filtered or not)
    watches = conn.execute(query, params).fetchall()

    # Convert the prices based on the selected currency
    converted_watches = []
    for watch in watches:
        converted_price = convert_currency(watch['price'], 'EUR', currency)
        converted_watches.append({
            'id': watch['id'],
            'name': watch['name'],
            'price': converted_price,
            'brand': watch['brand']
        })

    conn.close()
    return render_template('index.html', watches=converted_watches, selected_currency=currency)


# Viewing a single watch
@app.route('/view_watch/<int:id>')
def view_watch(id):
    conn = get_db_connection()
    watch = conn.execute('SELECT * FROM watches WHERE id=?', (id,)).fetchone()
    conn.close()

    if watch:
        # render product details page if product exists
        return render_template('watch.html', watch=watch)
    else:
        # return error if product is not found
        return flash('Product not found', category='danger')



# Create or Edit a watch item - maybe make this admin only ?
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
@app.route('/add', methods=('GET', 'POST'), defaults={'id': None})
def edit(id):
    conn = get_db_connection()

    # If editing, fetch item
    item = None
    if id:
        item = conn.execute('SELECT * FROM watches WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        price = request.form['price']
        style = request.form['style']
        movement_type = request.form['movement_type']
        bracelet_material = request.form['bracelet_material']
        bracelet_colour = request.form['bracelet_colour']
        clasp_type = request.form['clasp_type']
        clasp_material = request.form['clasp_material']
        case_diameter = request.form['case_diameter']
        case_material = request.form['case_material']
        water_resistance = request.form['water_resistance']
        bezel_material = request.form['bezel_material']
        crystal = request.form['crystal']
        dial = request.form['dial']
        power_reserve = request.form['power_reserve']
        image = request.files['image']
        description = request.form['description']
        stock = request.form['stock']

        image_data = None
        if image and image.filename != '':
            image_data = image.read()  # Convert file to BLOB

        if id:  # Update existing item
            if image_data:
                conn.execute('UPDATE watches SET name = ?,brand = ?, price = ?, style = ?, movement_type = ?,'
                             ' bracelet_material = ?, bracelet_colour = ?, clasp_type = ?, clasp_material = ?, '
                             'case_diameter = ?, case_material = ?, water_resistance = ?, bezel_material = ?,'
                             'crystal = ?, dial = ?, power_reserve = ?, image = ?, description = ?, stock = ?'
                             'WHERE id = ?',
                             (name, brand, price, style, movement_type, bracelet_material, bracelet_colour, clasp_type,
                              clasp_material, case_diameter, case_material, water_resistance, bezel_material, crystal,
                              dial, power_reserve, image_data, description, stock, id))
            else:
                conn.execute('UPDATE watches SET name = ?,brand = ?, price = ?, style = ?, movement_type = ?,'
                             ' bracelet_material = ?, bracelet_colour = ?, clasp_type = ?, clasp_material = ?, '
                             'case_diameter = ?, case_material = ?, water_resistance = ?, bezel_material = ?,'
                             'crystal = ?, dial = ?, power_reserve = ?, description = ?, stock = ?'
                             'WHERE id = ?',
                             (name, brand, price, style, movement_type, bracelet_material, bracelet_colour, clasp_type,
                              clasp_material, case_diameter, case_material, water_resistance, bezel_material, crystal,
                              dial, power_reserve, description, stock, id))
        else:  #add new watch
            conn.execute('INSERT INTO watches (name, brand, price, style, movement_type, bracelet_material, '
                              'bracelet_colour, clasp_type, clasp_material, case_diameter, case_material, '
                              'water_resistance, bezel_material, crystal, dial, power_reserve, image, description,'
                              'stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (name, brand, price, style, movement_type, bracelet_material, bracelet_colour,
                                    clasp_type, clasp_material, case_diameter, case_material, water_resistance,
                                    bezel_material, crystal, dial, power_reserve, image_data, description, stock))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', item=item)

# Delete an item
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM watches WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Fetch image from database
@app.route('/image/<int:id>')
def get_image(id):
    conn = get_db_connection()
    item = conn.execute('SELECT image FROM watches WHERE id = ?', (id,)).fetchone()
    conn.close()

    if item and item['image']:
        return send_file(io.BytesIO(item['image']), mimetype='image/jpeg')
    return '', 404  # Return 404 if no image is found


# Display all users
# When I have the page in - this will show on the admin page
@app.route('/users')
def users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users)


# Delete user
@app.route('/delete_user/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Cart
# Add to cart
@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    # initialise the session cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # Check if the user is logged in
    if 'username' not in session:
        flash('You need to log in to add to cart.', category='error')
        return redirect(url_for('login'))

    # Check if the product is already in the cart
    cart = session['cart']
    if id in cart:
        flash('Watch already in your cart.', category='info')
    else:
        # Add the watch ID to the cart
        cart.append(id)
        session['cart'] = cart  # Update session data
        flash('Watch added to your cart.', category='success')

    return redirect(url_for('view_cart'))


@app.route('/cart')
def view_cart():
    # Retrieve cart from the session
    cart = session.get('cart', [])

    # Fetch watch details for the IDs in the cart
    conn = get_db_connection()
    watches = [conn.execute('SELECT * FROM watches WHERE id = ?', (id,)).fetchone() for id in cart]
    conn.close()

    # Filter out None values in case of invalid or deleted watch IDs
    watches = [watch for watch in watches if watch is not None]

    return render_template('cart.html', watches=watches)


# Remove product from cart
@app.route('/remove_from_cart/<int:id>', methods=['POST'])
def remove_from_cart(id):
    # Get the current cart from session
    cart = session.get('cart', [])
    if id in cart:
        # Remove product from cart if it exists
        cart.remove(id)
        session['cart'] = cart
        flash('product removed from your cart.', category='success')
    else:
        # Flash an error message if product is not in cart
        flash('product not found in your cart.', category='error')
    return redirect(url_for('view_cart'))


if __name__ == '__main__':
    app.run(debug=True)
