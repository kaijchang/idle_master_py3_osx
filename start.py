import requests
from bs4 import BeautifulSoup
import browser_cookie3
import time
import re
import subprocess
import logging
import json

from colorama import init, Fore


class Game:
    def __init__(self, cards_left: int, game_id: str, game_name: str):
        self.cards_left = cards_left
        self.game_id = game_id
        self.game_name = game_name

    def __repr__(self):
        return "{game_name} ({game_id}) - {cards_left} card(s) left".format(**self.__dict__)


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
        self.session.cookies = browser_cookie3.load(domain_name="steamcommunity.com")

        try:
            self.account_id = requests.utils.dict_from_cookiejar(self.session.cookies)["steamLoginSecure"][:17]
        except KeyError:
            self.logger.error(Fore.RED + "Unable to load cookies, login into https://steamcommunity.com then try again." + Fore.RESET)

        self.sort = settings["sort"]
        self.blacklist = settings["blacklist"]
        self.delay_per_card = settings["delayPerCard"]

        self.logger.info(Fore.GREEN + "Finding games that have card drops remaining" + Fore.RESET)

        self.games_left = self.get_games()

    def main(self):
        try:
            while self.games_left:
                game = self.games_left[0]

                self.start_idling(game)

                while game.cards_left != 0:
                    self.logger.info(Fore.BLUE + "Sleeping for {} minutes".format(self.delay_per_card * game.cards_left) + Fore.RESET)
                    time.sleep(self.delay_per_card * game.cards_left * 60)

                    self.update_cards_left(game)

                    if game.cards_left == 0:
                        self.games_left.remove(game)
                        self.stop_idling()

                        self.logger.info(Fore.GREEN + "Finished idling {}, {} games left".format(game.game_name, len(self.games_left)) + Fore.RESET)

            self.logger.info(Fore.GREEN + "Done idling!" + Fore.RESET)

        except KeyboardInterrupt:
            self.stop_idling()

    def update_cards_left(self, game: Game):
        self.logger.info(Fore.GREEN + "Checking how many card drops {} has left".format(game.game_name) + Fore.RESET)

        game_soup = BeautifulSoup(
            self.session.get("https://steamcommunity.com/profiles/{}/gamecards/{}/".format(self.account_id, game.game_id)).text,
            "html.parser"
        )

        game.cards_left = int(re.match(r"([0-9]+|(No)) card drops? remaining", game_soup.find("span", {"class": "progress_info_bold"}).text).group(1)) if re.match(r"([0-9]+|(No)) card drops? remaining", game_soup.find("span", {"class": "progress_info_bold"}).text).group(1) != "No" else 0

        self.logger.info(Fore.GREEN + "{} has {} card drop(s) left".format(game.game_name, game.cards_left) + Fore.RESET)

        return game.cards_left

    def get_games(self):
        game_soup = BeautifulSoup(
            self.session.get("https://steamcommunity.com/profiles/{}/badges".format(self.account_id)).text,
            "html.parser"
        )

        games = list(
            filter(lambda game: game.cards_left != 0, [
                Game(
                    int(re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1)) if re.match(r"([0-9]+|(No)) card drops? remaining", game.find("span", {"class": "progress_info_bold"}).text).group(1) != "No" else 0,
                    int(re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", game.find("a", {"class": "badge_row_overlay"})["href"]).group(1)),
                    game.find("div", {"class": "badge_title"}).text.replace("View details", "").strip()
                ) for game in filter(lambda p: re.match(r"https:\/\/steamcommunity.com\/id\/.+\/gamecards\/([0-9]{6})\/", p.find("a", {"class": "badge_row_overlay"})["href"]) and p.find("span", {"class": "progress_info_bold"}), game_soup.find_all("div", {"class": "badge_row"}))
            ])
        )

        if self.blacklist:
            self.logger.info(Fore.BLUE + "Applying blacklist" + Fore.RESET)

            games_before_blacklist = len(games)

            games = list(
                filter(lambda game: game.game_id not in self.blacklist, games)
            )

            self.logger.info(Fore.BLUE + "The blacklist removed {} games".format(games_before_blacklist - len(games)) + Fore.RESET)

        else:
            self.logger.info(Fore.BLUE + "No blacklist found" + Fore.RESET)

        if self.sort:
            if self.sort == "leastcards":
                games.sort(key=lambda game: game.cards_left)

                self.logger.info(Fore.BLUE + "Sorted from least to most card drops remaining" + Fore.RESET)

            elif self.sort == "mostcards":
                games.sort(key=lambda game: game.cards_left, reverse=True)

                self.logger.info(Fore.BLUE + "Sorted from most to least card drops remaining" + Fore.RESET)

            else:
                self.logger.warning(Fore.RED + "Skipping sort in config, unknown sort type: {}".format(self.sort) + Fore.RESET)

        else:
            self.logger.info(Fore.BLUE + "No sort found" + Fore.RESET)

        self.logger.info(Fore.GREEN + "Found {} games and {} trading cards to idle:".format(
            len(games),
            sum(game.cards_left for game in games)) + Fore.RESET)

        for game in games:
            self.logger.info(Fore.WHITE + repr(game) + Fore.RESET)

        return games

    def start_idling(self, game: Game):
        self.logger.info(Fore.GREEN + "Starting to idle {}".format(game) + Fore.RESET)
        try:
            self.child = subprocess.Popen(["./steam-idle", str(game.game_id)])

        except PermissionError:
            subprocess.Popen(["chmod", "+x", "./steam-idle"])
            self.child = subprocess.Popen(["./steam-idle", str(game.game_id)])

    def stop_idling(self):
        self.logger.info(Fore.GREEN + "Killing steam-idle process" + Fore.RESET)
        self.child.terminate()


with open("settings.json") as settings_file:
    idler = SteamIdle(**json.load(settings_file))
    idler.main()
