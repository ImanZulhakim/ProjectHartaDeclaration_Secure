from flask import Flask, render_template, request, session, flash, redirect, url_for
import mysql.connector
import mysql
import logging

app = Flask(__name__)
app.secret_key = "flash_message"

# Configure database connection
config = {
    'user': 'root',
    'password': 'Hanum2002@',
    'port': 3306,
    'host': 'localhost',
    'database': 'harta'
}

# Create a connection object
mysql = mysql.connector.connect(**config)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder authentication logic
        if username == "admin" and password == "password":
            return redirect(url_for('main'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        repeat_password = request.form['psw-repeat']

        # Simple validation
        if password != repeat_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Insert into database
        try:
            cur = mysql.cursor()
            # Insert user data into the database
            cur.execute("INSERT INTO user (email, password) VALUES (%s, %s)",
                        (email, password))
            mysql.commit()
            cur.close()

            flash('Account successfully created')
            return redirect(url_for('login'))
        except Exception as e:
            logging.exception("Error during signup")
            flash('Signup failed')
            return redirect(url_for('signup'))

    # This part is necessary to handle GET requests and POST requests that do not satisfy conditions
    return render_template('signup.html')



@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


@app.route('/main')
def main():
    try:
        cur = mysql.cursor()
        cur.execute("SELECT * FROM harta")
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', harta=data)
    except Exception as e:
        logging.exception("Ralat semasa mengambil data harta:")
        flash("Ralat berlaku semasa mengambil data harta.")
        return redirect(url_for('harta'))


@app.route('/harta')
def harta():
    try:
        cur = mysql.cursor()
        cur.execute("SELECT * FROM harta")
        data = cur.fetchall()
        cur.close()
        return render_template('harta.html', harta=data)
    except Exception as e:
        logging.exception("Ralat semasa mengambil data harta:")
        flash("Ralat berlaku semasa mengambil data harta.")
        return redirect(url_for('harta'))


@app.route('/insert_harta', methods=['POST'])
def insert_harta():
    try:
        tahun = request.form['tahun']
        failNo = request.form['failNo']
        namaPasangan = request.form['namaPasangan']
        jenis = request.form['jenis']
        kategori = request.form['kategori']

        cur = mysql.cursor()
        cur.execute("INSERT INTO harta (tahun, failNo, namaPasangan, jenis, kategori) VALUES ( %s, %s, %s, %s, %s)",
                    (tahun, failNo, namaPasangan, jenis, kategori))
        mysql.commit()

        flash("Harta Berjaya Diisytihar!")
        return redirect(url_for('harta'))

    except Exception as e:
        logging.exception("Harta Gagal Diisytihar!")
        logging.error("Tahun: %s, Nombor Fail: %s, namaPasangan=%s, Jenis: %s, Kategori: %s", tahun, failNo, namaPasangan, jenis, kategori)
        flash("Harta Gagal Diisytihar!")
        return redirect(url_for('harta'))


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

            cur = mysql.cursor()
            cur.execute("UPDATE harta SET tahun=%s, failNo=%s, namaPasangan=%s, jenis=%s, kategori=%s WHERE bil=%s",
                        (tahun, failNo, namaPasangan, jenis, kategori, bil))
            flash("Harta Berjaya Dikemas Kini!")
            mysql.commit()
            return redirect(url_for('harta'))
        except Exception as e:
            logging.exception("Harta Gagal Dikemas Kini!")
            flash("Ralat Semasa Mengemas Kini Harta!")
            return redirect(url_for('harta'))


@app.route('/delete_harta/<int:bil>', methods=['POST'])
def delete_harta(bil):
    try:
        cur = mysql.cursor()
        cur.execute("DELETE FROM harta WHERE bil=%s", (bil,))
        mysql.commit()
        flash("Harta Berjaya Dipadam!")
        return redirect(url_for('harta'))
    except Exception as e:
        logging.exception("Harta Gagal Dipadam!")
        flash("Ralat Semasa Memadam Harta!")
        return redirect(url_for('harta'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
