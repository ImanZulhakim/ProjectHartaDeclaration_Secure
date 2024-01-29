from flask import Flask, render_template, request, session, flash, redirect, url_for, make_response
import logging
import pymysql
import requests
import openpyxl
from werkzeug.utils import secure_filename
from datetime import timedelta
from flask import send_file
import pandas as pd
import tempfile
import io

app = Flask(__name__)
app.secret_key = "flash_message"

# Configure session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Preventing cookie theft and XSS attacks.
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
# Set session timeout to 5 minutes

# Configure database connection
config = {
    'user': 'root',
    'password': 'root',
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
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not validate_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed. Please try again.', 'error')
            return redirect(url_for('login'))

        email = request.form['email']
        password = request.form['password']

        logging.debug(f"Email: {email}, Password: {password}")

        if email == 'admin' and password == 'System@dmin02':
            session['name'] = ['name']
            session['admin'] = True
            session['email'] = 'admin'
            flash('Admin login successful', 'success')
            return redirect(url_for('main'))

        try:
            cur = connection.cursor()
            cur.execute("SELECT * FROM user WHERE email = %s AND password = %s AND is_active = TRUE",
                        (email, password))
            curUser = cur.fetchone()
            cur.close()

            if curUser:
                session['email'] = curUser[1]  # Assuming email is at index 1 in the user tuple
                flash('User login successful', 'success')
                return redirect(url_for('main'))
            else:
                flash('Invalid credentials or inactive account', 'error')

        except Exception as e:
            logging.exception("Error during login")
            flash('Login failed', 'error')

    return render_template('login.html')


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
            flash("Anda perlu daftar masuk dahulu!", 'error')
            return redirect(url_for('login'))

        email = session['email']
        if email == 'admin':
            # Admin can see all user harta information
            cur = connection.cursor()
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
        flash("Ralat semasa mengambilkan data harta!", 'error')
        return redirect(url_for('harta'))


@app.route('/harta')
def harta():
    try:
        if 'email' not in session:
            flash('Anda perlu daftar masuk dahulu!', 'error')
            return redirect(url_for('login'))

        email = session['email']
        if email == 'admin':
            # Admin can see all user harta information
            cur = connection.cursor()
            cur.execute(
                "SELECT harta.*, user.name FROM harta JOIN user ON harta.email = user.email")
            hartaData = cur.fetchall()

            cur.execute("SELECT * FROM user WHERE is_active = TRUE")
            userData = cur.fetchall()
            cur.close()
            name = session.get('name', 'User')

            return render_template('harta_admin.html', harta=hartaData, user=userData, username=name)

        else:
            # Non-admin user can see their own harta information
            cur = connection.cursor()
            cur.execute("SELECT * FROM harta WHERE email=%s", (email,))
            data = cur.fetchall()
            cur.close()
            name = session.get('name', 'User')

            return render_template('harta_user.html', harta=data, name=name)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("Ralat semasa mengambilkan data harta!", 'error')
        return redirect(url_for('harta'))


ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'xslx'}  # Add allowed file extensions


