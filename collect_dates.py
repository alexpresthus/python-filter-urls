import re
import requesting_urls

def find_dates(html, output=None, saveToFolder='filter_dates_regex'):
    '''
    Receives a string of html and returns a list of all dates found in the text.
    If argument 'output' is specified, the list will be saved to a text file with a specified name output.txt.

    Args:
        html:           The string of html to search
        output:         (Optional) The filename (format as 'output.txt') for where to save the list. Defaults to None.
        saveToFolder:   (Optional) The folder for where to save the output file. Defaults to 'filter_dates_regex'
    Returns:
        <Array> dates:  A list of date items, where each item is a string formatted as 'YYYY/MM/DD'
    '''
    # List to hold matches
    matches = []

    # List to hold formatted dates
    dates = []

    # Regex patterns
    regexes = {
            'DMY': r"(?xm)\b(?:(?P<d>[1-9]|[12][\d]|3[01])[\ ])?(?P<m>[ADFJMOSN][aceopu][abceghilmnoprstuvy]{1,7})[\ ](?P<y>[1-9][\d]{2,3}|[4-9][\d]|3[2-9])\b",
            'MDY': r"(?x)\b(?P<m>[ADFJMOSN][aceopu][abceghilmnoprstuvy]{1,7})(?:[\ ](?P<d>[1-9]|[12][\d]|3[01]))?[\,][\ ](?P<y>[1-9][\d]{2,3}|[4-9][\d]|3[2-9])\b",
            'YMD': r"(?x)\b(?P<y>[1-9][\d]{2,3}|[4-9][\d]|3[2-9])[\ ](?P<m>[ADFJMOSN][aceopu][abceghilmnoprstuvy]{1,7})[\ ](?:(?P<d>[1-9]|[12][\d]|3[01]))\b",
            'ISO': r"(?x)\b(?P<y>[1-9][\d]{2,3}|[4-9][\d]|3[2-9])[\-](?P<m>(?:0?[1-9])|(?:1[0-2]))[\-](?:(?P<d>0?[1-9]|[12][\d]|3[01]))\b"
            }

    # Use regex to search for matches and append to dates list
    for format in regexes:
        r = re.compile(regexes[format])
        for match in r.finditer(html):
            matches.append(match.groupdict())

    def format_month(text):
        '''
        Takes a string of text and formats as a two-digit month number.
        If no matches are found, the string remains the same.
        If text is not a number or a month represtented as a dict key, it's a false positive case and None is returned.

        Args:
            text:   The string to match and potentially substitute
        Returns:
            <String>:   The formatted string. None if false positive case.
        '''
        # Add '0' at start if one-digit number, then return
        if re.match(r"\b\d{1}\b", text):
            return f'0{text}'

        # Dict of expressions to match and corresponding substitute strings
        dict = {
            'January': '01', 'Jan': '01',
            'February': '02', 'Feb': '02',
            'March': '03', 'Mar': '03',
            'April': '04', 'Apr': '04',
            'May': '05',
            'June': '06', 'Jun': '06',
            'July': '07', 'Jul': '07',
            'August': '08', 'Aug': '08',
            'September': '09', 'Sep': '09',
            'October': '10', 'Oct': '10',
            'November': '11', 'Nov': '11',
            'December': '12', 'Dec': '12'
        }
        # Create a regular expression  from the dictionary keys
        regex = re.compile(f'({ "|".join(dict.keys()) })')

        # For each match, look-up corresponding value in dictionary
        string = regex.sub(lambda m: dict[m.string[m.start():m.end()]], text)

        # If the string still has word characters, it's a case of false positive. Return None
        if re.match(r"(?m)^[a-zA-Z]*$", string):
            return None

        return string

    def format_day(text):
        '''
        Takes a string of text and uses regex to check if it's a one-digit number.
        Add '0' to start if match, else return the original.

        Args:
            text:   The string to match
        Retruns:
            <String>:   The formatted string
        '''
        # Add '0' at start if one-digit number
        if re.match(r"\b\d{1}\b", text):
            return f'0{text}'
        return text

    # Format date strings as YYYY/MM[/DD]
    for match in matches:
        (d, m, y) = (match['d'], match['m'], match['y'])
        m = format_month(m)
        if m is not None:
            if d is None:
                dates.append( f'{y}/{m}' )
            else:
                d = format_day(d)
                dates.append( f'{y}/{m}/{d}' )



    # Write to file if output is specified
    if output is not None:
        with open (f'./{saveToFolder}/{output}', 'w', encoding='utf-8') as f:
            f.write('DATES ON PAGE:\n\n')
            for index, line in enumerate(dates):
                f.write(f'{index+1}) {line}\n')


    # Always return dates list
    return dates

def test():
    """
    Makes a set of calls to find_dates() with parameters given in an array of test arguments, 'tests'.
    """
    tests = [['https://en.wikipedia.org/wiki/Linus_Pauling', 'Linus_Pauling_output.txt'],
            ['https://en.wikipedia.org/wiki/Rafael_Nadal', 'Rafael_Nadal_output.txt'],
            ['https://en.wikipedia.org/wiki/J._K._Rowling', 'J._K._Rowling_output.txt'],
            ['https://en.wikipedia.org/wiki/Richard_Feynman', 'Richard_Feynman_output.txt'],
            ['https://en.wikipedia.org/wiki/Hans_Rosling', 'Hans_Rosling_output.txt']]

    for test in tests:
        html = requesting_urls.get_html(test[0]).text
        output = test[1]
        find_dates(html, output=output)

if __name__ == '__main__':
    test()
