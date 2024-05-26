import sqlite3
import csv
from datetime import date
from datetime import datetime
from datetime import timedelta
import os.path as op
from os import remove
import glob
import urllib.request
from matplotlib import pyplot as plt
# import matplotlib.dates as mdates
# import numpy as np
from currency_converter import ECB_URL, CurrencyConverter
import time
import multiprocessing


# check if vehicle valid
# check date is valid or fetch today
# check if mileage higher or valid
# check litres are valid
# check if cost valid or is curreny

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

cursor.execute("""CREATE TABLE IF NOT EXISTS tracker 
               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
               vehicle TEXT, 
               date DATE, 
               mileage INTEGER, 
               litres INTEGER, 
               cost INTEGER, 
               currency TEXT)""")
# Create table tracker within data base

today = date.today()
date_output = ''
currency_output = "GBP"
currency_list = ['CHF', 'EUR', 'GBP', 'SEK', 'DKK', 'CZK', 'PLN', 'TRY']
vehicles = []
vehicle = ''
vehicle_new = False
vehicle_output = ''
mileage_last = 0
mileage_output = 0
litres_output = 0
cost_output = 0
distinct_vehicles = []
menu_running = True
menu_option = ''

def fetch_ecb_file(filename):
    print('\nUpdating converter file...')
    try:
        urllib.request.urlretrieve(ECB_URL, filename)
        print('File updated')
    except: raise

def update_ecb_file():
    if date.today().weekday() in [0,1,2,3,4]:
        temp = datetime.today()
    elif date.today().weekday() == 5:
        temp = datetime.today() - timedelta(days=1)
    else:
        temp = datetime.today() - timedelta(days=2)
    temp = temp.strftime('%Y%m%d')
    filename = "ecb_" + str(temp) + ".zip"
    
    try:
        if not op.isfile(filename):
            fetch_ecb_file(filename)
    except:
        print('Failed to update file')
    
    file_names = glob.glob('ecb_*.zip', recursive=True)
    file_names.sort(reverse = True)

    for file in file_names:
        try:
            c = CurrencyConverter(file, fallback_on_missing_rate=True)
            print('Loaded file ' + file)
            break
        except: pass

    for file_delete in file_names:
        if file_delete != file:
            remove(file_delete)
    
    return c


def int_convert(input):
    input_split = input.split('.')
    if len(input_split) > 2 or int(input_split[0]) < 0:
        raise
    try:
        output = int(input_split[0]) * 100
        if len(input_split[1]) == 1:
            output += int(input_split[1]) * 10
        elif int(input_split[1]) < 0: raise
        else:
            output += int(input_split[1])
    except:
        try: output = int(input) * 100
        except: raise
    return output

def draw_graph(sql_line, c):
    y = []
    x = []
    sql_line += ' ORDER BY date'
    plt.gca().xaxis
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=20))
    for line in cursor.execute(sql_line):
        try:
            if int(line[5]) != 0:
                if line[6] != 'GBP':
                    converted = c.convert(int(line[5]), line[6], 'GBP', date=datetime.strptime(line[2], '%Y-%m-%d'))
                    y.append(round((int(converted)/int(line[4])), 2))
                else: y.append(round((int(line[5])/int(line[4])), 2))
                x.append(line[2])
        except: pass
    
    plt.xlabel("date")
    plt.ylabel("fuel ppl")
    plt.title('Fuel price over time')
    plt.plot(x, y)
    plt.show()


def print_tracker(c):
    vehicles = []
    distinct_vehicles = list(cursor.execute("SELECT DISTINCT vehicle FROM tracker"))
    vehicle = "\nSelect which vehicle to display"
    sql_fetch = 'SELECT * FROM tracker '
    for item in distinct_vehicles:
        vehicle += ', ' + item[0].upper()
        vehicles.append(item[0])
    vehicle += ' or Enter for all:'

    print(vehicle)
    vehicle_input = input().lower()

    if vehicle_input in vehicles:
        sql_fetch += 'WHERE vehicle = \'' + vehicle_input + '\''

    litres_total = 0
    cost_total = 0
    fuel_price_average = 0
    lines = 0
    veh_current = ''
    veh_previous = ''
    mileage_current = 0
    mileage_previous = 0
    mileage_diff = 0
    mpg = 0
    

    print('\nTracker contains:')
    for line in cursor.execute(sql_fetch):
        if line[6] != 'GBP':
            converted = c.convert(int(line[5]), line[6], 'GBP', date=datetime.strptime(line[2], '%Y-%m-%d'))
        else:
            converted = line[5]
        try: fuel_price = round((int(converted)/int(line[4])), 2)
        except: fuel_price = 0

        veh_previous = veh_current
        veh_current = str(line[1])
        mileage_previous = mileage_current
        mileage_current = int(line[3])
        mileage_diff = mileage_current - mileage_previous
        cost_total += int(converted)
        litres_total += int(line[4])
        fuel_price_average += fuel_price
        lines += 1

        if line[6] != 'GBP':
            gallons = int(line[4]) / 454.609
            mpg = mileage_diff / gallons

            print(str(line[0]) + '\t' + 
                  str(line[1]) + '\t' + 
                  str(line[2]) + '\t' + 
                  str(line[3]) + '\t' + 
                  str(round((line[4]/100), 2)) + '\t' + 
                  str(round((converted/100), 2)) + '\t' + 
                  'GBP' + '\t' + 
                  str(fuel_price) + '\t' + 
                  str(round(mpg, 2)) + '\t' +
                  str(round((line[5]/100), 2)) + '\t' + 
                  str(line[6]))
        elif veh_current == veh_previous:
            gallons = int(line[4]) / 454.609
            mpg = mileage_diff / gallons

            print(str(line[0]) + '\t' + 
                  str(line[1]) + '\t' + 
                  str(line[2]) + '\t' + 
                  str(line[3]) + '\t' + 
                  str(round((line[4]/100), 2)) + '\t' + 
                  str(round((line[5]/100), 2)) + '\t' + 
                  str(line[6]) + '\t' + 
                  str(fuel_price) + '\t' + 
                  str(round(mpg, 2)))
        else:
            cost_total += int(line[5])
            print(str(line[0]) + '\t' + 
                  str(line[1]) + '\t' + 
                  str(line[2]) + '\t' + 
                  str(line[3]) + '\t' + 
                  str(round((line[4]/100), 2)) + '\t' + 
                  str(round((line[5]/100), 2)) + '\t' + 
                  str(line[6]) + '\t' + 
                  str(fuel_price))
    
    litres_total = litres_total / 100
    cost_total = cost_total / 100
    fuel_price_average = round((fuel_price_average / lines), 2)

    print('Total: \t\t\t\t\t' + str(litres_total) + '\t' + str(cost_total) + '\t\t' + str(fuel_price_average))
    draw_graph(sql_fetch, c)


