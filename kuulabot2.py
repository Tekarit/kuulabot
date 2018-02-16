import telepot
import requests
import time
import os
from bs4 import BeautifulSoup

'''
Second iteration of kuulabot
'''


# Initialization and global variables

with open('token.txt', 'r') as tokenfile:
    TOKEN = tokenfile.read().replace('\n','')
KUULATORI = "https://www.kuulatori.fi"               # URL for kuulatori.fi fronpage
chat_ids = []                                               # List of chat ids that have called /activate
activated = False
initial_largest_index = 0

# msg is the message send by a user
def handle(msg):
    # extracts the content_type, chat_type and chat_id from message
    content_type, chat_type, chat_id = telepot.glance(msg)
    # extracts the text from message to variable 'text'
    text = msg.get('text', '')

    if content_type == 'text':
        if '/activate' in text:
            global activated
            global initial_largest_index

			# Send a message to user that tracking has been activated
            bot.sendMessage(chat_id, 'Activated! Now tracking changes in Kuulatori. Will report any changes on the frontpage')

            # Find currently largest item so we do not initially spam the chat with all frontpage items
            initial_largest_index = max(get_items())

			# Add the 'chat_id' to list (global variable 'chat_ids') to track chats where messages should be send.
            chat_ids.append(chat_id)

            # Changes the bot to "activated" status (mainly for debugging purposes
            activated = True

		# Tells the user what to do is \help is called
        elif '/help' in text:
            ss = r'This the beta version of the KuulaBOT. In order to activate the bot, please use command /activate. This will start tracking of the kuulatori.fi frontpage, and the bot will notify you for any changes on it.'
            bot.sendMessage(chat_id, ss)

		# If the command is not recognized, the user if instructed to use commands \help of \activate
        else:
            ss = r'Command ' + msg['text'] + r' is not recognized. Please use /help or /activate'
            bot.sendMessage(chat_id, ss)

def get_items():
    # Get kuulatori.fi frontpage HTML
    html = requests.get(KUULATORI).text

    # Make soup using BS
    soup = BeautifulSoup(html, 'html.parser')

    # Collect the things inside all a_hrefs in the frontpage and save them to list
    frontpage_a_hrefs = []
    for a in soup.find_all('a', href = True):
        frontpage_a_hrefs.append(a['href'])

    # remove everything not with '/item/' prefix
    frontpage_items = list(filter(lambda x: x.startswith("/item/"), frontpage_a_hrefs))

    # remove text from frontpage_items
    frontpage_item_numbers = map(lambda x: x.strip("/item"), frontpage_items)

    # convert the string into int and remove duplicates
    frontpage_item_numbers = list(set(map(lambda x: int(x), frontpage_item_numbers)))

    # return the list of items
    return frontpage_item_numbers


# These need major redo
# IDEA: From the kuulatori frontpage, create a list of items there. Every 5 minutes, list all items that have larger index than previous highest, send messages and replace the largest value, tada!
def kuulatori_changes(chat_id):
    global initial_largest_index
    # Get all item numbers on the frontpage
    item_numbers = get_items()

    # select the ones that are new
    new_item_numbers = [number for number in item_numbers if number > initial_largest_index]

    # update the largest item index if there are new ones
    if(len(new_item_numbers)>0):
        initial_largest_index = max(new_item_numbers)

    # then loop over them and for each new item, send message to each chat with the url to the item
    # TODO: Include title and price of the item
    for item_number in new_item_numbers:
        ss = "New item: " + KUULATORI + "/item/" + str(item_number)
        bot.sendMessage(chat_id, ss)
    ## chat_id is used to identify chats where messages should be send
    ## kuulatori_old is the previously requested HTML code (snapshot) of kuulatori.fi
    #
    #kuulatori_current = requests.get(KUULATORI).text        # Reads current HTML code (snapshot) of kuulatori.fi
    #
    #if(kuulatori_current != kuulatori_old):                 # Checks if there are any changes in the HTML between current
    #    global kuulatori_old                                                    # and previous snapshot of kuulatori.fi frontpage
    #
    #    bot.sendMessage(chat_id, 'New item on Kuulatori!') # Sends message to selected chat if there are any changes
    #
    #    kuulatori_old = requests.get(KUULATORI).text        # Updates the variable 'kuulatori_old' to correspond to current
    #    #print('this loop does something')                   # snapshot of kuulatori.fi


# Initializes a Telegram Bot with the TOKEN granted by BotFather
bot = telepot.Bot(TOKEN)

# Creates a 'message_loop'
bot.message_loop(handle)

# Infinite loop, until CTRL+C in used in command line or error arises
while 1:
    # Interval between checks of kuulatori.fi, in seconds
    time.sleep(10)
    if(activated):
	# Checks changes for all chats where activated
        for chat_id in chat_ids:
            kuulatori_changes(chat_id)
    else:
	# Prints not activated to console (mostly for debugging purposes)
        print('not activated')
