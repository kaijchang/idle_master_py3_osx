import requests
from bs4 import BeautifulSoup
import time
import re
import subprocess
import sys
import logging
import datetime
import ctypes
import json

from colorama import init, Fore


class Game:
    def __init__(self, cardsLeft, gameId, gameName):
        self.cardsLeft = cardsLeft
        self.gameId = gameId
        self.gameName = gameName

    def __repr__(self):
        return "{gameName} ({gameId}) - {cardsLeft}".format(**self.__dict__)


class SteamIdle:
    def __init__(self, **settings):
        init()

        self.logger = logging.getLogger("Idle Master")

        logging.basicConfig(filename="idlemaster.log", filemode="w", format="[ %(asctime)s ] %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.DEBUG)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("[ %(asctime)s ] %(message)s", "%m/%d/%Y %I:%M:%S %p"))
        self.logger.addHandler(console)

        self.logger.info(Fore.GREEN + "WELCOME TO IDLE MASTER" + Fore.RESET)

        self.session = requests.Session()
        self.session.cookies.set(name="steamLoginSecure", value=settings["steamLoginSecure"])
        self.session.cookies.set(name="sessionid", value=settings["sessionid"])
        self.session.cookies.set(name="steamparental", value=settings["steamparental"])

        self.id_ = settings["steamLoginSecure"][:17]

        self.logger.info("Finding games that have card drops remaining")

        self.games = self.getGames()

    def getGames(self):
        gameSoup = BeautifulSoup(
            self.session.get("http://steamcommunity.com/profiles/{}/badges".format(self.id_)).text,
            "html.parser")

        games = [
            Game(
                int(re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1)) if re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1) != "No" else 0,
                int(re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", game.find("a", {"class": "badge_row_overlay"})["href"]).group(1)),
                game.find("div", {"class": "badge_title"}).text.replace("View details", "").strip()
            ) for game in filter(lambda p: re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", p.find("a", {"class": "badge_row_overlay"})["href"]) and p.find("span", {"class": "progress_info_bold"}), gameSoup.find_all("div", {"class": "badge_row"})[:-1])
        ]

        self.logger.info(Fore.GREEN + "Found {} games and {} trading cards to idle".format(
            len(games),
            sum(game.cardsLeft for game in games)) + Fore.RESET)

        return games


with open("settings.json") as settings_file:
    SteamIdle(**json.load(settings_file))
