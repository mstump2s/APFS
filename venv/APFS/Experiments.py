from funcs import *


# Filesystem starts at offset 0x5000


def write_and_copy_file(size):
    write_file_from_pattern(PATH + FILENAMES[0], (create_pattern(size)))
    #write_file_from_pattern_systemcall(SINGLE_FILE, (create_pattern(size)))
    copy_file()


def exp5():
    offset = get_offset()
    superblock = get_superblock(offset)
    file_inode = fls2(offset, superblock, False)

    for key in file_inode:
        offsets = istat(offset, superblock, file_inode[key], False)
        with open(PATH_TO_DMG, 'rb') as f:
            for o in offsets:
                f.seek(int(o, 16), 0)
                print(f"{o} :{f.read(BLOCKSIZE)}")



def exp6(read):
    offset = get_offset()
    superblock = get_superblock(offset)
    file_inode = fls2(offset, superblock, True)
    for key in file_inode:
        offsets = istat(offset, superblock, file_inode[key], True)
        if read:
            read_offsets(offsets)

    for i in range(10):
        modify_file(PATH + FILENAMES[0], (4096*10)-5)
        superblock = get_superblock(offset)
        file_inode = fls2(offset, superblock, False)
        for key in file_inode:
            print(key)
            offsets = istat(offset, superblock, file_inode[key], True)
            if read:
                read_offsets(offsets)
def test():
    return 0

def exp8(read,modify):
    offset = get_offset()
    superblock = get_superblock(offset)
    file_inode = fls(offset, superblock, True)
    offsets = []
    offsets.append(istat(offset, superblock, file_inode, True))

    if(modify):
        for i in range(10):
            #modify_file(PATH + SINGLE_FILE, 1)
            superblock = get_superblock(offset)
            file_inode = fls(offset, superblock, True)
            offsets.append(istat(offset, superblock, file_inode, True))

        if read:
            for l in offsets:
                read_offsets(l)


def exp9(read):
    offset = get_offset()
    superblock = get_superblock(offset)
    file_inode = fls(offset, superblock, True)
    offsets = istat(offset, superblock, file_inode, True)

    print(offsets)
    if read:
        for o in offsets:
            read_offsets(o)
