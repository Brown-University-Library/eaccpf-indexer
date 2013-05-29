class date_cleanser:

    def __init__(self):
        # time formats we will try to clean
        self.timeformats = [
            "%Y-%m-%d", # 1976-01-01
            "%Y %m %d", # 1976 01 01
            "%d %B %Y", # 12 January 1997
            "%B %Y",    # February 1998
            "%Y",       # 2004
            "c. %Y",    # c. 2004
            "%Y?",      # 2004?
        ]


    def clean(self, datevalue):
        """Date data needs to be in Solr date format

        The format for this date field is of the form 1995-12-31T23:59:59Z,

        @params:
        date: the date string we want to standardise
        """
        #  handle whatever it is we find...
        for timeformat in self.timeformats:
            try:
                datevalue = datetime.strptime(datevalue, timeformat)
                datevalue = "%sZ" % str(datevalue).replace(' ', 'T')
                break
            except:
                pass
                # ie try the next format until we succeed, or get to the end of the list

        # here we check that we can read the datevalue using
        #  the expected format. If there wasn't a suitable format in the list,
        #  then here we'll find the original string, it will fail, and a warning
        #  will be issued.
        try:
            checkdate = datetime.strptime(datevalue, "%Y-%m-%dT%H:%M:%SZ")
            return datevalue
        except ValueError as e:
            log.warn("Unknown time format: %s" % datevalue)
            return None

def clean_dates(self, doc):
    """Date data needs to be in Solr date format

    The format for this date field is of the form 1995-12-31T23:59:59Z,

    @requirements:
    # given a list of date fields that could be found in an XML doc; something like:
    date_fields = [ 'date_start', 'date_end', 'date_birth', 'date_death' ]class date_cleanser:

    def __init__(self):
        # time formats we will try to clean
        self.timeformats = [
            "%Y-%m-%d", # 1976-01-01
            "%Y %m %d", # 1976 01 01
            "%d %B %Y", # 12 January 1997
            "%B %Y",    # February 1998
            "%Y",       # 2004
            "c. %Y",    # c. 2004
            "%Y?",      # 2004?
        ]


    def clean(self, datevalue):
        """Date data needs to be in Solr date format

        The format for this date field is of the form 1995-12-31T23:59:59Z,

        @params:
        date: the date string we want to standardise
        """
        #  handle whatever it is we find...
        for timeformat in self.timeformats:
            try:
                datevalue = datetime.strptime(datevalue, timeformat)
                datevalue = "%sZ" % str(datevalue).replace(' ', 'T')
                break
            except:
                pass
                # ie try the next format until we succeed, or get to the end of the list

        # here we check that we can read the datevalue using
        #  the expected format. If there wasn't a suitable format in the list,
        #  then here we'll find the original string, it will fail, and a warning
        #  will be issued.
        try:
            checkdate = datetime.strptime(datevalue, "%Y-%m-%dT%H:%M:%SZ")
            return datevalue
        except ValueError as e:
            log.warn("Unknown time format: %s" % datevalue)
            return None

def clean_dates(self, doc):
    """Date data needs to be in Solr date format

    The format for this date field is of the form 1995-12-31T23:59:59Z,

    @requirements:
    # given a list of date fields that could be found in an XML doc; something like:
    date_fields = [ 'date_start', 'date_end', 'date_birth', 'date_death' ]

    @params:
    doc: the XML document
    """
    date_elements = [ e for e in doc.iter() if e.get('name') in date_fields ]
    for e in date_elements:
        # have we found an empty or missing date field ?
        if e.text is None:
            continue

        dc = date_cleanser()
        datevalue = dc.clean(e.text)
        if datevalue is not None:
            e.text = datevalue
        else:
            e.text = ''


def strip_empty_elements(self, doc):
    """Remove empty elements from the document.

    Solr date fields don't like to be empty - hence why this
    method exists. As it turns out, it can't hurt to ditch empty
    elements - less to submit. Hence why it's generic

    @params:
    doc: the XML document
    """
    for elem in doc.iter('field'):
        if elem.text is None:
            elem.getparent().remove(elem)

    @params:
    doc: the XML document
    """
    date_elements = [ e for e in doc.iter() if e.get('name') in date_fields ]
    for e in date_elements:
        # have we found an empty or missing date field ?
        if e.text is None:
            continue

        dc = date_cleanser()
        datevalue = dc.clean(e.text)
        if datevalue is not None:
            e.text = datevalue
        else:
            e.text = ''


def strip_empty_elements(self, doc):
    """Remove empty elements from the document.

    Solr date fields don't like to be empty - hence why this
    method exists. As it turns out, it can't hurt to ditch empty
    elements - less to submit. Hence why it's generic

    @params:
    doc: the XML document
    """
    for elem in doc.iter('field'):
        if elem.text is None:
            elem.getparent().remove(elem)