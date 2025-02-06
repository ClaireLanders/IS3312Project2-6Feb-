from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import io

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# Home page to display all watches and users at the moment!
# it currently only shows name and description, but I will add brand and other stuff later
@app.route('/')
def index():
    conn = get_db_connection()
    watches = conn.execute('SELECT id, name, description FROM watches').fetchall()
    users = conn.execute('SELECT id, username, email, role FROM users').fetchall()
    conn.close()
    return render_template('index.html', watches=watches, users=users)

# Add or Edit a watch item
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
        image = request.files['image']

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


if __name__ == '__main__':
    app.run(debug=True)
