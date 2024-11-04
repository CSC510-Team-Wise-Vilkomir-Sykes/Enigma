<h1 align="center">
  Enigma 🤖 - A music recommender bot for Discord
  
 [![Open Source Love](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
</h1>

<div align="center">

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# [![GitHub Release](https://img.shields.io/github/release/CSC510-Team87/Enigma.svg)](https://github.com/CSC510-Team87/Enigma/releases)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/CSC510-Team87/Enigma.svg)](https://img.shields.io/github/repo-size/CSC510-Team87/Enigma.svg)
[![Language](https://img.shields.io/badge/language-Python-1f425f.svg)](https://www.python.org/)
[![GitHub contributors](https://img.shields.io/badge/contributors-3-green)](https://github.com/CSC510-Team87/Enigma/graphs/contributors)
[![Open Issues](https://img.shields.io/badge/issues-0-yellow)](https://github.com/CSC510-Team87/Enigma/issues)
[![Pull Requests](https://img.shields.io/badge/pull%20requests-0-yellow)](https://github.com/CSC510-Team87/Enigma/pulls)
![Supports Python](https://img.shields.io/pypi/pyversions/pytest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14032034.svg)](https://doi.org/10.5281/zenodo.14032034)
[![codecov](https://codecov.io/gh/CSC510-Team87/Enigma/branch/dev/graph/badge.svg?token=OEPEJ0W8CR)](https://codecov.io/gh/CSC510-Team87/Enigma)
[![Build Status](https://github.com/CSC510-Team87/Enigma/actions/workflows/github-actions-build.yml/badge.svg)](https://github.com/CSC510-Team87/Enigma/actions/workflows/github-actions-build.yml)
[![Code Formatter](https://github.com/CSC510-Team87/Enigma/actions/workflows/code-formatter.yml/badge.svg)](https://github.com/CSC510-Team87/Enigma/actions/workflows/code-formatter.yml)
[![Syntax Checker](https://github.com/CSC510-Team87/Enigma/actions/workflows/syntax-checker.yml/badge.svg)](https://github.com/CSC510-Team87/Enigma/actions/workflows/syntax-checker.yml)
[![Style Checker](https://github.com/CSC510-Team87/Enigma/actions/workflows/style-checker.yml/badge.svg)](https://github.com/CSC510-Team87/Enigma/actions/workflows/style-checker.yml)


</div>

<p align="center">
    <a href="https://github.com/rahulgautam21/Enigma/issues/new/choose">Report Bug</a>
    ·
    <a href="https://github.com/rahulgautam21/Enigma/issues/new/choose">Request Feature</a>
</p>

<h1> 💡 Features </h1>

<div>
<ul>
  <li>Recommend songs based on user input and play them on discord voice channel</li>
  <li>Can be used by teams/friends to listen to the same songs together</li>
  <li>Acts as an amplifier - can be used to play same music on multiple speakers to give a surround sound effect and increase volume output</li>
  <li>Ability to toggle music pause/resume</li>
  <li>Ability to play custom song without having to search the song on youtube</li>
  <li>Ability to switch back and forth between songs</li>
  <li>Ability to move songs around in the queue and replay songs</li>
</ul>
If you want to get added to the music server on discord to test the bot, drop an email to spriyad2@ncsu.edu
</div>
  
<h1> Features added by Group 87</h1>

<div>
<ul>
  <li>Custom songs are now put into the queue dynamically instead of being played instantly</li>
  <li>The bot is able to be used across several voice channels while still keeping a consistent internal state</li>
  <li>The bot has both instant and delayed replay of songs</li>
  <li>The bot can have songs inserted at any point in the queue</li>
  <li>The bot can have songs in the queue moved around to any arbitrary order even while running</li>
  <li>Songs can be removed from the queue</li>
  <li>More dynamic recommendation features: Recommendations will be made now from an arbitrary number of songs already present in the queue, and are based on particular artists and genres rather than simply "liked" and "disliked" songs</li>
</ul>
</div>

<h1> ⚒️ Installation Procedure </h1>


## 1. Prerequisites 

  * Modules in requirements.txt may only be compatible with Python 3.10
  * Install FFMPEG from [FFMPEG builds](https://www.gyan.dev/ffmpeg/builds), extract it and add it to your path [How to add FFMPEG to Path](https://www.thewindowsclub.com/how-to-install-ffmpeg-on-windows-10#:~:text=Add%20FFmpeg%20to%20Windows%20path%20using%20Environment%20variables&text=In%20the%20Environment%20Variables%20window,bin%5C%E2%80%9D%20and%20click%20OK.)

## 2. Running Code

First, clone the repository and cd into the folder:

```
$ git clone git@github.com:rahulgautam21/Enigma.git
$ cd Enigma
```

### Create a .env file with the discord token info: DISCORD_TOKEN=#SECRET_TOKEN#
### Join the discord channel of the bot [Discord Channel of bot](https://discord.com/channels/1017135653315686490/1017135653789646850) and connect to the voice channel.

```
$ pip install -r requirements.txt
$ python bot.py 
```

You can now use the discord bot to give music recommendations! Use /help to see all functionalities of bot.

<h1> 🚀 Video 1 - Why you should choose this project for project 3 (Team 87) </h1>

<a href="https://youtu.be/HvIVuy2wMXY">https://youtu.be/HvIVuy2wMXY</a>

<h1> 🚀 Video 2 - New Feature Showcase </h1>

<a href="https://youtu.be/fvlnV4p7qdk">https://youtu.be/fvlnV4p7qdk</a>

<h1>📍RoadMap </h1>

What We've Done:
1. Custom songs are now put into the queue dynamically instead of being played instantly
2. The bot is able to be used across several voice channels while still keeping a consistent internal state
3. The bot has both instant and delayed replay of songs
4. The bot can have songs inserted at any point in the queue
5. The bot can have songs in the queue moved around to any arbitrary order even while running
6. Songs can be removed from the queue
7. More dynamic recommendation features: Recommendations will be made now from an arbitrary number of songs already present in the queue, and are based on particular artists and genres rather than simply "liked" and "disliked" songs

What We've Yet To Do:
1. Allow for seemless transitions between songs by automatically detecting when a song is about to finish, the pre-loading the next song in the queue.
2. Have the database of song recommendations update automatically for when new songs come out
3. Improved sound quality of the audio playback to be fully integrated into Discord's built in volume adjuster (currently peaks the audio in some extreme cases) 



<h1>📖 Documentation</h1>

Documentation for the code available at - <a href="https://saswat123.github.io/Enigma/">Enigma Docs</a>  


<h1> 👥 Contributors <a name="Contributors"></a> </h1>

### Group 87

<table>
  <tr>
    Gwen Mason
    Yi Zhang
    Kevin Dai
  </tr>

</table>

<h1> Contributing </h1>

Please see [`CONTRIBUTING`](CONTRIBUTING.md) for contributing to this project.

<h1> Data </h1>

The data for this project is present [here](https://www.kaggle.com/datasets/saurabhshahane/music-dataset-1950-to-2019)

<h1> Support </h1>
For any and all support reach out to spriyad2@ncsu.edu or gwenmason125@ncsu.edu
For bug ticket request, use the internal Github ticketing features, or reach out to one of the emails above.
