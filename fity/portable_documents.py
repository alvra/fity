import datetime
import re
import six
from collections import OrderedDict
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError
from dateutil.tz import tzutc, tzoffset
from dateutil.parser import parse as dateutil_parse
from .base import hexbytes, ExtractionError
from .categories import DocumentType


date_pattern = re.compile(
    r"(D:)?"
    r"(?P<year>\d{4})"
    r"(?P<month>\d{2})"
    r"(?P<day>\d{2})"
    r"(?P<hour>\d{2})"
    r"(?P<minute>\d{2})"
    r"(?P<second>\d{2})"
    r"(?P<offset>[+-zZ])?"
    r"(?P<offset_hour>\d{2})?"
    r"'?"
    r"(?P<offset_minute>\d{2})?"
    r"'?"
    r"$"
)


def parse_date(string):
    match = date_pattern.match(string)
    if not match:
        try:
            date = dateutil_parse(string)
        except ValueError:
            # we could not parse it, give up
            return None
        else:
            return date
    data = match.groupdict()
    # normalize values
    for key, value in data.iteritems():
        if value is None:
            pass
        elif key != 'offset':
            data[key] = int(value)
    # make timezone offset
    if data['offset'] in ('z', 'Z', None):
        data['tzinfo'] = tzutc()
    else:
        plusminus = 1 if data['offset'] == '+' else -1
        seconds = 3600 * data['offset_hour'] + 60 * data['offset_minute']
        data['tzinfo'] = tzoffset(None, plusminus * seconds)
    # remove unused data
    for k in ('offset', 'offset_hour', 'offset_minute'):
        del data[k]
    # done
    return datetime.datetime(**data)


class PortableDocument(DocumentType):
    mimetype = 'application/pdf'
    extension = 'pdf'
    description = 'PDF file'
    signature = hexbytes('25 50 44 46')

    @classmethod
    def extract(cls, file):
        try:
            reader = PdfFileReader(file)
        except PdfReadError as e:
            raise six.raise_from(ExtractionError("Could not open pdf reader"), e)
        except TypeError as e:
            if str(e) == "'NumberObject' object has no attribute '__getitem__'":
                # there's a bug in PyPDF2 for some pdf valid files
                # 
                return cls(file, dict())
            else:
                raise

        if reader.isEncrypted:
            try:
                # try to decrypt it with an empty password
                success = reader.decrypt('')
            except NotImplementedError:
                # the document uses an unsupported encryption method
                # it's (probably) a real pdf document though,
                # we just can't extract its metadata without the password
                return cls(file, dict())
            else:
                if success == 0:
                    # the password failed
                    # it's (probably) a real pdf document though,
                    # we just can't extract its metadata without the password
                    return cls(file, dict())
            # for success values 1 and 2 we should now be able to read the document

        props = OrderedDict()

        try:
            props['pages'] = reader.numPages
        except PdfReadError:
            pass

        try:
            info = reader.documentInfo
        except PdfReadError:
            info = None

        if info is None:
            return cls(file, props)

        for key, prop, parser in (
            ('Title', 'title', None),
            ('Subject', 'subject', None),
            ('Author', 'author', None),
            ('Creator', 'creator', None),
            ('Producer', 'producer', None),
            ('CreationDate', 'created', parse_date),
            ('ModDate', 'modified', parse_date),
        ):
            try:
                value = info['/%s' % key]
            except KeyError:
                pass
            else:
                if value is not None:
                    if parser:
                        value = parser(value)
                        if value is None:
                            continue
                    props[prop] = value

        return cls(file, props)
