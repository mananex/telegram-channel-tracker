# This is a simple telegram bot created for tracking new messages in personal chats, groups or channels
### Setup.
Before installing dependencies, go to **[here](https://my.telegram.org/auth?to=apps)** and authorize. After authorization, copy the values in the `api_id` and `api_hash` fields and save them somewhere.

Then go to the telegram bot **[BotFather](https://t.me/BotFather)** and create a new bot. After creating the bot, copy the **bot token** that botfather will give you and save it too. After these steps, install Python 3.x. I'm using Python version 3.12.1


Create a virtual environment and go to it.

Windows:
```
python -m venv channelTrackerVenv
cd channelTrackerVenv
```
Linux:
```
python3 -m venv channelTrackerVenv
cd channelTrackerVenv
```

Then clone this repository into your virtual environment folder: 
```
git clone https://github.com/mananex/telegram-channel-tracker.git
```
...or download the archive of this repository and unzip it, and start the virtual environment.

Windows:
```
scripts\activate
```
Linux:
```
source bin/activate
```

Next, install the necessary libraries to run the script. **(do not leave the virtual environment)**

Windows:
```
pip install -r requirements.txt
```
Linux:
```
pip3 install -r requirements.txt
```
### Configuring
Open the `configuration.py` file with any text editor. You will see the following:
```
API_ID                   = None # integer
API_HASH                 = None # string
BOT_TOKEN                = None # string
ADMIN_ID                 = None # integer
DATABASE_FILENAME        = 'base.db' # sqlite
chat_message_max_letters = 35
```
And now, replace `None` values with the values you copied earlier. Where it says `# string` paste the values inside the quotes (for example: `BOT_TOKEN = "3361714480:BBesiAym_dF_T9wTF03egVlR9YgtFnephoc"`)

**Note:** You need to write your Telegram user ID into the `ADMIN_ID` variable. To get your user ID, go to the bot **[Get My ID](https://t.me/getmyid_bot)** and start it.
### Running the script.
Now, after installing the necessary libraries and script configuration, you can run the script.

Windows:
```
python app.py
```
Linux:
```
python3 app.py
```

### Note: you can find out more about how the script works in DETAILED.md
