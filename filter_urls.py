import re
import requesting_urls

def find_urls(url, html):
    '''
    Receives a string of html and returns a list of all urls found in the text.

    Args:
        url:    The url from which the html is retrieved.
        html:   A string of html to filter.
    Returns:
        <Array<String>> urls:  A list of all urls found in the text.
    '''
    # Use regex to extract base url (to use in relative urls)
    regex_baseurl = r"^(.*://[A-Za-z0-9\-\.]+).*"
    baseurl = re.findall(regex_baseurl, url)[0]

    # Use regex to find all urls (a href) on the page
    regex_allurls = r"<a [^>] href=['\"]([^#'\"]+)['\"#]"
    urls = re.findall(regex_allurls, html, flags=re.VERBOSE)

    # Use regex to substitute all relative urls (starts with /) with the full url (replace / with baseurl + /)
    for i in range(len(urls)):
        urls[i] = re.sub(r"^/", baseurl+'/', urls[i], flags=re.MULTILINE | re.VERBOSE)

    return urls

def find_articles(url, params=None, output=None, saveToFolder='filter_urls'):
    '''
    Receives a url and returns a list of all urls to Wikipedia articles found on the page.
    If argument 'params' is specified, parameters are passed in the get request.
    If argument 'output' is specified, lists of all urls and wikipedia articles found will be saved to a text file with a specified name output.txt.
    If the specified output filename already exists, it overwrites the content.
    Output folder can be specified as saveToFolder, but defaults to filter_urls
    If no output argument is given, the list of wikipedia articles is simply returned.

    Args:
        url:            The url from which the html is retrieved.
        params:         (Optional) Parameters to pass to the get function. Defaults to None.
        output:         (Optional) The filename (format as 'output.txt') for where to save the url lists. Defaults to None.
        saveToFolder:   (Optional) The folder for where to save the output file. Defaults to 'filter_urls'
    Returns:
        <Array<String>> wiki_urls:  A list of the urls found of Wikipedia articles.
    '''
    # Call requesting_urls.get_html() with url and optional params. Save response.text to variable html, and pass to find_urls to get a list of all urls.
    response = requesting_urls.get_html(url, params=params)
    html = response.text
    all_urls = find_urls(url, html)

    # Use regex to find all wikipedia articles in the list of all urls (join iterable all_urls to one string with separator |)
    regex_wikiarticles = r"(https*://[\w]+.wikipedia.org/[^|:]*)"
    wiki_urls = re.findall(regex_wikiarticles, '|'.join(all_urls), flags=re.VERBOSE)

    # Save output to file if output is specified.
    if output is not None:
        with open (f'./{saveToFolder}/{output}', 'w', encoding='utf-8') as f:
            f.write('ALL URLS:\n')
            for url in all_urls:
                f.write(f'{url}\n')
            f.write('\nWIKIPEDIA ARTICLES:\n')
            for url in wiki_urls:
                f.write(f'{url}\n')

    # Always return the list of wikipedia articles
    return wiki_urls

def test():
    """
    Makes a set of calls to find_articles() with parameters given in a 2D-array of test arguments, 'tests'.
    """
    tests = [['https://en.wikipedia.org/wiki/Nobel_Prize', 'nobel_prize_output.txt'],
            ['https://en.wikipedia.org/wiki/Bundesliga', 'bundesliga_output.txt'],
            ['https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup', '2019_FIS_World_Cup_output.txt']]

    for test in tests:
        (url, output) = test
        find_articles(url, output=output)

if __name__ == '__main__':
    test()
