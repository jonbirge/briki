#!/usr/bin/env python

def filter_ascii_lines(file_in, file_out):
    with open(file_in, 'r') as fin, open(file_out, 'w') as fout:
        for line in fin:
            if not contains_non_ascii(line):
                fout.write(line)

def contains_non_ascii(s):
    return any(ord(c) > 127 for c in s)

def main():
    file_in = input("Enter the name of the input file: ")
    file_out = input("Enter the name of the output file: ")
    filter_ascii_lines(file_in, file_out)
    print("Done!")

if __name__ == "__main__":
    main()
