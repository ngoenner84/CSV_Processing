import csv
import sys
from sys import argv


# This program takes in a specific CSV file for Round 2.1 BMQC raw data results,
# checks for dynamic force as measured in right-hand columns, processes the
# data, and outputs into the accepted OCP BMQC Round 2.1 raw data file format.

# Check for command-line usage
if len(argv) != 3:
    sys.exit("Usage: python parse.py input.csv output.csv")

fieldnames = [
    'p_drop_psi',
    'p_socket_psi',
    'p_plug_psi',
    'q_lpm',
    'temp_c',
    'dist_mm',
    'force_n',
    'velocity_mms',
    'SPEED_mms',
    'is_movedir_mating',
    'offest_radial_mm',
    'offset_angle_deg',
    'is_flowdir_s2p',
    'cycle_num',
    'test_owner',
    'test_id',
    'ocp_test_spec',
    'test_date_ymd',
    'plug_id',
    'socket_id',
    'plug_vendor',
    'socket_vendor']

try:
    with open(argv[2], "w", newline = '') as outfile:
        writer = csv.DictWriter(outfile, fieldnames = fieldnames)
        writer.writeheader()
except:
    print("Could not write header.")
    exit(-1)

# Read data file into temp file, one line at a time. If encounter
# a value in 'Force Max' field, move data into two separate lines
# to conform with OCP standard formatting.

with open(argv[1], "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        temp = []
        temp.append(row)
        if temp[0]['FORCE MAX'] != '':
            temp.append(temp[0].copy())
            temp[0]['dist_mm'] = temp[0]['DIST @MIN']
            temp[0]['force_n'] = temp[0]['FORCE MIN']
            temp[1]['dist_mm'] = temp[0]['DIST @MAX']
            temp[1]['force_n'] = temp[0]['FORCE MAX']
            temp[1]['is_movedir_mating'] = 0

        # Write reformatted line(s) to output file

        try:
            with open(argv[2], "a", newline = '') as outfile:
                writer = csv.DictWriter(outfile, fieldnames = fieldnames, extrasaction = 'ignore')
                for data in temp:
                    writer.writerow(data)
        except:
            print("Could not write to file.")