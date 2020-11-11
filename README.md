## Python filter urls

### About the project

This was a school project utilizing RegEx and the Python package BeautifulSoup4 to filter html responses from Wikipedia sites.

### Required dependencies and packages

Dependencies
* python 3.8
* pip 20.1.1

Python packages
* requests 2.24.0
* beautifulsoup 4.9.1
* networkx 2.4 (For subtask 5.6 only)

Install required packages using:
```
pip install requests, beautifulsoup4, networkx
```

### How to run scripts

To run subtask functions with test input (as described in the assignment) and generate output files, run the files as scripts:

```
python requesting_urls.py
python filter_urls.py
python time_planner.py
python fetch_playerstatistics.py
python collect_dates.py
python wiki_race_challenge.py [url1 url2]
```

### Additional comments

Subtask 5.3

* In the inital search, the match pattern for month is not fully restricting (e.g. Movement is a valid month). To fix this I implemented an additional match check before adding the date string to the results list: When formatting the month as a two-digit number, if the month string is not matched with a digit [1-9] OR represented in a dict of valid month strings, it has to be a false positive, and is not included in the final result.
* Year can be any 2,3 or 4-number digit, starting with 1-9, higher than 31 (to avoid mix ups between DMY and YMD, e.g. 13 october 14 (where both year and day could be 13/14).


Subtask 5.6

* I did a quick attempt to solve the task, but am aware that it is a poor implementation.
* My idea is to recursively build a node-graph, with nodes representing urls as strings. The graph would be recursively doing a site scan for urls (v) on a site (u), add the edges (u,v) and check if any v is the destination url. If it is, use nx' built-in Dijkstra's algorithm to find the shortest path, then exit. If it is not, do the same search for each v. Repeat until found.
* This implementation builds a node-graph on-demand, adding new edges only after checking that the destination url is not yet found. This way, the first find is sure to be the shortest.
* However it is very time consuming, O(n^m), where n is the number of edges for each url (avg. ~1000), and m is the depth of the search. The runtime for a search of n=1000 and m=2 (1.000.000 iterations) was on average about 30 seconds, meaning a search with depth = 3 (1.000.000.000 iterations) could take over 8 hours.
* The biggest problem is not being able to vectorize the function that creates and adds edges to the graph, since it's not merely computational but makes a GET-request to a url, then scans the result before creating the array of urls (nodes). The procedure is also depending on the internet connection and server response time for each request. If the procedure was merely computational, we could build the graph much faster (e.g. using np)
* Alas, this doesn't change our O-notation. I would like to try and make the (now iterative) procedure recursive by implementing a queue that continously fills the graph while a match is not found in a newly added edge. However there is definitely still going to be issues since runtime is depending on network speed and server response time.
