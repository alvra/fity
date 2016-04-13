import re
import six


hexadecimals = '0123456789ABCDEF'


class LiteralSignature(object):
    def __init__(self, string, likeliness):
        self.string = string
        self.length = len(string)
        self.likeliness = likeliness

    def matches(self, string):
        return string.startswith(self.string)

    @classmethod
    def create(cls, string, likeliness=None):
        return cls(string, likeliness or len(string))


class RegexSignature(object):
    def __init__(self, regex, length, likeliness):
        self.regex = regex
        self.length = length
        self.likeliness = likeliness

    def matches(self, string):
        return self.regex.match(string) is not None

    @classmethod
    def compile(cls, pattern, length, likeliness, flags=re.DOTALL):
        return cls(re.compile(pattern, flags), length, likeliness)

    @classmethod
    def create(cls, signature):
        hexbytes = signature.split()
        pattern = b''.join(
            '.' if '?' in c else re.escape(six.int2byte(int(c, 16)))
            for c in hexbytes
        )
        signature = cls.compile(pattern, len(hexbytes), sum('?' not in c for c in hexbytes))
        signature.hexbytes = hexbytes
        return signature


class ExtractionError(Exception):
    pass


filetype_classes = set()


class FiletypeMeta(type):
    def __init__(cls, name, bases, dct):
        filetype_classes.add(cls)
        super(FiletypeMeta, cls).__init__(name, bases, dct)


class Filetype(six.with_metaclass(FiletypeMeta, object)):
    mimetype = NotImplemented
    extension = NotImplemented
    description = NotImplemented

    def __init__(self, file, properties, mimetype=None, extension=None, description=None):
        self.file = file
        self.properties = properties
        if mimetype is not None:
            self.mimetype = mimetype
        if extension is not None:
            self.extension = extension
        if description is not None:
            self.description = description

    def __getitem__(self, property):
        return self.properties[property]

    @classmethod
    def extract(cls, file):
        "Extract the filetype from a file."
        return cls(file, dict())

    @classmethod
    def detect(cls, file):
        """Returns zero or greater indiciting how likely the file matches this filetype.

        If the file is definitely not of this type, it must return zero.
        Otherwise it must return the number of bits that match,
        this is proportional to the information content in the detection
        and thus also to minus the natural logarithm of the probability
        a random file matches (up to a factor ln(2)).
        We call this number the likeliness.
        """
        try:
            signatures = cls.signatures
        except AttributeError:
            try:
                signatures = [cls.signature]
            except AttributeError:
                return 0
        length = max(s.length for s in signatures)
        start = file.read(length)
        for signature in sorted(signatures, key=lambda s: -s.likeliness):
            if signature.matches(start):
                return signature.likeliness
        return 0


filetype_classes.remove(Filetype)
Filetype.subclasses = filetype_classes


hexbytes = RegexSignature.create
literal = LiteralSignature.create
regexpr = RegexSignature.compile
