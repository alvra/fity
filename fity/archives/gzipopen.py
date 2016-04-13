import gzip


class GzipFile(gzip.GzipFile):
    def __init__(self, file):
        super(GzipFile, self).__init__(fileobj=file, mode='r')
