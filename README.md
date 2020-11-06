[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a5eff1b92655481fb66ef90db72debaa)](https://www.codacy.com/app/Apache-HB/Robo-Claymore?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Apache-HB/Robo-Claymore&amp;utm_campaign=Badge_Grade)
[![Discord Server](https://discordapp.com/api/guilds/441399366000050197/widget.png?style=shield)](https://discord.gg/y3uSzCK)

# Robo Claymore
beep boop

# bot setup

install prereqs
```sh
sudo apt update && apt upgrade
sudo apt install python3.8 python3.8-dev
```

create a config.ini
```ini
[discord]
token = discord-bot-token
prefix = discord-prefix
activity = default-activity
owner = user-id

[mongo]
url = mongo-url
db = mongo-db-name

[keys]
wolfram = wolfram-key
github = github-app-key
docs = readthedocs.io-key
```

run bot
```
python3.8 -m pip install -r requirements.txt
cd source/
python3.8 main.py
```
