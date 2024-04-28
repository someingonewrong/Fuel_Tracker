import sqlite3
from datetime import date

con = sqlite3.connect("fuel_tracker.db")  #connect to the database
cursor = con.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS tracker (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle TEXT, date DATE, mileage INTEGER, litres INTEGER, cost INTEGER, currency TEXT)")
# Create table tracker within data base

today = date.today()
currency = "GBP"
vehicles = []
vehicle_new = False
vehicle_output = ''
mileage_last = 0

table_input = "INSERT INTO tracker (vehicle, date, mileage, litres, cost, currency) VALUES ('{VEHICLE}', '{TODAY}', '{MILAGE}', '{LITRES}', '{COST}', '{CURRENCY}')"
# Lince to add row to table tracker, needs a .format()

line = list(cursor.execute("SELECT DISTINCT vehicle FROM tracker"))

for item in line:
    vehicles.append(item[0])

if len(vehicles) == 0 :
    vehicle_output = "No entries into the table, enter NEW to create new vehicle:"
else:
    vehicle_output = "Please select from vehicles in table already"
    for item in vehicles:
        vehicle_output += ', ' + item.title()
    vehicle_output += ' or enter NEW to add a new vehicle:'

print(vehicle_output)
vehicle_input = input().lower()

if vehicle_input in vehicles:
    pass
elif vehicle_input == 'new':
    vehicle_new = True
else:
    print('Invalid input')
    exit()

mileage_last = cursor.execute("SELECT mileage FROM tracker WHERE vehicle = '{}' ORDER BY mileage DESC LIMIT 1".format(vehicle_input)).fetchone()[0]

print('Enter mileage, last milage for {} is {}:'.format(vehicle_input, mileage_last))
try:
    mileage_input = int(input())
except:
    print('Not integer')
    exit()



print(mileage_last)






con.commit()
con.close()