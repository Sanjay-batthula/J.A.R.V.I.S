import csv
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
# cursor.execute(query)

# query = "INSERT INTO sys_command VALUES (null,'Firefox','C:\\Program Files\\Mozilla Firefox\\firefox.exe')"
# cursor.execute(query)
# con.commit()

# query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
# cursor.execute(query)

# query = "INSERT INTO web_command VALUES (null,'Canva', 'https://www.canva.com/')"
# cursor.execute(query)
# con.commit()

#cursor.execute("UPDATE web_command SET name = LOWER(name);")
#con.commit() 

#cursor.execute("UPDATE sys_command SET name = LOWER(name);")
#con.commit() 

#Create a table with the desired columns
#cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL)''')

# Specify the column indices you want to import (0-based index)
# Example: Importing the 1st and 3rd columns
desired_columns_indices = [0, 15]

# Use the correct path for contacts.csv
csv_path = '../contacts.csv'
# If contacts.csv is in the parent directory, use:
# csv_path = '../contacts.csv'

# Read data from CSV and insert into SQLite table for the desired columns
with open(csv_path, 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        selected_data = [row[i] for i in desired_columns_indices]
        cursor.execute(''' INSERT INTO contacts (id, 'name', 'mobile_no') VALUES (null, ?, ?);''', tuple(selected_data))

con.commit()

# Ensure the contacts table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id integer primary key,
        name VARCHAR(200),
        mobile_no VARCHAR(255),
        email VARCHAR(255) NULL
    )
''')
con.commit()

# Delete all existing contacts
# cursor.execute("DELETE FROM contacts;")
# con.commit()

# # Add your new contacts here. Replace with your desired names and numbers.
# cursor.execute("INSERT INTO contacts VALUES (null, 'sanjay', '+91 98662 02655', null)")
# cursor.execute("INSERT INTO contacts VALUES (null, 'srikruthi', '+91 95739 28999', null)")
# cursor.execute("INSERT INTO contacts VALUES (null, 'srivatsa javangula maam', '+91 93464 64760', null)")
# con.commit()

#query = 'vishakha'
#query = query.strip().lower()

# cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])

con.close()