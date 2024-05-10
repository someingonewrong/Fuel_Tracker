import sqlite3
import csv
from datetime import date
from datetime import datetime

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
litres_input_split = []
litres = 0
c_litres = 0
cost_output = 0
cost_input_split = []
cost = 0
p_cost = 0
output_line = []
distinct_vehicles = []
import_file_name = ''
row = []
menu_running = True
menu_option = ''

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

def print_tracker():
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

    print('Order by (v)ehicle, (d)ate (m)ileage, (l)itres, (c)ost, (cu)rrency or Enter to order by id:')
    order_input = input().lower()

    if order_input == 'v':
        sql_fetch += ' ORDER BY vehicle'
    if order_input == 'd':
        sql_fetch += ' ORDER BY date'
    if order_input == 'm':
        sql_fetch += ' ORDER BY mileage'
    if order_input == 'l':
        sql_fetch += ' ORDER BY litres'
    if order_input == 'c':
        sql_fetch += ' ORDER BY cost'
    if order_input == 'cu':
        sql_fetch += ' ORDER BY currency'

    print('\nTracker contains:')
    for line in cursor.execute(sql_fetch):
        print(str(line[0]) + '\t' + 
              str(line[1]) + '\t' + 
              str(line[2]) + '\t' + 
              str(line[3]) + '\t' + 
              str(line[4]) + '\t' + 
              str(line[5]) + '\t' + 
              str(line[6]))



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
        print_tracker()
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
