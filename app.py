from flask import Flask, render_template, request, session, flash, redirect, url_for, \
    make_response
import logging
import pymysql
import requests
from werkzeug.utils import secure_filename
from datetime import timedelta
from flask import send_file
import pandas as pd
import tempfile
import os
app = Flask(__name__)
app.secret_key = "flash_message"

# Configure session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# Set session timeout to 5 minutes

# Configure database connection
config = {
    'user': 'root',
    'password': 'Hanum2002@',
    'port': 3306,
    'host': 'localhost',
    'database': 'harta'
}

connection = pymysql.connect(**config)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not validate_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed. Please try again.')
            return redirect(url_for('login'))
        email = request.form['email']
        password = request.form['password']

        # Logging the username and password for debugging
        logging.debug(f"Email: {email}, Password: {password}")

        if email == 'admin' and password == 'admin':
            # Admin login
            # Inside the login route, after successful authentication
            session['name'] = ['name']
            session['admin'] = True
            session['email'] = 'admin'
            flash('Admin login successful')
            return redirect(url_for('main'))

        # Check if the user exists in the database and validate credentials
        try:
            cur = connection.cursor()
            cur.execute("SELECT * FROM user WHERE email = %s AND password = %s",
                        (email, password))
            curUser = cur.fetchone()
            cur.close()

            if user:
                # User login
                session['email'] = curUser[1]  # Assuming email is at index 1 in the user tuple
                flash('User login successful')
                return redirect(url_for('main'))
            else:
                flash('Invalid credentials')

        except Exception as e:
            logging.exception("Error during login")
            flash('Login failed')

    return render_template('login.html')


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         if request.method == 'POST':
#             # Validate reCAPTCHA
#             recaptcha_response = request.form.get('g-recaptcha-response')
#             if not validate_recaptcha(recaptcha_response):
#                 flash('reCAPTCHA verification failed. Please try again.')
#                 return redirect(url_for('signup'))
#         name = request.form['name']
#         nric = request.form['nric']
#         email = request.form['email']
#         password = request.form['psw']
#         repeat_password = request.form['psw-repeat']
#
#         # Simple validation
#         if password != repeat_password:
#             flash('Passwords do not match')
#             return redirect(url_for('signup'))
#
#         # Insert into database
#         try:
#             cur = connection.cursor()
#             # Insert user data into the database
#             cur.execute("INSERT INTO user (name, nric, email, password) VALUES (%s, %s, %s, %s)",
#                         (name, nric, email, password))
#             connection.commit()
#             cur.close()
#
#             flash('Account successfully created')
#             return redirect(url_for('login'))
#         except Exception as e:
#             logging.exception("Error during signup")
#             flash('Signup failed')
#             return redirect(url_for('signup'))
#
#     # This part is necessary to handle GET requests and POST requests that do not satisfy conditions
#     return render_template('signup.html')


def validate_recaptcha(response):
    secret_key = '6LdO3jIpAAAAABSvzaRxVQ1ydFfKM2JxmejIfZq_'  # Replace with your actual Secret Key
    payload = {'secret': secret_key, 'response': response}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = r.json()
    return result['success']


@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()

    # Redirect to the login page
    return redirect(url_for('login'))


@app.route('/main')
def main():
    try:
        if 'email' not in session:
            flash('You need to log in first!')
            return redirect(url_for('login'))

        email = session['email']
        if email == 'admin':
            # Admin can see all user harta information
            cur = connection.cursor()
            # cur.execute("SELECT * FROM harta")
            cur.execute(
                "SELECT harta.*, user.name FROM harta JOIN user ON harta.email = user.email")
            data = cur.fetchall()
            cur.close()
            return render_template('admin_index.html', harta=data)
        else:
            # Non-admin user can see their own harta information
            cur = connection.cursor()
            cur.execute("SELECT * FROM harta WHERE email=%s", (email,))
            data = cur.fetchall()
            cur.close()
            return render_template('user_index.html', harta=data)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("An error occurred while fetching harta data.")
        return redirect(url_for('harta'))


@app.route('/harta')
def harta():
    try:
        if 'email' not in session:
            flash('You need to log in first.')
            return redirect(url_for('login'))

        email = session['email']
        if email == 'admin':
            # Admin can see all user harta information
            # cur = mysql.cursor()
            cur = connection.cursor()
            # cur.execute("SELECT * FROM harta")
            cur.execute(
                "SELECT harta.*, user.name FROM harta JOIN user ON harta.email = user.email")
            hartaData = cur.fetchall()

            cur.execute(
                "SELECT * FROM user")
            userData = cur.fetchall()

            cur.close()
            # Fetch jenis options from the database (replace this with your actual query)
            jenis_options = ["Tanah", "Kereta", "Motosikal"]
            # Fetch kategori options from the database (replace this with your actual query)
            kategori_options = ["Sendiri", "Bersama"]
            name = session.get('name', 'User')

            return render_template('harta_admin.html', harta=hartaData, user=userData, name=name,
                                   jenis_options=jenis_options,
                                   kategori_options=kategori_options)


        else:
            # Non-admin user can see their own harta information
            # cur = mysql.cursor()
            cur = connection.cursor()
            cur.execute("SELECT * FROM harta WHERE email=%s", (email,))
            data = cur.fetchall()
            cur.close()
            # Fetch jenis options from the database (replace this with your actual query)
            jenis_options = ["Tanah", "Kereta", "Motosikal"]
            # Fetch kategori options from the database (replace this with your actual query)
            kategori_options = ["Sendiri", "Bersama"]
            name = session.get('name', 'User')

            return render_template('harta_user.html', harta=data, name=name,
                                   jenis_options=jenis_options,
                                   kategori_options=kategori_options)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("An error occurred while fetching harta data.")
        return redirect(url_for('harta'))


ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt'}  # Add allowed file extensions


