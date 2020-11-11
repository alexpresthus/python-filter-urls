from bs4 import BeautifulSoup
import requesting_urls
import re

def extract_events(url, createSlip=True):
    '''
    Takes a url and extracts data (date, venue, type) from the main table.
    If createSlip is True (default), creates an empty betting slip, saved to datetime_filter/betting_slip_empty.md
    Returns the data as an array of (date, venue, type) arrays.

    Args:
        url:        The url of which site to extract events from.
        createSlip: (Optional) Whether to create a betting slip with the extracted data. Defaults to True.
    Returns:
        Array<Array<String>> data:  Returns the set of data (array of each (date, venue, type) for each row) extracted.
    '''
    response = requesting_urls.get_html(url)
    document = BeautifulSoup(response.content, "lxml")
    table = document.find('table', {"class": 'wikitable plainrowheaders'})
    rows = table.find_all("tr")

    # Remove filler rows
    for row in rows:
        if (len(row.find_all(["td"])) < 2):
            rows.remove(row)

    # Array to keep (date, venue, type) values for each row
    data = []

    # Extract date, venue and type for each row
    for i in range(0, len(rows)):
        cells = rows[i].find_all(["td"])
        cells = cells[0:5] # Limit to first 5 data cells

        cells_text = [cell.get_text(strip=True) for cell in cells] # Strip for html tags

        # Use regex to filter out the first cells until date, this being '#' 'event' and empty cells. Makes date the first cell
        while re.search(r"^[\d]*$", cells_text[0], flags=re.VERBOSE | re.MULTILINE):
            cells_text.pop(0)

        # Use regex to filter out all cells after type. Makes type the last cell
        for j in range(len(cells_text)):
            if re.search(r"[A-Z]{2}[\dcnx]{3}", cells_text[j]):
                cells_text = cells_text[:j+1]
                break

        # Check length of cells_text. If 2, venue is missing and is set equals to previous row's venue
        if (len(cells_text) == 2 and i != 1):
            venue = data[i-1][1]
            cells_text.insert(1, venue)

        # Add to data
        data.append(cells_text)

    # Format data
    for cells in data:
        (date, venue, type) = cells

        # Format date (extract only date string as D(D) Month YYYY)
        date = re.findall(r"([\d]{1,2} [\w]+ [\d]{4})", date, flags=0)[0]
        cells[0] = date

        # Format type (remove numbers after event key)
        type = re.sub(r"([\dcnx]{3})", '', type)
        cells[2] = type

    # Call createBettingSlip to create empty betting slip if createSlip==True
    if createSlip:
        createBettingSlip(data)

    # Always return data
    return data

def createBettingSlip(data):
    '''
    Takes an array of (date, venue, type) arrays and formats an empty betting slip to ./datetime_filter/betting_slip_empty.md

    Args:
        data: An array of arrays (date, venue, type) of the data to include in the betting slip
    '''
    with open (f'./datetime_filter/betting_slip_empty.md', 'w', encoding='utf-8') as f:
        f.write('BETTING SLIP\n\nName:\n\n')
        f.write('Event Key: DH – Downhill, SL – Slalom, GS – Giant Slalom, SG – Super Giant Slalom, AC – Alpine Combined, PG – Parallel Giant Slalom\n\n')
        f.write('| **DATE** | **VENUE** | **DISCIPLINE** | **Who wins?** |\n')
        f.write('| --- | --- | --- | --- |\n')
        for row in data:
            (date, venue, type) = row
            f.write(f'| {date} | {venue} | {type} |  |\n')


if __name__ == "__main__":
    url = 'https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup'
    extract_events(url)
