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
    'database': 'spars'
}

# Create a connection object
mysql = mysql.connector.connect(**config)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def main():
    try:
        # Fetch customers data
        cur_customers = mysql.cursor()
        cur_customers.execute("SELECT * FROM customers")
        customers_data = cur_customers.fetchall()
        cur_customers.close()

        # Fetch treatments data
        cur_treatments = mysql.cursor()
        cur_treatments.execute("SELECT * FROM treatments")
        treatments_data = cur_treatments.fetchall()
        cur_treatments.close()

        return render_template('index.html', customers=customers_data, treatments=treatments_data)
    except Exception as e:
        logging.exception("Error retrieving data:")
        flash("An error occurred while retrieving data.")
        return redirect(url_for('customers'))




@app.route('/customers')
def customers():
    try:
        cur = mysql.cursor()
        cur.execute("SELECT * FROM customers")
        data = cur.fetchall()
        cur.close()
        return render_template('customers.html', customers=data)
    except Exception as e:
        logging.exception("Error retrieving customer data:")
        flash("An error occurred while retrieving customer data.")
        return redirect(url_for('customers'))


@app.route('/insert_customer', methods=['POST'])
def insert_customer():
    try:
        name = request.form['name']
        treatment_name = request.form['treatment_name']
        phone = request.form['phone']

        cur = mysql.cursor()
        cur.execute("INSERT INTO customers (name, treatment_name, phone) VALUES (%s, %s, %s)",
                    (name, treatment_name, phone))
        mysql.commit()

        flash("Customer Data Inserted Successfully")
        return redirect(url_for('customers'))

    except Exception as e:
        logging.exception("Error inserting customer data:")
        logging.error("Name: %s, Treatment Name: %s, Phone: %s", name, treatment_name, phone)
        flash("An error occurred while inserting customer data.")
        return redirect(url_for('customers'))


@app.route('/update_customer', methods=['POST'])
def update_customer():
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']
            name = request.form['name']
            treatment_name = request.form['treatment_name']
            phone = request.form['phone']

            cur = mysql.cursor()
            cur.execute("UPDATE customers SET name=%s, treatment_name=%s, phone=%s WHERE customer_id=%s",
                        (name, treatment_name, phone, customer_id))
            flash("Customer Data Updated Successfully")
            mysql.commit()
            return redirect(url_for('customers'))
        except Exception as e:
            logging.exception("Error updating customer data:")
            flash("An error occurred while updating customer data.")
            return redirect(url_for('customers'))


@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        cur = mysql.cursor()
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
        mysql.commit()
        flash("Customer deleted Successfully")
        return redirect(url_for('customers'))
    except Exception as e:
        logging.exception("Error deleting customer data:")
        flash("An error occurred while deleting customer data.")
        return redirect(url_for('customers'))



@app.route('/treatments')
def treatments():
    try:
        cur = mysql.cursor()
        cur.execute("SELECT * FROM treatments")
        data = cur.fetchall()
        cur.close()
        return render_template('treatments.html', treatments=data)
    except Exception as e:
        logging.exception("Error retrieving treatment data:")
        flash("An error occurred while retrieving treatment data.")
        return redirect(url_for('treatments'))

@app.route('/insert_treatment', methods=['POST'])
def insert_treatment():
    if request.method == "POST":
        try:
            treatment_name = request.form['treatment_name']
            category = request.form['category']
            description = request.form['description']
            price = request.form['price']

            cur = mysql.cursor()
            cur.execute("INSERT INTO treatments (treatment_name, category, description, price) VALUES (%s, %s, %s, %s)",
                        (treatment_name, category, description, price))
            mysql.commit()

            flash("Treatment Data Inserted Successfully")
            return redirect(url_for('treatments'))

        except Exception as e:
            logging.exception("Error inserting treatment data:")
            logging.error("Treatment Name: %s, Category: %s, Description: %s, Price: %s", treatment_name, category, description, price)
            flash("An error occurred while inserting treatment data.")
            return redirect(url_for('treatments'))

@app.route('/update_treatment', methods=['POST'])
def update_treatment():
    if request.method == 'POST':
        try:
            treatment_id = request.form['treatment_id']
            treatment_name = request.form['treatment_name']
            category = request.form['category']
            description = request.form['description']
            price = request.form['price']

            cur = mysql.cursor()
            cur.execute("UPDATE treatments SET treatment_name=%s, category=%s, description=%s, price=%s WHERE treatment_id=%s",
                        (treatment_name, category, description, price, treatment_id))
            flash("Treatment Data Updated Successfully")
            mysql.commit()
            return redirect(url_for('treatments'))
        except Exception as e:
            logging.exception("Error updating treatment data:")
            flash("An error occurred while updating treatment data.")
            return redirect(url_for('treatments'))

@app.route('/delete_treatment/<int:treatment_id>', methods=['POST'])
def delete_treatment(treatment_id):
    try:
        flash("Treatment Record Has Been Deleted Successfully")
        cur = mysql.cursor()
        cur.execute("DELETE FROM treatments WHERE treatment_id=%s", (treatment_id,))
        mysql.commit()
        return redirect(url_for('treatments'))
    except Exception as e:
        logging.exception("Error deleting treatment data:")
        flash("An error occurred while deleting treatment data.")
        return redirect(url_for('treatments'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
