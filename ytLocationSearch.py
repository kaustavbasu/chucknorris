# -*- coding: utf-8 -*-

#    File name: ytLocation.py
#    Author: Kaustav Basu
#    Date created: 02/13/2019
#    Date last modified: 02/13/2019
#    Python Version: 3

#!/usr/bin/python

import os
import xlrd

script = 'python3 /Users/kaustavbasu/Desktop/API/crawls/location/yeezy/app.py'

# Main function
if __name__ == '__main__':
    inputFile = sys.argv[1]
    wb = xlrd.open_workbook(inputFile)
    sheet = wb.sheet_by_index(0)
    for x in range(sheet.nrows):
        location = sheet.cell_value(x, 0)
        cmd = script + ' ' + location
        print(cmd)
        #os.system(cmd)
