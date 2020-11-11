from bs4 import BeautifulSoup
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import requesting_urls

def extract_teams(url, plot=True, showPlot=False, savePlot=True):
    '''
    Takes a url to a NBA season playoff wikipedia site and extracts the (8) teams in the Conference Semifinals column in the season bracket.
    If plot is True (defualt), plots graphs showing top 3 players from each team with respect to their statistics in PPG, BPG and RPG (2019-20 season).
    If showPlot is True (defaults to False), the plots are displayed.
    If savePlot is True (default), the plots are saved to the folder ./NBA_player_statistics as png's.

    Args:
        url:        The url to the NBA playoff wikipedia site (any season)
        plot:       (Optional) Whether to create plots. Defaults to True.
        showPlot:   (Optional) Whether to display plots. Defaults to False.
        savePlot:   (Optional) Whether to save plots. Defaults to True

    '''
    # Use regex to extract base url (to use in relative urls)
    regex_baseurl = r"^(.*://[A-Za-z0-9\-\.]+).*"
    baseurl = re.findall(regex_baseurl, url)[0]

    response = requesting_urls.get_html(url)
    document = BeautifulSoup(response.content, 'lxml')
    bracket = document.find('table', {'border': '0', 'cellpadding': '0', 'cellspacing': '0'})

    bracket_rows = np.array(bracket.find_all('tr'))
    rows = bracket_rows[[4, 6, 16, 18, 28, 30, 40, 42]]


    teams = []

    for row in rows:
        a_tag = row.find(['a'], href=True)
        teamstatistics = extract_url(a_tag, baseurl)
        teams.append(teamstatistics)

    # Sort
    teams_comparison = []

    def get_ppg(player):
        '''
        Helper method to return a player's ppg as float

        Args:
            player:     The player dict
        Returns:
            <float>:    ppg as float, or 0 if empty
        '''
        if player.get('ppg') != '':
            return float(player.get('ppg'))
        else:
            return 0

    for team in teams:
        if team is not None:
            team_best = sorted(team, key=get_ppg, reverse=True)[:3]
            teams_comparison.append(team_best)

    # Plot
    if plot:
        createPlot(teams_comparison, 'ppg', show=showPlot, save=savePlot)
        createPlot(teams_comparison, 'bpg', show=showPlot, save=savePlot)
        createPlot(teams_comparison, 'rpg', show=showPlot, save=savePlot)


def extract_url(a_tag, baseurl):
    '''
    Takes 'a' tag and baseurl from a team's html a-tag cell, and extracts the team Roster listing and each players NBA Regular Season statistics.
    Returns the statistics as an array of dict items, where each item represents a player and their statistics for the 2019-20 regular season.

    Args:
        a_tag:      The html 'a'-tag cell for the team.
        baseurl:    The base url for the page.
    Returns:
        <Array<Dict>> teamstatistics:   Array of dict items, where each item represents a player's {'team', 'name', 'ppg', 'bpg', 'rpg'}
    '''
    teamUrl = baseurl + a_tag['href']
    teamName = a_tag.getText(strip=True)

    # Extract html
    response = requesting_urls.get_html(teamUrl)
    document = BeautifulSoup(response.content, 'lxml')

    # Navigate to table
    for text in document.find_all('caption', text="Roster listing\n"):
        rostertable = text.findParents('table')[0]

    playertable = rostertable.find_all('table', {'class': 'sortable'})[0]

    if (playertable is not None):
        playerrows = playertable.find_all("tr")
    else:
        return None

    # Array of Dicts holding the statistics of all players on the team, formatted like {'team', 'name', 'ppg', 'bpg', 'rpg'}
    teamstatistics = []

    # Extract player statistics and fill teamstatistics
    for row in playerrows[1:]:
        cells = row.find_all(["td"])
        namecell = cells[2]
        player_atag = namecell.find('a', href=True)
        playername = re.sub(r"(\([\w]*\))", '', namecell.getText(strip=True))
        playerurl = baseurl + player_atag['href']

        playerresponse = requesting_urls.get_html(playerurl)
        playerdocument = BeautifulSoup(playerresponse.content, 'lxml')

        statisticstables = playerdocument.find_all('table', {'class': 'wikitable sortable'})

        if len(statisticstables) > 0:
            statisticstable = statisticstables[0]
        else:
            return

        nodata = True
        for text in statisticstable.find_all("a", text=re.compile(r".*2019.*20.*")):
            nodata = False
            statisticsrow = text.findParents('tr')[0]

        if nodata:
            (PPG, BPG, RPG) = ('', '', '')
        else:
            statisticscells = statisticsrow.find_all(["td"])

            (PPG, BPG, RPG) = np.array(statisticscells)[[12, 11, 8]]
            # Strip of formatting and extra characters (* and -)
            (PPG, BPG, RPG) = (re.sub(r"[\*\-]", '', PPG.getText(strip=True)), re.sub(r"[\*\-]", '', BPG.getText(strip=True)), re.sub(r"[\*\-]", '', RPG.getText(strip=True)))

        playerstatistics = {'team': teamName, 'name': playername, 'ppg': PPG, 'bpg': BPG, 'rpg': RPG}
        teamstatistics.append(playerstatistics)

    return teamstatistics


