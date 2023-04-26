# NHL App
### A command line tool pull live NHL game data, rosters, schedules, and more

## Installation
#### git clone the repo
#### cd into the directory
#### create a virtual environment 'python -m venv venv'
#### activate the virtual environment 'source venv/bin/activate'
#### pip install .

# Usage
#### run 'python main.py games_today' to see the games scheduled for today and current scores
#### run 'python main.py ticker GAME_ID PERIOD (ex. python main.py ticker 2022030115 all) to get every play of the game'
#### run 'python main.py roster TEAM_ABBREVIATION' to get a json file of a team's roster, the terminal will also display the team roster