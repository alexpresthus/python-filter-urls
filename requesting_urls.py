# requesting_urls.py

import requests as req

def get_html(url, params=None, output=None, saveToFolder='requesting_urls'):
    """
    Makes a url request of a given website.
    If argument 'params' is specified, parameters are passed in the get request.
    If argument 'output' is specified, the response url and text will be saved to a text file with a specified name output.txt.
    If the specified output filename already exists, it overwrites the content.
    Output folder can be specified as saveToFolder, but defaults to requesting_urls
    If no output argument is given, the response is simply returned.

    Args:
        url:            The url from which the html is retrieved.
        params:         (Optional) Parameters to pass to the get function. Defaults to None.
        output:         (Optional) The filename (format as 'output.txt') for where to save the response url and text. Defaults to None.
        saveToFolder:   (Optional) The folder for where to save the output file. Defaults to 'requesting_urls'
    Returns:
        <Response> response: The html response from the request on the url.
    """
    response = req.get(url, params=params)

    if output is not None:
        with open (f'./{saveToFolder}/{output}', 'w', encoding='utf-8') as f:
            f.write(f'URL: {response.url}\nTEXT:\n{response.text}')
    return response

def test():
    """
    Makes a set of calls to get_html() with parameters given in an array of test arguments, 'tests'.
    """
    tests = [["https://en.wikipedia.org/wiki/Studio_Ghibli", None, 'studio_ghibli_output.txt'],
            ["https://en.wikipedia.org/wiki/Star_Wars", None, 'star_wars_output.txt'],
            ["https://en.wikipedia.org/wiki/Dungeons_%26_Dragons", None, 'dungeons_dragons_output.txt'],
            ["https://en.wikipedia.org/w/index.php", {'title': 'Main_Page', 'action': 'info'}, 'wiki_main_page_output.txt'],
            ["https://en.wikipedia.org/w/index.php", {'title': 'Hurricane_Gonzalo', 'oldid': '983056166'}, 'wiki_hurricane_gonzalo_output.txt']]

    for test in tests:
        (url, params, output) = test
        get_html(url, params=params, output=output)

if __name__ == '__main__':
    test()