@app.route('/download_harta/<int:bil>')
def download_harta(bil):
    try:

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
            file = request.files['file']

            # Check if the post-request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

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
                    "INSERT INTO harta (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email, last_modified_by, last_modified_at) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                    (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email, email))
                connection.commit()

                flash("Harta Berjaya Diisytihar!", "success")
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
                    "INSERT INTO harta (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email, last_modified_by, last_modified_at) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                    (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email, email))
                connection.commit()

                flash("Harta Berjaya Diisytihar!", "success")
                return redirect(url_for('harta'))

            else:
                flash("Invalid file type. Allowed file types are: pdf, png, jpg, jpeg, gif", "error")
                return redirect(request.url)


    except Exception as e:
        logging.exception("An error occurred while processing the file upload for 'harta'.")
        logging.error("Error details: %s", str(e))
        logging.error("Tahun: %s, Nombor Fail: %s, namaPasangan=%s, Jenis: %s, Kategori: %s", tahun, failNo,
                      namaPasangan, jenis, kategori)
        flash("Harta Gagal Diisytihar! Ralat berlaku.", "error")
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

            # Get the email of the user who is making the update
            email = session['email']

            # Check if the post-request has the file part
            if 'file' in request.files:
                file = request.files['file']

                # If a user does not select file, the browser also submits an empty part without filename
                if file.filename != '':
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_data = file.read()

                        # Update the harta entry and set last modification details
                        cur = connection.cursor()
                        cur.execute(
                            "UPDATE harta SET tahun=%s, failNo=%s, namaPasangan=%s, jenis=%s, kategori=%s, file_data=%s, filename=%s,last_modified_by=%s, "
                            "last_modified_at=NOW() WHERE bil=%s",
                            (tahun, failNo, namaPasangan, jenis, kategori, file_data, filename, email, bil))
                        flash("Harta Berjaya Dikemas Kini!", "success")
                        connection.commit()
                        return redirect(url_for('harta'))
                    else:
                        flash("Invalid file type. Allowed file types are: pdf, png, jpg, jpeg, gif", "error")
                        return redirect(request.url)

            # If no file is provided or the file is not valid, proceed with updating other data
            # Update the harta entry without modifying the file
            cur = connection.cursor()
            cur.execute(
                "UPDATE harta SET tahun=%s, failNo=%s, namaPasangan=%s, jenis=%s, kategori=%s, last_modified_by=%s, "
                "last_modified_at=NOW() WHERE bil=%s",
                (tahun, failNo, namaPasangan, jenis, kategori, email, bil))
            flash("Harta Berjaya Dikemas Kini!", "success")
            connection.commit()
            return redirect(url_for('harta'))

        except Exception as e:
            logging.exception("An error occurred while updating 'harta'.")
            logging.error("Error details: %s", str(e))
            flash("Harta Gagal Dikemas Kini! Ralat Berlaku.", "error")
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
        return redirect(url_for('harta'))

    except Exception as e:
        logging.exception("Harta Gagal Dipadam!")
        flash("Ralat Semasa Memadam Harta!", "error")
        return redirect(url_for('harta'))


@app.route('/user')
def user():
    try:
        if 'email' not in session:
            flash("Anda perlu daftar masuk dahulu!", "error")
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

            return render_template('user.html', user=data, name=name)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("Ralat semasa memaparkan data pengguna!", "error")
        return redirect(url_for('user'))


@app.route('/insert_user', methods=['POST'])
def insert_user():
    try:
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        nric = request.form['nric']

        # Insert user into the database
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO user (email, password, name, nric, last_modified_by, last_modified_at) VALUES "
            "(%s, %s, %s, %s, %s, NOW())",
            (email, password, name, nric, email))
        connection.commit()

        flash("Pengguna Berjaya Ditambah!", "success")
        return redirect(url_for('user'))

    except Exception as e:
        logging.exception("An error occurred while processing the file upload for 'user'.")
        logging.error("Error details: %s", str(e))
        flash("Pengguna gagal ditambah!", "error")
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

            # Get the email of the user who is making the update
            updater_email = session['email']

            # Check if the user is an admin
            if 'admin' in session and session['admin']:
                # Admin is updating the user, use admin's email as the last modifier
                updater_email = 'admin'

            # Update the user's data in the database and set last modification details
            cur = connection.cursor()
            cur.execute(
                "UPDATE user SET email=%s, password=%s, name=%s, nric=%s, "
                "last_modified_by=%s, last_modified_at=NOW() WHERE bil=%s",
                (email, password, name, nric, updater_email, bil))

            flash("Maklumat Pengguna Berjaya DiKemas Kini!", "success")
            connection.commit()
            return redirect(url_for('user'))
        except Exception as e:
            logging.exception("An error occurred while updating 'user'.")
            logging.error("Error details: %s", str(e))
            flash("Maklumat Pengguna Gagal Dikemas Kini! Ralat berlaku!.", "error")
            return redirect(url_for('user'))


