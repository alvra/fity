import bz2file


class Bzip2File(bz2file.BZ2File):
    def __init__(self, file):
        super(Bzip2File, self).__init__(file, mode='r')
