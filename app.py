from flask import Flask, render_template, request, redirect, url_for, flash
import logging, mysql.connector

app = Flask(__name__)
app.secret_key = "flash_message"

# Configure database connection
config = {
    'user': 'root',
    'password': 'root',
    'port': 3306,
    'host': 'localhost',
    'database': 'harta'
}

# Create a connection object
mysql = mysql.connector.connect(**config)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def main():
    try:
        # Fetch customers data
        cur_harta = mysql.cursor()
        cur_harta.execute("SELECT * FROM harta")
        harta_data = cur_harta.fetchall()
        cur_harta.close()

        # # Fetch treatments data
        # cur_hartalain = mysql.cursor()
        # cur_hartalain.execute("SELECT * FROM hartalain")
        # hartalain_data = cur_hartalain.fetchall()
        # cur_hartalain.close()

        # hartalain=hartalain_data
        return render_template('index.html', harta=harta_data )
    except Exception as e:
        logging.exception("Error retrieving data:")
        flash("An error occurred while retrieving data.")
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
        logging.exception("Error retrieving customer data:")
        flash("An error occurred while retrieving customer data.")
        return redirect(url_for('harta'))


@app.route('/insert_harta', methods=['POST'])
def insert_harta():
    try:
        tahun = request.form['tahun']
        failNo = request.form['failNo']
        jenis = request.form['jenis']
        kategori = request.form['kategori']

        cur = mysql.cursor()
        cur.execute("INSERT INTO harta (tahun, failNo, jenis, kategori) VALUES ( %s, %s, %s, %s)",
                    (tahun, failNo, jenis, kategori))
        mysql.commit()

        flash("Harta Berjaya Diisytihar!")
        return redirect(url_for('harta'))

    except Exception as e:
        logging.exception("Harta Gagal Diisytihar!")
        logging.error("Tahun: %s, Nombor Fail: %s, Jenis: %s, Kategori: %s", tahun, failNo, jenis, kategori)
        flash("Harta Gagal Diisytihar!")
        return redirect(url_for('harta'))


@app.route('/update_harta', methods=['POST'])
def update_harta():
    if request.method == 'POST':
        try:
            bil = request.form['bil']
            tahun = request.form['tahun']
            failNo = request.form['failNo']
            jenis = request.form['jenis']
            kategori = request.form['kategori']

            cur = mysql.cursor()
            cur.execute("UPDATE harta SET tahun=%s, failNo=%s, jenis=%s, kategori=%s WHERE bil=%s",
                        (tahun, failNo, jenis, kategori, bil))
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



# @app.route('/hartalain')
# def hartalain():
#     try:
#         cur = mysql.cursor()
#         cur.execute("SELECT * FROM hartalain")
#         data = cur.fetchall()
#         cur.close()
#         return render_template('hartalain.html', hartalain=data)
#     except Exception as e:
#         #logging.exception("Error retrieving treatment data:")
#         logging.exception("Harta Lain Gagal Dipapar!")
#         flash("Ralat Semasa Memapar Harta!")
#         return redirect(url_for('hartalain'))
#
# @app.route('/insert_treatment', methods=['POST'])
# def insert_treatment():
#     if request.method == "POST":
#         try:
#             treatment_name = request.form['treatment_name']
#             category = request.form['category']
#             description = request.form['description']
#             price = request.form['price']
#
#             cur = mysql.cursor()
#             cur.execute("INSERT INTO hartalain (treatment_name, category, description, price) VALUES (%s, %s, %s, %s)",
#                         (treatment_name, category, description, price))
#             mysql.commit()
#
#             flash("Treatment Data Inserted Successfully")
#             return redirect(url_for('hartalain'))
#
#         except Exception as e:
#             logging.exception("Error inserting treatment data:")
#             logging.error("Treatment Name: %s, Category: %s, Description: %s, Price: %s", treatment_name, category, description, price)
#             flash("An error occurred while inserting treatment data.")
#             return redirect(url_for('hartalain'))
#
# @app.route('/update_treatment', methods=['POST'])
# def update_treatment():
#     if request.method == 'POST':
#         try:
#             treatment_id = request.form['treatment_id']
#             treatment_name = request.form['treatment_name']
#             category = request.form['category']
#             description = request.form['description']
#             price = request.form['price']
#
#             cur = mysql.cursor()
#             cur.execute("UPDATE hartalain SET treatment_name=%s, category=%s, description=%s, price=%s WHERE treatment_id=%s",
#                         (treatment_name, category, description, price, treatment_id))
#             flash("Treatment Data Updated Successfully")
#             mysql.commit()
#             return redirect(url_for('hartalain'))
#         except Exception as e:
#             logging.exception("Error updating treatment data:")
#             flash("An error occurred while updating treatment data.")
#             return redirect(url_for('hartalain'))
#
# @app.route('/delete_treatment/<int:treatment_id>', methods=['POST'])
# def delete_treatment(treatment_id):
#     try:
#         flash("Treatment Record Has Been Deleted Successfully")
#         cur = mysql.cursor()
#         cur.execute("DELETE FROM hartalain WHERE treatment_id=%s", (treatment_id,))
#         mysql.commit()
#         return redirect(url_for('hartalain'))
#     except Exception as e:
#         logging.exception("Error deleting treatment data:")
#         flash("An error occurred while deleting treatment data.")
#         return redirect(url_for('hartalain'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
