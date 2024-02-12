# Developer instructions

## Setup

Create a python venv, google it if you're a noob.

In VS Code, navigate to *View -> Command palett -> Python: Select Interpreter*.

Choose the venv python executable from the menu.

Install dependencies in the venv:

- `discord.py`
- `dota2` 

This would look something like

`home/user/inhousebot/bin/python -m pip install {dependecy}`

You can now start the bot by running bot.py and can use `Ctrl + C` to end it. To leave the bot running after the session, see Start the bot. This must be used on a server that is always on.

## Managing the bot

### Start the bot

Run the script in the directory by

`./inhousebot.sh &`

You may need to press *Enter* again to return to the terminal.

### Kill the bot
List all ongoing python processes by

`ps -e | grep python`

Output should look like

`38362 pts/4    00:00:00 python`

Kill the ongoing process with

`sudo kill 38362`
