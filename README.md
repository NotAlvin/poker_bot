# Poker Bot
This is a Telegram bot designed to help facilitate a poker game. It can be used to track buy-ins, transfers, and final chip counts, and to settle the game at the end. The bot is built using the Python python-telegram-bot library and can be run on any platform that supports Python.

# Setup

## Clone the repository:
`git clone https://github.com/yourusername/poker-bot.git`

## Install the necessary packages:
`pip install -r requirements.txt`

Create a new Telegram bot by following the instructions on the Telegram website. Make sure to save the API token for later.

Update the TOKEN variable in the poker_bot.py file with your bot's API token.

## Usage
To start the bot, run the following command:

`python poker_bot.py`

# Commands
- /start - Start the bot and select the game type (cash or tournament).
- /buy_in - Register your buy-in amount.
- /transfer - Transfer chips to another player.
- /add_final_chips - Add your final chip count.
- /settle - Calculate and display the settlements.
- /game_state - Calculate and display the current effective buy-ins of all players.
- /help - Display the list of available commands.

# How to Use
1. Start the bot by sending the /start command.
2. Select the game type (cash or tournament).
3. Register your buy-in amount by sending the /buy_in command.
4. Transfer chips to another player by sending the /transfer command.
5. Add your final chip count by sending the /add_final_chips command.
6. Calculate and display the settlements by sending the /settle command.
7. Calculate and display the current effective buy-ins of all players by sending the /game_state command.
8. Display the list of available commands by sending the /help command.

# Acknowledgments
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - The Python library used to create the bot.
- [Telegram API documentation](https://github.com/python-telegram-bot/python-telegram-bot) - The documentation for the Telegram Bot API.
- [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) - The template used to create this README.
