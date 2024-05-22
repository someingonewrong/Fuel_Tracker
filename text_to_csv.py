import csv

txt_file = open('temp.txt', newline='')
file = csv.reader(txt_file)

csv_file = open('gassy.csv', 'w', newline='')
list = []

for line in file:
    split_line = line[0].split('\t')
    str_line = str(split_line[0])+','+str(split_line[1])+','+str(split_line[2])+','+str(split_line[3])+'\n'
    list.append(str_line)

csv_file.writelines(list)

txt_file.close()
csv_file.close()