@app.route('/download_harta/<int:bil>')
def download_harta(bil):
    try:
        # Fetch jenis options from the database (replace this with your actual query)
        jenis_options = ["Tanah", "Kereta", "Motosikal"]

        # Fetch kategori options from the database (replace this with your actual query)
        kategori_options = ["Sendiri", "Bersama"]

        cur = connection.cursor()
        cur.execute("SELECT file_data, filename FROM harta WHERE bil = %s", (bil,))
        result = cur.fetchone()

        if result is None:
            # Flash a message or handle the error if the entry is not found
            flash("File not found.")
            return redirect(url_for('harta'))

        file_data, original_filename = result
        cur.close()

        if not allowed_file(original_filename):
            # Flash a message or handle the error if the file extension is not allowed
            flash("Invalid file extension for download.")
            return redirect(url_for('harta'))

        # Ensure a valid filename is used for download
        if not original_filename:
            original_filename = f"file_{bil}.bin"  # Provide a default filename if none is found

        # Create a response with the PDF data
        response = make_response(file_data)

        # Set the Content-Type header to indicate that the response contains a PDF file
        response.headers['Content-Type'] = 'application/pdf'

        # Set the Content-Disposition header to suggest a filename for the browser to use
        response.headers['Content-Disposition'] = f'inline; filename={original_filename}'

        # Return the response
        return response

    except Exception as e:
        logging.exception("An error occurred while processing the file download for 'harta'.")
        logging.error("Error details: %s", str(e))
        flash("An error occurred while processing the file download.")
        return redirect(url_for('harta'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/insert_harta', methods=['POST'])
def insert_harta():
    try:
        # Check if the current user is an admin
        email = session['email']
        if email == 'admin':
            email = request.form['email']
            tahun = request.form['tahun']
            failNo = request.form['failNo']
            namaPasangan = request.form['namaPasangan']
            jenis = request.form['jenis']
            kategori = request.form['kategori']

            # Check if the post-request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']

            # If a user does not select file, the browser also submits an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()

                # Insert harta into the database
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO harta (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s)",
                    (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email))
                connection.commit()

                flash("Harta Berjaya Diisytihar!")
                return redirect(url_for('harta'))

            else:
                flash("Invalid file type. Allowed file types are: pdf, png, jpg, jpeg, gif")
                return redirect(request.url)

        else:
            email = session['email']
            tahun = request.form['tahun']
            failNo = request.form['failNo']
            namaPasangan = request.form['namaPasangan']
            jenis = request.form['jenis']
            kategori = request.form['kategori']

            # Check if the post-request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']

            # If a user does not select file, the browser also submits an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()

                # Insert harta into the database
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO harta (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s)",
                    (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email))
                connection.commit()

                flash("Harta Berjaya Diisytihar!")
                return redirect(url_for('harta'))

            else:
                flash("Invalid file type. Allowed file types are: pdf, png, jpg, jpeg, gif")
                return redirect(request.url)


    except Exception as e:
        logging.exception("An error occurred while processing the file upload for 'harta'.")
        logging.error("Error details: %s", str(e))
        logging.error("Tahun: %s, Nombor Fail: %s, namaPasangan=%s, Jenis: %s, Kategori: %s", tahun, failNo,
                      namaPasangan, jenis, kategori)
        flash("Harta Gagal Diisytihar! An error occurred.")
        return redirect(url_for('harta'))


@app.route('/get_username', methods=['POST'])
def get_username():
    email = request.form.get('email')
    cur = connection.cursor()
    cur.execute("SELECT name FROM user WHERE email = %s", [email])
    data = cur.fetchone()
    cur.close()
    return data[0] if data else ''



@app.route('/update_harta', methods=['POST'])
def update_harta():
    if request.method == 'POST':
        try:
            bil = request.form['bil']
            tahun = request.form['tahun']
            failNo = request.form['failNo']
            namaPasangan = request.form['namaPasangan']
            jenis = request.form['jenis']
            kategori = request.form['kategori']

            # cur = mysql.cursor()
            cur = connection.cursor()
            cur.execute(
                "UPDATE harta SET tahun=%s, failNo=%s, namaPasangan=%s, jenis=%s, kategori=%s WHERE bil=%s",
                (tahun, failNo, namaPasangan, jenis, kategori, bil))
            flash("Harta Berjaya Dikemas Kini!")
            connection.commit()
            return redirect(url_for('harta'))
        except Exception as e:
            logging.exception("An error occurred while updating 'harta'.")
            logging.error("Error details: %s", str(e))
            flash("Harta Gagal Dikemas Kini! An error occurred.")
            return redirect(url_for('harta'))


