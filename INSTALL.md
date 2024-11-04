## 1. Prerequisites 

Installation Guides:
  * [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  * [IDE Installation Guide (VSCode)](https://code.visualstudio.com/docs/setup/setup-overview)
  * Install FFMPEG from [FFMPEG builds](https://www.gyan.dev/ffmpeg/builds), extract it and add it to your path [How to add FFMPEG to Path](https://www.thewindowsclub.com/how-to-install-ffmpeg-on-windows-10#:~:text=Add%20FFmpeg%20to%20Windows%20path%20using%20Environment%20variables&text=In%20the%20Environment%20Variables%20window,bin%5C%E2%80%9D%20and%20click%20OK.)
  * [Set up a bot and invite it to your server](https://discordpy.readthedocs.io/en/stable/discord.html)

## 2. Running Code

First, clone the repository and cd into the folder:

```
$ git clone https://github.com/CSC510-Team87/Enigma.git
$ cd Enigma
```

### Create a .env file with the discord token info: DISCORD_TOKEN=#SECRET_TOKEN#
### Join a discord server and connect to any voice channel.

```
$ pip install -r requirements.txt
$ python bot.py 
```

Use /join to get the bot join the same voice chanel as you. You can now use the discord bot to give music recommendations! Use /help to see all functionalities of bot.