def new_input_tracker():
    distinct_vehicles = list(cursor.execute("SELECT DISTINCT vehicle FROM tracker"))
    vehicles = []
    mileage_last = 0
    vehicle_new = False
    currency_output = 'GBP'
    for item in distinct_vehicles:
        vehicles.append(item[0])

    if len(vehicles) == 0 :
        vehicle = "\nEnter new vehicle: "
        vehicle_new = True
    else:
        vehicle = "\nPlease select from vehicles in table already"
        for item in vehicles:
            vehicle += ', ' + item.upper()
        vehicle += ' or enter NEW to add a new vehicle:'

    print(vehicle)
    vehicle_input = input().lower()

    if vehicle_input in vehicles or len(vehicles) == 0: pass
    elif vehicle_input == 'new': vehicle_new = True
    else:
        print('Invalid input')
        return

    if vehicle_new:
        print('Enter new vehicle: ')
        vehicle_output = input().lower()
        print('Enter mileage:')
    else:
        vehicle_output = vehicle_input

    if vehicle_new == False:
        mileage_last = cursor.execute("SELECT mileage FROM tracker WHERE vehicle = '{}' ORDER BY mileage DESC LIMIT 1".format(vehicle_input)).fetchone()[0]
        print('Enter mileage, last milage for {} is {}:'.format(vehicle_output, mileage_last))

    try:
        mileage_output = int(input())
    except:
        print('Not integer')
        return

    if mileage_output < mileage_last:
        print('New mileage cannot be smaller than last mileage.')
        return

    print('Enter litres of fuel (must be 0.00):')
    litres_input = input()

    try:
        litres_output = int_convert(litres_input)
    except:
        print('incorrect format')
        return

    print('Enter cost of fuel or currency code if not GBP:')
    cost_input = input()

    if cost_input.upper() in currency_list:
        currency_output = cost_input.upper()
        print('Enter cost of fuel:')
        cost_input = input()

    try:
        cost_output = int_convert(cost_input)
    except:
        print('Incorrect format, valid currencies ' + str(currency_list))
        return

    record = Record(vehicle_output, today, mileage_output, litres_output, cost_output, currency_output)
    record.insert_record()

    print('\nInputting:')
    print('Vehicle  - ', record.vehicle)
    print('Date     - ', record.date)
    print('Mileage  - ', record.mileage)
    print('Litres   - ', record.litres)
    print('Cost     - ', record.cost)
    print('Currency - ', record.currency)

def import_csv():
    print('\nEnter file.csv to import:')
    import_file_name = input()

    try:
        csv_file = open(import_file_name, newline='')
        file = csv.reader(csv_file)
    except:
        print("File not found")
        return
    
    vehicle_output = import_file_name.split('.')[0]
    print('\nData added:')

    try:
        for row in file:
            date_output = str(datetime.strptime(row[0], "%d/%m/%y").date())
            mileage_output = row[1].strip('p')
            currency_output = 'GBP'
            litres_output = int_convert(row[3])

            if row[2].startswith('€'):
                currency_output = 'EUR'
                row[2] = row[2].strip('€')
            
            cost_output = int_convert(row[2])

            record = Record(vehicle_output, date_output, mileage_output, litres_output, cost_output, currency_output)
            record.insert_record()
            print(record.vehicle + '\t' + 
                  record.date + '\t' + 
                  str(record.mileage) + '\t' + 
                  str(record.litres) + '\t' + 
                  str(record.cost) + '\t' + 
                  record.currency)
    except:
        print('File format invalid, failed row:')
        print(row)
        return
    csv_file.close()

def sql_input():
    print('\nEnter SQL line:')
    sql_input = input()

    try:
        list = cursor.execute(sql_input)
        for line in list:
            print(line)
    except:
        try:
            cursor.execute(sql_input)
        except:
            print('Query failed')
            return
    
    print('\nQuery successful')

while menu_running:
    print('\nOptions (r)ead table, (i)mport csv, (n)ew entry, (s)ql query, (e)xit:')
    menu_option = input().lower()

    if menu_option == 'r':
        print_tracker(update_ecb_file())
    elif menu_option == 'i':
        import_csv()
    elif menu_option == 'n':
        new_input_tracker()
    elif menu_option == 's':
        sql_input()
    elif menu_option == 'e':
        menu_running = False

print('\nBye Bye')

con.commit()
con.close()
