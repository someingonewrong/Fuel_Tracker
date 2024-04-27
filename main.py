import sqlite3
from datetime import date

con = sqlite3.connect("fuel_tracker.db")
cursor = con.cursor()

today = date.today()
currency = "GBP"

table_input = "INSERT INTO tracker (vehicle, date, mileage, litres, cost, currency) VALUES ('vivaro', '{TODAY}', '0', '0', '0', '{CURRENCY}')".format(TODAY = today, CURRENCY = currency)

cursor.execute("CREATE TABLE IF NOT EXISTS tracker (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle TEXT, date DATE, mileage INTEGER, litres INTEGER, cost INTEGER, currency TEXT)")

# cursor.execute(table_input)

line = cursor.execute("SELECT id, vehicle, date FROM tracker").fetchall()
# line = cursor.execute("DELETE FROM tracker WHERE vehicle = 'vivaro'")

print(line)

con.commit()
con.close()