def createPlot(teams, type, show=False, save=True):
    '''
    Creates plots displaying statistics based on the giving 'teams' array, showing statistics for top 3 players over 'type' (ppg, bpg or rpg) for each team.
    If show is True (defaults to False), the plots are displayed.
    If save is True (deault), the plots are saved to folder ./NBA_player_statistics as png's

    Args:
        teams:  Array holding statistics from top 3 players from each team.
        type:   Type of statistics to plot ('ppg' | 'bpg' | 'rpg')
        show:   (Optional) Whether to display plots. Defaults to False.
        save:   (Optional) Whether to save plots. Defaults to True.

    '''
    saveLocation = './NBA_player_statistics/'
    # Set title and file name based on type
    if type == 'ppg':
        title = 'Points per game'
        fname = 'players_over_ppg'
    elif type == 'bpg':
        title = 'Blocks per game'
        fname = 'players_over_bpg'
    elif type == 'rpg':
        title = 'Rebounds per game'
        fname = 'players_over_rpg'
    else:
        title = 'NBA Statistics'
        fname = 'nba_statistics'

    # Sort
    def get_points(player, p):
        '''
        Helper method to return a player's points in category 'p' as float

        Args:
            player:     The player dict
            p:          Point type ('ppg' | 'bpg' | 'rpg')
        Returns:
            <float>:    Point as float, or 0 if empty
        '''
        if player.get(p) != '':
            return float(player.get(p))
        else:
            return 0

    labels_teams = []
    first = {'names': [], 'points': []}
    second = {'names': [], 'points': []}
    third = {'names': [], 'points': []}

    # Set labels and values to use in plot
    for team in teams:
        labels_teams.append(team[0]['team'])
        first['names'].append(team[0]['name'])
        first['points'].append(get_points(team[0], type))
        second['names'].append(team[1]['name'])
        second['points'].append(get_points(team[1], type))
        third['names'].append(team[2]['name'])
        third['points'].append(get_points(team[2], type))

    # Plot init and formatting
    x = np.arange(len(labels_teams))
    width = 0.2

    fig, ax = plt.subplots(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
    fig.canvas.set_window_title('NBA conference semifinals statistics')
    rects1 = ax.bar(x - width, first['points'], width)
    rects2 = ax.bar(x, second['points'], width)
    rects3 = ax.bar(x + width, third['points'], width)

    def autolabel(rects, pos):
        '''
        Auto labels rectangles with the name of the player
        Args:
            rects:  Set of rectangles (ax)
            pos:    [1 | 2 | 3] rectangle group (first, second, third)
        '''
        for index, rect in enumerate(rects):
            if pos == 1:
                name = first['names'][index]
            elif pos == 2:
                name = second['names'][index]
            elif pos == 3:
                name = third['names'][index]
            else:
                break
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width(), 0, name,
                    ha='center', va='bottom', rotation='60', fontsize=10)
            ax.text(rect.get_x() + rect.get_width() / 2, height, height,
                    ha='center', va='bottom', rotation='0', fontsize=12)

    ax.set_ylabel(type)
    ax.set_title(f'{title} by top players from each team')
    ax.set_xticks(x)
    ax.set_xticklabels(labels_teams)

    autolabel(rects1, 1)
    autolabel(rects2, 2)
    autolabel(rects3, 3)

    fig.tight_layout()

    if show:
        # Display plot
        plt.show()
    if save:
        # Save plot
        plt.savefig(fname=saveLocation+fname)


# Run as script
if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/2020_NBA_playoffs'
    extract_teams(url)
