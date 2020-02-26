#!/usr/bin/env python

import os
import sys
from shutil import copyfile

import fnv


def get_sample_data():
    """
    Quick, make some sample data!
    """
    sample_passwords = open('sample_passwords.txt', 'r').readlines()
    sample_passwords = [ passw.strip() for passw in sample_passwords ]
    hashes = convert_to_fnv(sample_passwords)

    return hashes


def convert_to_fnv(data):
    """
    Convert from string, to utf-8 byte, to fnv1a-128, to hex
    """
    result = []
    for string in data:
        hexed = format(fnv.hash(bytes(string, 'utf-8')), 'x')
        result.append(hexed)
    return result


def find_fnv_matches(passwords, hashes, **kwargs):
    """
    Given a list of passwords, convert them to fnv1a-128 and find their matching hashes (if any)

    And yes, a reverse lookup via dict is SIGNIFICANTLY faster
    """
    hash_dict = {str(value): str(index) for index, value in enumerate(hashes)}

    result = {}
    for password in passwords:
        hexed = format(fnv.hash(bytes(password, 'utf-8')), 'x')

        if hash_dict.get(hexed):
            print(f"FOUND A MATCH FOR {password}: {hexed}")
            result[hexed] = password

    write_data_to_file(result, **kwargs)


def write_data_to_file(data, **kwargs):
    """
    Write matches to file in '^{key}:{value}$' format
    """
    filename = kwargs["filename"] if kwargs.get("filename") else "output.txt"
    # copyfile(filename, f'{filename}.bak')
    with open(filename, 'w') as file:
        for key, value in data.items():
            file.write(f'{key}:{value}\n')


if __name__ == "__main__":
    """
    Usage ./cracker.py passwords_to_test_against.txt hashes_to_crack.txt
    """
    if len(sys.argv) < 3:
        print("USAGE: python cracker.py passwords.txt hashes.txt")
        exit(1)

    passwords = open(sys.argv[1], 'br').readlines()
    hashes = open(sys.argv[2], 'r').readlines()
    # hashes = get_sample_data()  # Only for testing
    clean_passwords = [passw.decode('latin-1').strip() for passw in passwords]
    clean_hashes = [hash.strip() for hash in hashes]

    find_fnv_matches(clean_passwords, clean_hashes)

    print("Done processing")
