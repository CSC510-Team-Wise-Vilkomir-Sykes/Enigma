<h1 align="center">
# ✨ ♬  ᴇɴɪɢᴍᴀ ♬  ✨
**Your Ultimate Music Recommender Bot for Discord**

 [![Open Source Love](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
</h1>

<div align="center">

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Release](https://img.shields.io/github/release/CSC510-Team-Wise-Vilkomir-Sykes/Enigma.svg)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/releases)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/CSC510-Team-Wise-Vilkomir-Sykes/Enigma.svg)](https://img.shields.io/github/repo-size/CSC510-Team-Wise-Vilkomir-Sykes/Enigma.svg)
[![Language](https://img.shields.io/badge/language-Python-1f425f.svg)](https://www.python.org/)
[![GitHub contributors](https://img.shields.io/badge/contributors-3-green)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/graphs/contributors)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/CSC510-Team-Wise-Vilkomir-Sykes/Enigma)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/issues?q=is%3Aissue+is%3Aopen)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/CSC510-Team-Wise-Vilkomir-Sykes/Enigma)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/pulls?q=is%3Apr+is%3Aopen)
[![Supports Python](https://img.shields.io/pypi/pyversions/pytest)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14225873.svg)](https://doi.org/10.5281/zenodo.14225873)

Code coverage (develop):[![Running Code Coverage](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/codecov.yml/badge.svg)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/codecov.yml)
Syntax checker and code formatter: [![Code checker](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/code-formatter.yml/badge.svg)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/code-formatter.yml)
Style checker: [![Style Check](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/style-checker.yml/badge.svg?branch=develop)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/style-checker.yml)
Run unit tests: [![Run Tests](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/github-actions-build.yml/badge.svg)](https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/actions/workflows/github-actions-build.yml)

</div>

<p align="center">
    <a href="https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/issues/new/choose">Report Bug</a>
    ·
    <a href="https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma/issues/new/choose">Request Feature</a>
</p>

---

## **Why Enigma?**
> https://youtu.be/hOm4ca4YgeQ
[![YouTube](http://i.ytimg.com/vi/hOm4ca4YgeQ/hqdefault.jpg)](https://www.youtube.com/watch?v=hOm4ca4YgeQ)

## **Features**

- Recommends songs based on user input and plays them in Discord voice channels.
- Designed for teams or friends to enjoy music together.
- Acts as an amplifier to play the same music on multiple speakers, creating a surround sound effect and increasing volume output.
- Provides controls to toggle music playback (pause/resume).
- Plays custom songs directly without searching on YouTube.
- Enables users to switch back and forth between songs, manage the queue, and replay songs.
- Dynamic queue management: Custom songs are added to the queue instead of being played instantly.
- Multi-channel support: The bot maintains a consistent internal state across several voice channels.
- Replay flexibility: Supports both instant and delayed replay of songs.
- Advanced queue operations:
    - Insert songs at any point in the queue.
    - Reorder songs in the queue dynamically.
    - Remove songs from the queue.
- Improved recommendations:
    - Recommendations are dynamically generated from the current queue.
    - Based on specific artists and genres, not just "liked" or "disliked" songs.

---


## **Group 6 Contributions**

### **Video of our additions:**
> https://youtu.be/eta7pT2b0v4

https://github.com/user-attachments/assets/0723f5ae-83d0-4749-8181-24f7c5bd4735


### **Improvements and Features Added**

1. **Preloading Songs in Queue:**
    - Previously, when the `/next` command was used, the bot would take time to download the next song, causing a buffering delay.
    - With the new addition, the first five songs in the queue are preloaded (pre-downloaded).
    - Now, the bot plays the next song instantly when `/next` is issued, eliminating download wait times.

2. **Volume Control Command:**
    - Added the `/volume <percentage>` command to adjust playback volume dynamically.
    - Example: `/volume 50` sets the bot’s playback volume to 50%.

3. **Exploratory Data Analysis (EDA) Features:**
    - Developed functions in `eda.py` to analyze music data and provide insights to users:
        - `!top_songs`: Displays the top 10 songs based on Billboard charts.
        - `!top_songs add`: Displays the top 10 songs and adds them to the playlist.
        - `!top_artists`: Displays the top 10 artists.
        - `!longest_charting`: Displays the top 10 longest-charting songs.
        - `!longest_charting add`: Displays and adds the longest-charting songs to the playlist.
    - These functions integrate seamlessly with the bot commands, providing users with valuable music insights.

4. **Web Scraping for Music Data:**
    - Introduced web scraping functionality in `scraper.py` to extract and update music charts.
    - Features:
        - Initial scraping of Billboard music charts.
        - Periodic updates using the `schedule` module to ensure data freshness.

---


## **🚀 Installation Procedure**

### **1. Prerequisites**

- [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [VSCode Setup Guide](https://code.visualstudio.com/docs/setup/setup-overview)
- [Install FFMPEG](https://www.gyan.dev/ffmpeg/builds) and add it to your path. [Guide](https://www.thewindowsclub.com/how-to-install-ffmpeg-on-windows-10#:~:text=Add%20FFmpeg%20to%20Windows%20path%20using%20Environment%20variables)
- [Set up and invite a bot](https://discordpy.readthedocs.io/en/stable/discord.html).

---

### **2. Running Code**

1. Clone the repository and navigate to the directory:
   ```bash
   $ git clone https://github.com/CSC510-Team-Wise-Vilkomir-Sykes/Enigma.git
   $ cd Enigma
   ```
2. Create a `.env` file with the following:
   `DISCORD_TOKEN=#YOUR_SECRET_TOKEN#`
3. Install dependencies and run the bot:
   ```bash
   $ pip install -r requirements.txt
   $ python bot.py
   ```
4. Join a Discord server, connect to a voice channel, and interact with the bot.
   Use `/join` to invite the bot to your channel and `/help` for command options.

---

## **📖 Documentation**

Find the full documentation [here]([https://saswat123.github.io/Enigma/](https://csc510-team-wise-vilkomir-sykes.github.io/Enigma-docs/)).

---

## **👥 Contributors**

| Contributor       | GitHub Profile                         |
|-------------------|----------------------------------------|
| Katerina Vilkomir | [Kii4ka](https://github.com/Kii4ka)    |
| Madeline Wise     | [madewise](https://github.com/madewise)|
| Jackson Sykes     | [ScenicJaguar101](https://github.com/ScenicJaguar101) |

---

## **Contributing**

For contributing, see the [CONTRIBUTING](CONTRIBUTING.md) guide.

---

## **Data**

The project dataset is available [here](https://www.kaggle.com/datasets/saurabhshahane/music-dataset-1950-to-2019).

---

## **Support**

For bugs or feature requests, use GitHub’s issue tracker or email the contributors.

