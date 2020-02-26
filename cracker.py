import logging
import os
import threading
from shutil import copyfile

import fnv
import numpy as np

def get_sample_data():

    # sample_passwords = ['test1', 'test2', 'test3']
    sample_passwords = open('rockyou.txt', 'br').readlines()
    sample_passwords = [ str(passw).strip() for passw in sample_passwords ]
    hashes = convert_to_fnv(sample_passwords)

    # for password, hash in zip(sample_passwords, hashes):
    #     logging.debug("Before: ", password, "\n    After: ", hash)

    return sample_passwords, hashes


def convert_to_fnv(data):
    result = []
    for string in data:
        hexed = format(fnv.hash(bytes(string, 'utf-8')), 'x')
        result.append(hexed)
    return result


def spin_up_thread(function, thread_name, **kwargs):

    thread = threading.Thread(target=function, kwargs={"filename": f"thread{thread_name}.out", **kwargs})
    thread.start()
    return thread


def find_fnv_matches(passwords, hashes, **kwargs):

    hash_dict = {str(value): str(index) for index, value in enumerate(hashes)}

    result = {}
    for password in passwords:
        hexed = format(fnv.hash(bytes(password, 'utf-8')), 'x')

        if hash_dict.get(hexed):
            # print(f"FOUND A MATCH FOR {password}: {hexed}")
            result[password] = hexed

    write_data_to_file(result, **kwargs)


def write_data_to_file(data, **kwargs):

    filename = kwargs["filename"] if kwargs.get("filename") else "output.txt"
    with open(filename, 'w') as file:
        for key, value in data.items():
            file.write(f'{key}: {value}\n')


def join_all_data(filenames):
    copyfile('output.txt', 'output.bak')
    with open('output.txt', 'w') as output:
        for file in filenames:
            output.write(open(file, 'r').read())
            os.remove(file)


if __name__ == "__main__":
    sample_passwords, hashes = get_sample_data()

    num_threads = 64

    split_data = np.array_split(hashes, num_threads)

    threads = []
    for index in range(len(split_data)):
        threads.append(
            spin_up_thread(
                find_fnv_matches,
                str(index),
                passwords=sample_passwords,
                hashes=split_data[index]
            )
        )

    for thread in threads:
        thread.join()

    filenames = [f'thread{num}.out' for num in range(len(split_data))]
    join_all_data(filenames)

    print("Done processing")
