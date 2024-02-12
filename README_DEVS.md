# Developer instructions

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
