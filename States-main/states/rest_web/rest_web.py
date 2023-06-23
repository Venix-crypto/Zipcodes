import mysql.connector
import pandas as pd
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__, static_url_path='')

conn = mysql.connector.connect(user='root', password='',
                               host='127.0.0.1',
                               database='zipcodes',
                               buffered=True)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS states (
        id INT AUTO_INCREMENT PRIMARY KEY,
        State VARCHAR(255),
        zip VARCHAR(255),
        Pop INT
    )
""")
zip_code_data = pd.read_csv('zip_code_database.csv')
for _, row in zip_code_data.iterrows():
    state = row['state']
    zip_code = row['zip']
    population = 0  # Initialize population as 0
    cursor.execute("INSERT INTO states (State, ZipCode, Population) VALUES (%s, %s, %s)",
                   (state, zip_code, population))

population_data = pd.read_csv('Populationstate.csv')
for _, row in population_data.iterrows():
    state = row['state']
    population = row['population']
    cursor.execute("UPDATE states SET Population = %s WHERE State = %s", (population, state))

conn.commit()

@app.route('/search', methods=['GET'])
def search():
    user = request.args.get('zip')
    return redirect(url_for('searchzip', searchzipcodes=user))


# Get data from the database based on the zip code
@app.route('/searchzipcodes/<searchzipcodes>')
def searchzip(searchzipcodes):
    cursor.execute("SELECT * FROM `states` WHERE zip=%s", [searchzipcodes])
    test = cursor.rowcount
    if test != 1:
        return searchzipcodes + " was not found"
    else:
        searched = cursor.fetchall()
        return 'Success! Here you go: %s' % searched


# Update state database population for a specified state
@app.route('/updatestatepop/<updateSTATE> <updatePOP>')
def updatestatepop(updateSTATE, updatePOP):
    cursor.execute("SELECT * FROM `states` WHERE State=%s", [updateSTATE])
    test = cursor.rowcount
    if test != 1:
        return updateSTATE + " was not found"
    else:
        cursor.execute("UPDATE `states` SET Pop = %s WHERE State= %s;", [updatePOP, updateSTATE])
        cursor.execute("SELECT * FROM `states` WHERE State=%s and Pop=%s", [updateSTATE, updatePOP])
        test1 = cursor.rowcount
        if test1 != 1:
            return updateSTATE + " failed to update"
        else:
            return 'Population has been updated successfully for State: %s' % updateSTATE


# Update webpage
@app.route('/update', methods=['POST'])
def update():
    user = request.form['ustate']
    user2 = request.form['upop']
    return redirect(url_for('updatestatepop', updateSTATE=user, updatePOP=user2))


# Root of web server and goes to template (login.html)
@app.route('/')
def root():
    return render_template('login.html')


# Main
if __name__ == '__main__':
    app.run(debug=True)
