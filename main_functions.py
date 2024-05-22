import sqlite3
import csv
from datetime import date
from datetime import datetime
from matplotlib import pyplot as plt

currency_list = ['CHF', 'EUR', 'GBP', 'SEK', 'DKK', 'CZK', 'PLN', 'TRY']

class Record:
    def __init__(self, vehicle, date, mileage, litres, cost, currency):
        self.vehicle = vehicle
        self.date = date
        self.mileage = mileage
        self.litres = litres
        self.cost = cost
        self.currency = currency

    def insert_record(self):
        table_input = "INSERT INTO tracker (vehicle, date, mileage, litres, cost, currency) VALUES (?,?,?,?,?,?)"
        inputs = [self.vehicle, self.date, self.mileage, self.litres, self.cost, self.currency]

        con = sqlite3.connect("fuel_tracker.db")
        con.execute(table_input, inputs)
        con.commit()
        con.close()

con = sqlite3.connect("fuel_tracker.db")  #connect to the database
cursor = con.cursor()

record = Record('a','a',0,0,0,'GBP')

cursor.execute("""CREATE TABLE IF NOT EXISTS tracker 
               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
               vehicle TEXT, 
               date DATE, 
               mileage INTEGER, 
               litres INTEGER, 
               cost INTEGER, 
               currency TEXT)""")


def int_convert(input):  # takes 0.00 and converts to 000 with checks2
    input_split = input.split('.')
    if len(input_split) > 2 or int(input_split[0]) < 0: raise
    try:
        output = int(input_split[0]) * 100
        if len(input_split[1]) == 1: output += int(input_split[1]) * 10
        elif int(input_split[1]) < 0: raise
        else: output += int(input_split[1])
    except:
        try: output = int(input)
        except: raise
    return output

def current_vehicles():  # Returns a list of existing vehicles in the database
    distinct_vehicles = list(cursor.execute("SELECT DISTINCT vehicle FROM tracker"))
    vehicles = []
    for item in distinct_vehicles:
        vehicles.append(item[0])
    return vehicles

def add_new_vehicle():  # Gets input for new vehicle and mileage
    print('\nEnter new vehicle: ')
    record.vehicle = input().lower()
    if len(record.vehicle) == 0: raise
    print('Enter mileage:')
    record.mileage = int(input())

def existing_vehicle(vehicles):  # input for existing vehicle and checks mileage
    vehicle = "\nPlease select from vehicles in table already"
    for item in vehicles:
        vehicle += ', ' + item.upper()
    vehicle += ' or enter NEW to add a new vehicle:'

    print(vehicle)
    vehicle_input = input().lower()

    if vehicle_input == 'new':
        try: add_new_vehicle()
        except: raise
        return
    elif vehicle_input in vehicles:
        record.vehicle = vehicle_input
        mileage_last = cursor.execute("SELECT mileage FROM tracker WHERE vehicle = '{}' ORDER BY mileage DESC LIMIT 1".format(vehicle_input)).fetchone()[0]
        print('Enter mileage, last milage for {} is {}:'.format(record.vehicle, mileage_last))
        record.mileage = int(input())
        if record.mileage < mileage_last:
            print('New mileage cannot be smaller than last mileage.')
            raise
    else:
        print('Invalid Vehicle')
        raise

def cost_input():
    record.cost = input().upper()

    if record.cost in currency_list:
        print('Enter cost of fuel:')
        cost_input()
    else:
        try: record.cost = int_convert(record.cost)
        except: raise

def new_input():
    record.date = date.today()
    record.currency = 'GBP'
    vehicles = current_vehicles()
    if len(vehicles) == 0:
        try: add_new_vehicle()
        except:
            print('Not integer')
            return
    else:
        try: existing_vehicle(vehicles)
        except ValueError:
            print('Invalid mileage')
            return
        except: 
            print('Invalid vehicle')
            return

    print('Enter litres of fuel (must be 0.00):')
    record.litres = input()

    try:record.litres = int_convert(record.litres)
    except:
        print('Incorrect format')
        return

    print('Enter cost of fuel or currency code if not GBP:')
    try: cost_input()
    except: print('Incorrect format, valid currencies ' + str(currency_list))
    
    record.insert_record()

    print('\nInputting:')
    print('Vehicle  - ', record.vehicle)
    print('Date     - ', record.date)
    print('Mileage  - ', record.mileage)
    print('Litres   - ', record.litres)
    print('Cost     - ', record.cost)
    print('Currency - ', record.currency)

new_input()

print('\nBye Bye')

con.commit()
con.close()