@app.route('/delete_user/<int:bil>', methods=['POST'])
def delete_user(bil):
    try:
        cur = connection.cursor()

        # First, get the email of the user to be deleted
        cur.execute("SELECT email FROM user WHERE bil = %s", (bil,))
        user_data = cur.fetchone()
        if user_data is None:
            flash("Pengguna Tidak Dijumpai!", "error")
            return redirect(url_for('user'))

        user_email = user_data[0]

        # Delete all harta associated with this user
        cur.execute("DELETE FROM harta WHERE email = %s", (user_email,))

        # Set is_active to False for the user instead of deleting the row
        cur.execute("UPDATE user SET is_active = FALSE WHERE bil = %s", (bil,))

        connection.commit()
        flash("Pengguna dan harta berkenaan telah Berjaya Dipadam (Deactivated)!", "success")
        return redirect(url_for('user'))

    except Exception as e:
        logging.exception("Pengguna Gagal Dipadam (Failed to Deactivate)!")
        flash("Ralat Semasa Memadam (Deactivating) Pengguna dan Harta Berkenaan!", "error")
        return redirect(url_for('user'))


@app.route('/export_users')
def export_users():
    try:
        # Query all user data from the database, including the is_active status
        cur = connection.cursor()
        cur.execute("SELECT bil, email, password, name, nric, is_active, last_modified_by, last_modified_at FROM user")
        users = cur.fetchall()
        cur.close()
        # Convert to DataFrame for easier Excel export
        df = pd.DataFrame(users, columns=['Bil', 'Email', 'Password', 'Nama Pengguna', 'Nombor IC', 'IsActive', 'Modifikasi terakhir oleh',
                                          'Modifikasi terakhir pada'])

        # Create a temporary directory and save the Excel file there
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            df.to_excel(tmp.name, index=False)
            return send_file(tmp.name, as_attachment=True, download_name='users.xlsx')

    except Exception as e:
        logging.exception("An error occurred during user export:")
        logging.error("Error details: %s", str(e))
        flash(f"Ralat semasa mengeksport data pengguna!", "error")
        return redirect(url_for('user'))


@app.route('/export_harta')
def export_harta():
    try:
        cur = connection.cursor()
        query = "SELECT bil, tahun, failNo, namaPasangan, jenis, kategori, filename, email, last_modified_by, last_modified_at FROM harta"
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        flash("Data harta berjaya di eksport!", "success")
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['Bil', 'Tahun', 'Nombor Fail', 'Nama Pasangan', 'Jenis Perisytiharan Harta',
                                         'Kategori Perisytiharan Harta', 'Fail Sokongan', 'Email',
                                         'Last Modified By', 'Last Modified At'])

        # Create an in-memory Excel file
        excel_data = io.BytesIO()
        df.to_excel(excel_data, index=False)
        excel_data.seek(0)

        # Send the Excel file as an attachment
        return send_file(
            excel_data,
            as_attachment=True,
            download_name='harta.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logging.exception("An error occurred during harta export:")
        logging.error("Error details: %s", str(e))
        flash(f"Ralat semasa mengeksport data harta!", "error")
        return redirect(url_for('harta'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        email = session['email']
        cur = connection.cursor()
        if request.method == "POST":
            if 'email' not in session:
                flash("Anda perlu daftar masuk dahulu!", "error")
                return redirect(url_for('login'))

            # Non-admin user can see their own profile information
            # Get the updated data from the form
            password = request.form.get("password")

            # Update the user's data in the database
            cur.execute("UPDATE user SET password=%s WHERE email=%s", (password, email))
            connection.commit()
            flash("Kata Laluan berjaya ditukar!", "success")

        # Fetch the user's data from the database
        cur.execute("SELECT * FROM user WHERE email=%s", (email,))
        data = cur.fetchone()
        cur.close()
        name = session.get('name', 'User')
        return render_template('profile.html', user=data, name=name)

    except Exception as e:
        logging.exception("Error fetching harta data:")
        flash("Ralat semasa mengambilkan data pengguna!", "error")
        return redirect(url_for('login'))


@app.route('/simulate_unauthorized_access')
def simulate_unauthorized_access():
    # Simulate an unauthorized access attempt
    unauthorized_user_email = 'test@example.com'
    logging.warning(f"Unauthorized user manipulation attempt by {unauthorized_user_email}")
    return "Simulated Unauthorized Access"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
