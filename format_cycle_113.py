import csv
import sys
from sys import argv


# This program takes in parsed CSV file (from "parse.py" output) for Round 2.1 BMQC raw data results,
# interprets the data line-by-line, then outputs a CSV file with headers matching Excel report template
# file for sorting and copy/paste into the master results file, section 11.1-11, entry for Table 11.3 results.

# Check for command-line usage
if len(argv) != 3:
    sys.exit("Usage: python format_cycle_113.py input.csv output.csv")

fieldnames = [
    'Plug',
    'Socket',
    'Plug Identifier',
    'Socket Identifier',
    'Config',
    'Set Speed (mm/s)',
    'Test Sequence',
    'Cycle #',
    'Force Mate',
    'Force Demate',
    'No binding',
    'Functional',
    'No leaks',
    'No damage'
    ]

csv_out = []

# Sequence key identifies lines from raw data that apply to the desired output file, and also abbreviates to comply with the desired output.

sequence_key = {'11.3-3': 3, '11.3-5': 5, '11.3-7': 7, '11.3-8': 8, '11.3-14': 14, '11.3-20': 20, '11.3-24': 24, '11.3-26': 26, '11.3-28': 28}

# Offset key inedexes/transforms data from raw file to preferred format of output file

offset_key = {'0': 'A', '4.65': 'R', '5.25': 'C'}

try:
    with open(argv[2], "w", newline = '') as outfile:
        writer = csv.DictWriter(outfile, fieldnames = fieldnames)
        writer.writeheader()
except:
    print("Could not write header.")

# Read data file into temp file, one line at a time. If encounter
# a value corresponding to dynamic force test, as noted in "sequence_key" per BMQC Spec,
# re-shuffle data into output template format.

def main():
    with open(argv[1], "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:

            # Check for a valid Test Sequence reading in 'sequence_key' dictionary. If not dynamic force, skip row.

            if row['test_id'] in sequence_key.keys():
                force = abs((float(row['force_n'])))
                match = 0

                # Check that Plug Vendor, Socket Vendor, Config, ID #'s, and Test Sequence match. If so, add force output at stage to entry.

                for line in range(len(csv_out)):
                    if (
                        row['plug_vendor'] == csv_out[line]['Plug'] and
                        row['socket_vendor'] == csv_out[line]['Socket'] and
                        sequence_key[row['test_id']] == csv_out[line]['Test Sequence'] and
                        offset_key[row['offest_radial_mm']] == csv_out[line]['Config'] and
                        row['plug_id'] == csv_out[line]['Plug Identifier'] and
                        row['socket_id'] == csv_out[line]['Socket Identifier']
                        ):
                            update_values(line, force, row)
                            match = 1
                            break

                # Initialize new entry to csv_out output file with common fields, specify index of output file, and add the force at the given stage.

                if match == 0:
                    new_entry = {
                        'Plug': row['plug_vendor'],
                        'Socket': row['socket_vendor'],
                        'Plug Identifier': row['plug_id'],
                        'Socket Identifier': row['socket_id'],
                        'Config': offset_key[row['offest_radial_mm']],
                        'Set Speed (mm/s)': round(float(row['SPEED_mms'])),
                        'Test Sequence': sequence_key[row['test_id']],
                        'No binding': '',
                        'Force Mate': '',
                        'Force Demate': ''
                        }
                    csv_out.append(new_entry)
                    new_index = len(csv_out) - 1
                    update_values(new_index, force, row)

        # Write csv_out to output file

        try:
            with open(argv[2], "a", newline = '') as outfile:
                writer = csv.DictWriter(outfile, fieldnames = fieldnames, extrasaction = 'ignore')
                for data in csv_out:
                    writer.writerow(data)
        except:
            print("Could not write to file.")

def update_values(line, force, row):
    if force > 266: # Bind is defined as a force > 266N
        csv_out[line]['No binding'] = 'F'
    elif force < 266 and csv_out[line]['No binding'] != 'F': # Do not overwrite a previous "Fail" with a "Pass" if no De-Mate bind
        csv_out[line]['No binding'] = 'P'

    # Default values to "Pass," will require manual review of data observations to re-write these to "Fail"

    csv_out[line]['Functional'] = 'P'
    csv_out[line]['No leaks'] = 'P'
    csv_out[line]['No damage'] = 'P'

    # Check for mate vs. de-mate direction to determine appropriate place to store data in output file.

    if row['is_movedir_mating'] == '1': # Found a Mate force, add to appropriate place in output file.
        csv_out[line]['Force Mate'] = force

    elif row['is_movedir_mating'] == '0': # Found a De-mate force, add to appropriate place in output file.
        csv_out[line]['Force Demate'] = force

if __name__ == "__main__":
    main()


