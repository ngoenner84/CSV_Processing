import csv
import sys
from sys import argv


# This program takes in parsed CSV file (from "parse.py" output) for Round 2.1 BMQC raw data results,
# interprets the data line-by-line, then outputs a CSV file with headers matching Excel report template
# file for sorting and copy/paste into the master results file.

# Check for command-line usage
if len(argv) != 3:
    sys.exit("Usage: python format_1119.py input.csv output.csv")

fieldnames = [
    'Plug',
    'Socket',
    'Plug Identifier',
    'Socket Identifier',
    'Config',
    'Total Cycles',
    'Stage 1',
    'Stage 2',
    'Stage 3',
    'Stage 4',
    'Stage 5',
    'Stage 6',
    'Stage 7',
    ]

csv_out = []

position_key = {'67.900203': 'Stage 7', '72.400766': 'Stage 6', '78.401516': 'Stage 5', '88.400781': 'Stage 4', '92.901344': 'Stage 3', '97.001062': 'Stage 2', '110.740875': 'Stage 1'}

cycle_key = {'11.3-2': 0, '11.3-4': 0, '11.3-6': 0, '11.3-11': 40, '11.3-12': 40, '11.3-13': 40, '11.3-17': 80, '11.3-18': 80, '11.3-19': 80, '11.3-23': 120, '11.3-25': 120, '11.3-27': 120}

offset_key = {'0': 'A', '4.65': 'R', '5.25': 'C'}

try:
    with open(argv[2], "w", newline = '') as outfile:
        writer = csv.DictWriter(outfile, fieldnames = fieldnames)
        writer.writeheader()
except:
    print("Could not write header.")

# Read data file into temp file, one line at a time. If encounter
# a value corresponding to "Stage 1" thru "Stage 7" per BMQC Spec,
# re-shuffle data into output template format.

with open(argv[1], "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        in_temp = row

        # Check for a Static Force reading in 'dist_mm' key. If not static force, skip row.

        if in_temp['dist_mm'] in position_key.keys():
            match = 0
            stage = position_key[in_temp['dist_mm']]
            for line in range(len(csv_out)): # Check that Plug Vendor, Socket Vendor, Config, ID #'s, and Total Cycles match. If so, add force output at stage to entry.
                if (
                    in_temp['plug_vendor'] == csv_out[line]['Plug'] and
                    in_temp['socket_vendor'] == csv_out[line]['Socket'] and
                    cycle_key[in_temp['test_id']] == csv_out[line]['Total Cycles'] and
                    offset_key[in_temp['offest_radial_mm']] == csv_out[line]['Config'] and
                    in_temp['plug_id'] == csv_out[line]['Plug Identifier'] and
                    in_temp['socket_id'] == csv_out[line]['Socket Identifier']
                    ):
                    csv_out[line][stage] = float(in_temp['force_n']) * -1
                    match = 1;
                    break

            if match == 0: # Initialize new entry to csv_out output file with common fields, and add the singular force at the given stage.
                new_entry = {
                    'Plug': in_temp['plug_vendor'],
                    'Socket': in_temp['socket_vendor'],
                    'Plug Identifier': in_temp['plug_id'],
                    'Socket Identifier': in_temp['socket_id'],
                    'Config': offset_key[in_temp['offest_radial_mm']],
                    'Total Cycles': cycle_key[in_temp['test_id']],
                    stage: float(in_temp['force_n']) * -1
                    }
                csv_out.append(new_entry)

# Write csv_out to output file

try:
    with open(argv[2], "a", newline = '') as outfile:
        writer = csv.DictWriter(outfile, fieldnames = fieldnames, extrasaction = 'ignore')
        for data in csv_out:
            writer.writerow(data)
except:
    print("Could not write to file.")
