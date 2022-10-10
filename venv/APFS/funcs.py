import math
import os
import re
import subprocess

BLOCKSIZE = 4096
FILENAMES = ["test.txt","Kopie.txt"]
SINGLE_FILE = "test.txt"
PATTERN_ELEMENT_SIZE = 8
PATH_TO_DMG = "/Users/apfstest/apfs.dmg"
PATH = "/Volumes/apfsimg/"

#START_OFFSET = 0x5000 #5GB
START_OFFSET = 0x0c805000 #10/50 GB


def create_pattern(total_size):
    replace_zeroes_with = b'\x00'

    number_elements = math.floor(total_size / PATTERN_ELEMENT_SIZE)
    padding = total_size % PATTERN_ELEMENT_SIZE

    pattern = ''
    for n in range(1, number_elements + 1):
        pattern_element = n.to_bytes(int(PATTERN_ELEMENT_SIZE / 2), 'big')
        pattern_element = pattern_element.replace(b'\x00', replace_zeroes_with)
        pattern_element = pattern_element.hex()
        pattern += pattern_element

    pattern += '0' * padding

    return pattern


def write_file_from_pattern(filename, pattern):
    file_path = os.path.join(PATH, filename)
    with open(file_path, 'w+') as f:
        f.write(pattern)
        f.close()
    sync()

def write_file_from_pattern_systemcall(filename, pattern):
    command = f'echo {pattern} > {PATH + filename}'
    subprocess.check_output(command,shell=True)
    sync()




def modify_file(filename, offset):
    file_path = os.path.join(PATH, filename)
    with open(file_path, 'r+') as f:
        f.seek(offset)
        old_version = int.from_bytes(bytes.fromhex(f.read(2)), 'big')
        new_version = (old_version + 1).to_bytes(1, 'big').hex()
        f.seek(offset)
        f.write(new_version)
        f.close()
    sync()


def sync():
    popen = subprocess.Popen("sync")


def get_offset():
    command = f'mmls {PATH_TO_DMG}'
    command = command.split()
    output = subprocess.check_output(command)
    output_decoded = output.decode("utf-8")
    x = re.search("disk image", output_decoded)
    offset_partiton_start = x.start() - 39
    return output_decoded[offset_partiton_start:offset_partiton_start + 10]


def get_superblock(offset):
    print(f"Using offset {offset}")
    command = f'pstat -o {offset} {PATH_TO_DMG}'
    command = command.split()
    output = subprocess.check_output(command)
    output_decoded = output.decode("utf-8")
    x = re.search("APSB Block Number: ", output_decoded)
    y = re.search("APSB oid: ", output_decoded)
    apsb_block = output_decoded[x.end():y.start() - 4]
    print(f"Current APSB Block Number: {apsb_block}")
    return apsb_block


def fls(offset, superblock, print_output):
    command = f"fls -o {offset} -B {superblock} {PATH_TO_DMG}"
    command = command.split()
    output = subprocess.check_output(command)
    output_decoced = output.decode("utf-8")
    if print_output:
        print(output_decoced)
    x = re.search(f"[0-9]*:\s{SINGLE_FILE}", output_decoced)
    y = re.search(f":\s{SINGLE_FILE}", output_decoced)
    file_inode = output_decoced[x.start():y.start()]
    print(f"File sits at Inode {file_inode}")
    return file_inode


def fls2(offset, superblock, print_output):
    file_inode = dict()
    command = f"fls -o {offset} -B {superblock} {PATH_TO_DMG}"
    command = command.split()
    output = subprocess.check_output(command)
    output_decoced = output.decode("utf-8")
    if print_output:
        print(output_decoced)
    for file in FILENAMES:
        x = re.search(f"[0-9]*:\s{file}", output_decoced)
        y = re.search(f":\s{file}", output_decoced)
        file_inode[file] = output_decoced[x.start():y.start()]

    for key in file_inode:
        print(f"File {key} sits at Inode {file_inode[key]}")
    return file_inode


def istat(offset, superblock, file_inode, print_output):
    command = f"istat -o {offset} -B {superblock} {PATH_TO_DMG} {file_inode}"
    command = command.split()
    output = subprocess.check_output(command)
    output_decoded = output.decode("utf-8")
    if print_output:
        print(output_decoded)

    a = re.search("init_size:(\s+([0-9]+\s+)+)", output_decoded)
    z = (output_decoded[a.start():a.end()])

    z = z.split("\n")
    z.remove(z[0])
    z.remove(z[-1])

    fileblocks = []

    for i in range(len(z)):
        fileblocks += z[i].split()

    int_fileblocks = [int(f) for f in fileblocks]
    physical_offsets = [hex(f * BLOCKSIZE + START_OFFSET) for f in int_fileblocks]

    pr = ""
    for j, i in enumerate(int_fileblocks):
        pr += "Offset: " + str(i * BLOCKSIZE) + ", Physical Offset:" + str(physical_offsets[j]) + ", "

    print(f"File is in block(s) {int_fileblocks}, which should be {pr} (Blocksize:{BLOCKSIZE})\n ")

    return physical_offsets


def copy_file():
    command = f"cp -c {PATH + FILENAMES[0]} {PATH + FILENAMES[1]}"
    command = command.split()
    subprocess.call(command)
    sync()


def read_offsets(offsets):
    with open(PATH_TO_DMG, "rb") as f:
        if isinstance(offsets,list):
            for o in offsets:
                f.seek(int(o, 16))
                print(f"{o} : {f.read(BLOCKSIZE)}")
        else:
            f.seek(int(offsets, 16))
            print(f"{offsets} : {f.read(BLOCKSIZE)}")