@app.route('/delete_harta/<int:bil>', methods=['POST'])
def delete_harta(bil):
    try:
        email = session['email']

        # Check if the user is an admin or owns the harta entry
        if 'admin' in session and session['admin']:
            # Admin can delete any harta entry
            cur = connection.cursor()
            cur.execute("DELETE FROM harta WHERE bil=%s", (bil,))
        else:
            # Regular user can only delete their own harta entry
            cur = connection.cursor()
            cur.execute("DELETE FROM harta WHERE bil=%s AND email=%s", (bil, email))

        connection.commit()
        flash("Harta Berjaya Dipadam!")
        return redirect(url_for('harta'))

    except Exception as e:
        logging.exception("Harta Gagal Dipadam!")
        flash("Ralat Semasa Memadam Harta!")
        return redirect(url_for('harta'))


@app.route('/user')
def user():
    try:
        if 'email' not in session:
            flash('You need to sign up first.')
            return redirect(url_for('login'))

        email = session['email']
        if email == 'admin':
            # Admin can see all user harta information
            # cur = mysql.cursor()
            cur = connection.cursor()
            # cur.execute("SELECT * FROM harta")
            cur.execute("SELECT * FROM user WHERE is_active = TRUE")
            data = cur.fetchall()
            cur.close()
            name = session.get('name', 'User')

            return render_template('user.html', harta=data, name=name)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("An error occurred while fetching harta data.")
        return redirect(url_for('user'))


@app.route('/insert_user', methods=['POST'])
def insert_user():
    try:
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        nric = request.form['nric']

        # Insert harta into the database
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO user (email, password, name, nric) VALUES "
            "(%s, %s, %s, %s)",
            (email, password, name, nric))
        connection.commit()

        flash("Pengguna Berjaya DItambah!")
        return redirect(url_for('user'))

    except Exception as e:
        logging.exception("An error occurred while processing the file upload for 'harta'.")
        logging.error("Error details: %s", str(e))
        flash("Pengguna gagal ditambah!")
        return redirect(url_for('user'))


@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        try:
            bil = request.form['bil']
            email = request.form['email']
            password = request.form['password']
            name = request.form['name']
            nric = request.form['nric']

            cur = connection.cursor()
            cur.execute(
                "UPDATE user SET email=%s, password=%s, name=%s, nric=%s"
                "WHERE "
                "bil=%s",
                (password, name, nric, email, bil))

            flash("Maklumat Pengguna Berjaya DiKemas Kini!")
            connection.commit()
            return redirect(url_for('user'))
        except Exception as e:
            logging.exception("An error occurred while updating 'user'.")
            logging.error("Error details: %s", str(e))
            flash("Maklumat Pengguna Gagal Dikemas Kini! An error occurred.")
            return redirect(url_for('user'))


@app.route('/delete_user/<int:bil>', methods=['POST'])
def delete_user(bil):
    try:
        cur = connection.cursor()
        # Set is_active to False instead of deleting the row
        cur.execute("UPDATE user SET is_active = FALSE WHERE bil = %s", (bil,))
        connection.commit()
        flash("Pengguna Berjaya Dipadam (Deactivated)!")
        return redirect(url_for('user'))

    except Exception as e:
        logging.exception("Pengguna Gagal Dipadam (Failed to Deactivate)!")
        flash("Ralat Semasa Memadam (Deactivating) Pengguna!")
        return redirect(url_for('user'))


@app.route('/export_users')
def export_users():
    # Query all user data from the database, including the is_active status
    cur = connection.cursor()
    cur.execute("SELECT bil, email, password, name, nric, is_active FROM user")
    users = cur.fetchall()
    cur.close()

    # Convert to DataFrame for easier Excel export
    df = pd.DataFrame(users, columns=['Bil', 'Email', 'Password', 'Nama Pengguna', 'Nombor IC', 'IsActive'])

    # Create a temporary directory and save the Excel file there
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)

        # Send the Excel file as attachment
        return send_file(tmp.name, as_attachment=True, download_name='users.xlsx')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        email = session['email']
        cur = connection.cursor()
        if request.method == "POST":
            if 'email' not in session:
                flash('You need to log in first.')
                return redirect(url_for('login'))

            # Non-admin user can see their own profile information
            # Get the updated data from the form
            password = request.form.get("password")

            # Update the user's data in the database
            cur.execute("UPDATE user SET password=%s WHERE email=%s", (password, email))
            connection.commit()

        # Fetch the user's data from the database
        cur.execute("SELECT * FROM user WHERE email=%s", (email,))
        data = cur.fetchone()
        cur.close()
        name = session.get('name', 'User')
        return render_template('profile.html', user=data, name=name)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("An error occurred while fetching harta data.")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
