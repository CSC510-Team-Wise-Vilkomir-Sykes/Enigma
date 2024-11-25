<h1 align="center">🎵 Enigma 🎶</h1>  
<p align="center"><b>Your Ultimate Music Recommender Bot for Discord</b></p>

<p align="center">
  <a href="https://github.com/ellerbrock/open-source-badges/">
    <img src="https://badges.frapsoft.com/os/v3/open-source.png?v=103" alt="Open Source Love"/>
  </a>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="License">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/releases">
    <img src="https://img.shields.io/github/release/CSC510-Team87/Enigma.svg" alt="Latest Release">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma">
    <img src="https://img.shields.io/github/repo-size/CSC510-Team87/Enigma.svg" alt="Repository Size">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/language-Python-1f425f.svg" alt="Language">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/graphs/contributors">
    <img src="https://img.shields.io/badge/contributors-3-green" alt="Contributors">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/issues">
    <img src="https://img.shields.io/badge/issues-0-yellow" alt="Open Issues">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/pulls">
    <img src="https://img.shields.io/badge/pull%20requests-0-yellow" alt="Pull Requests">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/pypi/pyversions/pytest" alt="Python Versions">
  </a>
  <a href="https://doi.org/10.5281/zenodo.14032034">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.14032034.svg" alt="DOI">
  </a>
  <a href="https://codecov.io/gh/CSC510-Team87/Enigma">
    <img src="https://codecov.io/gh/CSC510-Team87/Enigma/branch/dev/graph/badge.svg?token=OEPEJ0W8CR" alt="Code Coverage">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/actions/workflows/github-actions-build.yml">
    <img src="https://github.com/CSC510-Team87/Enigma/actions/workflows/github-actions-build.yml/badge.svg" alt="Build Status">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/actions/workflows/code-formatter.yml">
    <img src="https://github.com/CSC510-Team87/Enigma/actions/workflows/code-formatter.yml/badge.svg?branch=dev" alt="Code Formatter">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/actions/workflows/syntax-checker.yml">
    <img src="https://github.com/CSC510-Team87/Enigma/actions/workflows/syntax-checker.yml/badge.svg" alt="Syntax Checker">
  </a>
  <a href="https://github.com/CSC510-Team87/Enigma/actions/workflows/style-checker.yml">
    <img src="https://github.com/CSC510-Team87/Enigma/actions/workflows/style-checker.yml/badge.svg" alt="Style Checker">
  </a>
</p>

---


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

## **📹 Showcase Videos**

### [Why Choose This Project?](https://youtu.be/HvIVuy2wMXY)  
### [Feature Showcase](https://youtu.be/fvlnV4p7qdk)

---

## **📍Roadmap**

### Completed:
1. Dynamic queuing and replay options.  
2. Advanced queue management (insert, move, delete).  
3. Multi-channel support with consistent internal state.  
4. Enhanced recommendation logic based on artists/genres.  
5. EDA features integrated for music insights.  
6. Web scraping functionality for periodic music chart updates.

### Planned:
1. Seamless transitions with preloaded songs.  
2. Auto-updating song recommendation database.  
3. Improved sound quality with Discord’s volume adjuster.

---

## **📖 Documentation**

Find the full documentation [here](https://saswat123.github.io/Enigma/).

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

