import sqlite3
import csv
from datetime import date
from datetime import datetime

con = sqlite3.connect("fuel_tracker.db")  #connect to the database
cursor = con.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS tracker (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle TEXT, date DATE, mileage INTEGER, litres INTEGER, cost INTEGER, currency TEXT)")
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
table_input = "INSERT INTO tracker (vehicle, date, mileage, litres, cost, currency) VALUES (?,?,?,?,?,?)"
distinct_vehicles = []
import_file_name = ''
row = []
menu_running = True
menu_option = ''

def print_tracker():
    print('\nTracker contains:')
    for line in cursor.execute('SELECT * FROM tracker'):
        print(line)

def new_input_tracker():
    distinct_vehicles = list(cursor.execute("SELECT DISTINCT vehicle FROM tracker"))
    for item in distinct_vehicles:
        vehicles.append(item[0])

    if len(vehicles) == 0 :
        vehicle = "Enter new vehicle: "
        vehicle_new = True
    else:
        vehicle = "Please select from vehicles in table already"
        for item in vehicles:
            vehicle += ', ' + item.title()
        vehicle += ' or enter NEW to add a new vehicle:'

    print(vehicle)
    vehicle_input = input().lower()

    if vehicle_input in vehicles or len(vehicles) == 0:
        print('here')
        pass
    elif vehicle_input == 'new':
        vehicle_new = True
        print('here 2')
    else:
        print('Invalid input')
        exit()

    if vehicle_new == True:
        print('Enter new vehicle: ')
        vehicle_output = input().lower()
    else:
        vehicle_output = vehicle_input

    if vehicle_new == False:
        mileage_last = cursor.execute("SELECT mileage FROM tracker WHERE vehicle = '{}' ORDER BY mileage DESC LIMIT 1".format(vehicle_input)).fetchone()[0]

    print('Enter mileage, last milage for {} is {}:'.format(vehicle_output, mileage_last))
    try:
        mileage_input = int(input())
        mileage_output = mileage_input
    except:
        print('Not integer')
        exit()

    if mileage_input < mileage_last:
        print('New mileage cannot be smaller than last mileage.')
        exit()

    print('Enter litres of fuel (must be 0.00):')
    litres_input_split = input().split('.')

    if len(litres_input_split) != 2:
        print('Incorrect format')
        exit()

    try:
        litres = int(litres_input_split[0])
        c_litres = int(litres_input_split[1])
    except:
        print('incorrect format')
        exit()

    if len(litres_input_split[1]) != 2 or litres < 0 or c_litres < 0:
        print('Incorrect format')
        exit()

    litres_output = (litres * 100) + c_litres


    print('Enter cost of fuel or currency code if not GBP:')
    cost_input = input().split('.')

    if cost_input[0].upper() in currency_list:
        currency_output = cost_input[0].upper()
        print('Enter cost of fuel:')
        cost_input = input().split('.')

    if len(cost_input) != 2:
        print('Incorrect format, valid currencies ' + str(currency_list))
        exit()

    try:
        cost = int(cost_input[0])
        p_cost = int(cost_input[1])
    except:
        print('incorrect format')
        exit()

    if len(cost_input[1]) != 2 or cost < 0 or p_cost < 0:
        print('Incorrect format')
        exit()

    cost_output = (cost * 100) + p_cost

    print('\nInputting:')
    print('Vehicle  - ', vehicle_output)
    output_line.append(vehicle_output)
    print('Date     - ', today)
    output_line.append(today)
    print('Mileage  - ', mileage_output)
    output_line.append(mileage_output)
    print('Litres   - ', litres_output)
    output_line.append(litres_output)
    print('Cost     - ', cost_output)
    output_line.append(cost_output)
    print('Currency - ', currency_output)
    output_line.append(currency_output)

    cursor.execute(table_input, output_line)
    currency_output = 'GBP'

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
    output_line = []
    print('\nData added:')

    try:
        for row in file:
            date_output = str(datetime.strptime(row[0], "%d/%m/%y").date())
            mileage_output = row[1].strip('p')

            try:
                litres_input_split = row[3].split('.')
                if len(row[3].split('.')[1]) == 1:
                    litres_output = (int(litres_input_split[0]) * 100) + (int(litres_input_split[1]) * 10)
                else:
                    litres_output = (int(litres_input_split[0]) * 100) + int(litres_input_split[1])
            except:
                litres_output = int(row[3]) * 100

            try:
                cost_input_split = row[2].split('.')
                if len(row[2].split('.')[1]) == 1:
                    cost_output = (int(cost_input_split[0]) * 100) + (int(cost_input_split[1]) * 10)
                else:
                    cost_output = (int(cost_input_split[0]) * 100) + int(cost_input_split[1])
            except:
                cost_output = int(row[2]) * 100

            output_line = [vehicle_output, date_output, mileage_output, litres_output, cost_output, currency_output]
            cursor.execute(table_input, output_line)
            print(output_line)
    except:
        print('File format invalid, failed row:')
        print(row)
        return
    csv_file.close()

def sql_input():
    print('\nEnter SQL line:')
    sql_input = input()
    if_continue = True

    try:
        # print(cursor.execute(sql_input))
        for line in cursor.execute(sql_input):
            print(line)
            if_continue = False
    except: pass
    try:
        if if_continue == True:
            cursor.execute(sql_input)
    except:
        print('Error')
        return

while menu_running:
    print('\nOptions (p)rint table, (i)mport csv, (n)ew entry, (s)ql query, (e)xit:')
    menu_option = input().lower()

    if menu_option == 'p':
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