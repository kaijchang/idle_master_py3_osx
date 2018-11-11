import requests
from bs4 import BeautifulSoup
import time
import re
import subprocess
import logging
import json

from colorama import init, Fore


class Game:
    def __init__(self, cardsLeft, gameId, gameName):
        self.cardsLeft = cardsLeft
        self.gameId = gameId
        self.gameName = gameName

    def __repr__(self):
        return "{gameName} ({gameId}) - {cardsLeft} card(s) left".format(**self.__dict__)


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

        self.accountId = settings["steamLoginSecure"][:17]

        self.logger.info(Fore.GREEN + "Finding games that have card drops remaining" + Fore.RESET)

        self.gamesLeft = self.getGames()

    def main(self):
        try:
            while self.gamesLeft:
                game = self.gamesLeft[0]

                self.startIdling(game)

                while game.cardsLeft != 0:
                    self.logger.info(Fore.BLUE + "Sleeping for {} minutes".format(5 * game.cardsLeft) + Fore.RESET)
                    time.sleep(5 * game.cardsLeft * 60)

                    self.updateCardsLeft(game)

                    if game.cardsLeft == 0:
                        self.gamesLeft.remove(game)
                        self.stopIdling()

                        self.logger.info(Fore.GREEN + "Finished idling {}, {} games left".format(game.gameName, len(self.gamesLeft)) + Fore.RESET)

            self.logger.info(Fore.GREEN + "Done idling!" + Fore.RESET)

        except KeyboardInterrupt:
            self.stopIdling()

    def updateCardsLeft(self, game):
        self.logger.info(Fore.GREEN + "Checking how many card drops {} has left".format(game.gameName) + Fore.RESET)

        gameSoup = BeautifulSoup(
            self.session.get("https://steamcommunity.com/profiles/{}/gamecards/{}/".format(self.accountId, game.gameId)).text,
            "html.parser"
        )

        game.cardsLeft = int(re.match(r"([0-9]+|(No)) card drops? remaining", gameSoup.find("span", {"class": "progress_info_bold"}).text).group(1)) if re.match(r"([0-9]+|(No)) card drops? remaining", gameSoup.find("span", {"class": "progress_info_bold"}).text).group(1) != "No" else 0

        self.logger.info(Fore.GREEN + "{} has {} card drop(s) left".format(game.gameName, game.cardsLeft) + Fore.RESET)

        return game.cardsLeft

    def getGames(self):
        gameSoup = BeautifulSoup(
            self.session.get("http://steamcommunity.com/profiles/{}/badges".format(self.accountId)).text,
            "html.parser"
        )

        games = list(
            filter(lambda game: game.cardsLeft != 0, [
                Game(
                    int(re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1)) if re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1) != "No" else 0,
                    int(re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", game.find("a", {"class": "badge_row_overlay"})["href"]).group(1)),
                    game.find("div", {"class": "badge_title"}).text.replace("View details", "").strip()
                ) for game in filter(lambda p: re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", p.find("a", {"class": "badge_row_overlay"})["href"]) and p.find("span", {"class": "progress_info_bold"}), gameSoup.find_all("div", {"class": "badge_row"}))
            ])
        )

        self.logger.info(Fore.GREEN + "Found {} games and {} trading cards to idle:".format(
            len(games),
            sum(game.cardsLeft for game in games)) + Fore.RESET)

        for game in games:
            self.logger.info(Fore.WHITE + repr(game) + Fore.RESET)

        return games

    def startIdling(self, game):
        self.logger.info(Fore.GREEN + "Starting to idle {}".format(game) + Fore.RESET)
        try:
            self.child = subprocess.Popen(["./steam-idle", str(game.gameId)])

        except PermissionError:
            subprocess.Popen(["chmod", "+x", "./steam-idle"])
            self.child = subprocess.Popen(["./steam-idle", str(game.gameId)])

    def stopIdling(self):
        self.logger.info(Fore.GREEN + "Killing Idle Master process" + Fore.RESET)
        self.child.terminate()


with open("settings.json") as settings_file:
    idler = SteamIdle(**json.load(settings_file))
    idler.main()
