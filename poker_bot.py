import logging
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

TOKEN = "YOUR TELEGRAM API TOKEN"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store game data
'''
Dictionary looks like this:
{
    user_id: {
        "name": name,
        "total_buy_in": total_buy_in,
        "transfers": transfers,
        "final_chips": final_chips
    },
    ...
}

- user_id: a unique identifier for each user, based on their Telegram ID.
    - name: the user's display name.
    - total_buy_in: the total amount the user has bought in to the game.
    - transfers: a list of dictionaries representing transfers made by the user. 
        Each dictionary contains the following keys:
        - type: the type of transfer, either "send" or "receive".
        - amount: the amount of chips transferred.
    - final_chips: the final chip count for the user, which is added at the end of the game.
'''
players_data = {}

# Helper Functions
def get_user_name(user):
    if user.username:
        return user.username
    full_name = user.first_name
    if user.last_name:
        full_name += " " + user.last_name
    return full_name

def get_message(update: Update) -> Update:
    if update.message:
        return update.message
    elif update.channel_post:
        return update.channel_post
    else:
        return None

def end_conversation(update: Update, context: CallbackContext) -> int:
    get_message(update).reply_text("Ending the conversation.")
    return ConversationHandler.END

# Main Functions
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    update.message.reply_text(
        f"Hi {get_user_name(user)}! I'm your poker group's bot. "
        "Use /help to see a list of available commands."
    )

    keyboard = [
        [
            InlineKeyboardButton("Cash Game", callback_data="game_type|cash"),
            InlineKeyboardButton("Tournament", callback_data="game_type|tournament"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please select the game type:", reply_markup=reply_markup)

def handle_game_type_selection(update: Update, context: CallbackContext) -> None:
    global GAME_TYPE
    
    query = update.callback_query
    query.answer()

    data = query.data.split('|')
    game_type = data[1]

    if game_type == "cash":
        GAME_TYPE = "Cash"
    elif game_type == "tournament":
        GAME_TYPE = "Tournament"

    query.edit_message_text(f"Game type set to {GAME_TYPE}")
    return ConversationHandler.END

def buy_in(update: Update, context: CallbackContext) -> None:
    get_message(update).reply_text("Please enter the amount you want to buy in:")

    return "WAITING_BUY_IN_AMOUNT"

def handle_buy_in_amount(update: Update, context: CallbackContext) -> None:
    user_id = get_message(update).from_user.id
    name = get_message(update).from_user.first_name
    amount = int(get_message(update).text)

    if user_id not in players_data:
        players_data[user_id] = {"ID": user_id, "name": name}
        players_data[user_id]["total_buy_in"] = amount
    
    else:
        players_data[user_id]["total_buy_in"] += amount

    get_message(update).reply_text(f"Buy-in of {amount} registered for {name}.")
    return ConversationHandler.END

def transfer(update: Update, context: CallbackContext) -> None:
    user_id = get_message(update).from_user.id
    user_name = get_user_name(get_message(update).from_user)

    keyboard = []
    for recipient_id, recipient_data in players_data.items():
        if recipient_id != user_id:
            recipient_name = recipient_data["name"]
            keyboard.append([InlineKeyboardButton(recipient_name, callback_data=f'transfer_to|{recipient_id}|{recipient_name}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    get_message(update).reply_text('Please select the person you want to transfer chips to:', reply_markup=reply_markup)
    return "WAITING_TRANSFER_SELECTION"

def handle_transfer_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data.split('|')
    to_user_name = data[1]

    # Update players_data with a new transfer dictionary for the current user
    user_id = query.from_user.id
    user_name = players_data[user_id]["name"]
    players_data[user_id]["transfers"].append({
        "type": "send",
        "amount": 0,
        "to": to_user_name
    })

    query.edit_message_text(f'Selected {to_user_name}. Please send the amount to transfer as a message.')
    return "WAITING_TRANSFER_AMOUNT"


def handle_transfer_amount(update: Update, context: CallbackContext) -> None:
    from_user_id = get_message(update).from_user.id
    from_user_name = get_user_name(get_message(update).from_user)

    if 'transfer_to' in players_data:
        data = 'transfer_to'
        to_user_id = data["recipient_id"]
        to_user_name = data["recipient_name"]
        amount = float(get_message(update).text)

        # Update sender's transfers list
        players_data[from_user_id]["transfers"].append({"type": "send", "amount": amount})
        # Update sender's total buy-in
        players_data[from_user_id]["total_buy_in"] -= amount

        # Update recipient's transfers list
        players_data[to_user_id]["transfers"].append({"type": "receive", "amount": amount})
        # Update recipient's total buy-in
        players_data[to_user_id]["total_buy_in"] += amount

        get_message(update).reply_text(f"{from_user_name} transferred ${amount} to {to_user_name}")
        del players_data['transfer_to']
    else:
        get_message(update).reply_text('Please use /transfer command to initiate a transfer.')

def display_game_state(update: Update, context: CallbackContext) -> None:
    if not players_data:
        get_message(update).reply_text("No data available yet.")
        return

    message = f"Current state of the ({GAME_TYPE}) game:\n\n"

    for user_data in players_data.values():
        name = user_data["name"]
        total_buy_in = user_data.get("total_buy_in", 0)

        effective_buy_in = total_buy_in

        for transfer in user_data.get("transfers", []):
            if transfer["type"] == "send":
                effective_buy_in -= transfer["amount"]
            else:
                effective_buy_in += transfer["amount"]

        message += f"{name} (ID: {user_data['ID']}):\n"
        message += f"Effective Buy-in: {effective_buy_in}\n\n"

    get_message(update).reply_text(message)

def add_final_chips(update: Update, context: CallbackContext) -> None:
    get_message(update).reply_text("Please enter your final chip count:")

    return "WAITING_FINAL_CHIP_AMOUNT"

def handle_final_chip_amount(update: Update, context: CallbackContext) -> None:
    user_id = get_message(update).from_user.id
    name = get_message(update).from_user.first_name
    final_chips = float(get_message(update).text)

    players_data[user_id]["final_chips"] = final_chips

    get_message(update).reply_text(f"{name}'s final chips: ${final_chips}")
    return ConversationHandler.END

def settle(update: Update, context: CallbackContext) -> None:
    global players_data

    # Check if all players have entered their final chip amounts
    for user_id, user_data in players_data.items():
        if "final_chips" not in user_data:
            get_message(update).reply_text("Error: Not all players have entered their final chip amounts.")
            return ConversationHandler.END

    # Calculate balances and tally amounts owed and received
    balances = {}
    total_owed = 0
    total_received = 0
    for user_id, user_data in players_data.items():
        name = user_data["name"]
        total_buy_in = user_data["total_buy_in"]
        transfers = user_data.get("transfers", [])
        final_chip_count = user_data["final_chips"]
        effective_buy_in = total_buy_in

        for transfer in transfers:
            if transfer["type"] == "send":
                effective_buy_in -= transfer["amount"]
            else:
                effective_buy_in += transfer["amount"]

        balance = final_chip_count - effective_buy_in
        balances[name] = balance
        if balance < 0:
            total_owed += balance
        else:
            total_received += balance

    # Send the balance report
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    num_players = len(players_data)
    balance_report = f"Settlements ({GAME_TYPE}):\n"
    balance_report += f"Time: {current_time}\n"
    balance_report += f"Number of players: {num_players}\n\n"
    for user_name, balance in balances.items():
        if balance < 0:
            balance_report += f"{user_name} owes ${-balance:.2f}\n"
        else:
            balance_report += f"{user_name} receives ${balance:.2f}\n"

    get_message(update).reply_text(balance_report)

    # Check if the amounts add up
    if total_owed + total_received != 0:
        get_message(update).reply_text(f"Error: The total amount owed (${total_owed:.2f}) does not match the total amount received (${total_received:.2f}).")
    else:
        get_message(update).reply_text(f"The total amount owed and received is ${total_owed:.2f}.")

    # Reset players_data and other global variables
    players_data = {}

    return ConversationHandler.END

def help(update: Update, context: CallbackContext) -> None:
    help_text = (
        "/buy_in - Register your buy-in amount\n"
        "/transfer - Transfer chips to another player\n"
        "/add_final_chips - Add your final chip count\n"
        "/settle - Calculate and display the settlements\n"
        "/game_state - Calculate and display the current effective buy-ins of all players\n"
    )
    get_message(update).reply_text(help_text)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Create a dictionary to store the game type
    global GAME_TYPE
    GAME_TYPE = ""

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(handle_game_type_selection, pattern=r"^game_type\|"))
    dispatcher.add_handler(CommandHandler("help", help))

    poker_handler = ConversationHandler(
        entry_points=[
            CommandHandler("buy_in", buy_in),
            CommandHandler("add_final_chips", add_final_chips),
            CommandHandler("settle", settle),
        ],
        states={
            "WAITING_BUY_IN_AMOUNT": [MessageHandler(Filters.text & ~Filters.command, handle_buy_in_amount)],
            "WAITING_FINAL_CHIP_AMOUNT": [MessageHandler(Filters.text & ~Filters.command, handle_final_chip_amount)],
        },
        fallbacks=[CommandHandler("cancel", end_conversation)],
    )
    dispatcher.add_handler(poker_handler)

    dispatcher.add_handler(CommandHandler("transfer", transfer))
    transfer_selection_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_transfer_selection, pattern=r"^transfer_to\|")],
        states={
            "WAITING_TRANSFER_AMOUNT": [MessageHandler(Filters.text & ~Filters.command, handle_transfer_amount)],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(transfer_selection_handler)

    dispatcher.add_handler(CommandHandler("game_state", display_game_state))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

