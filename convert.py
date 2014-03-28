'''
This utility script converts (row, col, value) records like this:

    2,6,9
    2,7,23
    2,8,74
    ...
    6,20,76
    6,21,27
    6,22,0

Into a tabular format like this:

,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22
2,9,23,74,225,351,434,513,666,710,890,776,610,435,166,100,46,1
3,12,29,53,166,250,369,370,428,549,625,618,516,386,179,101,51,5
4,9,30,79,214,350,460,478,568,677,743,700,448,473,207,138,42,2
5,9,16,84,171,294,342,435,470,552,594,642,518,350,182,95,54,2
6,13,27,93,224,402,568,693,560,527,374,364,223,139,89,76,27,0

The tabular format CSV can then be used with punchcard.py
'''

import csv

def process(path):
    with open(path, 'rb') as fp:
        reader = csv.reader(fp)
        csv_rows = list(reader)
    rows = set()
    cols = set()
    lookup = {}
    int_rows = all(x[0].isdigit() for x in csv_rows[1:])
    int_cols = all(x[1].isdigit() for x in csv_rows[1:])
    for row, col, value in csv_rows[1:]:
        if int_rows:
            row = int(row)
        if int_cols:
            col = int(col)
        rows.add(row)
        cols.add(col)
        lookup[(row, col)] = value
    rows = sorted(rows)
    cols = sorted(cols)
    result = [[''] + cols]
    for row in rows:
        data = [lookup.get((row, col), 0) for col in cols]
        result.append([row] + data)
    with open(path, 'wb') as fp:
        writer = csv.writer(fp)
        writer.writerows(result)

if __name__ == '__main__':
    import sys
    process(sys.argv[1])
