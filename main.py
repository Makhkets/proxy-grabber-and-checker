import requests
import threading
from bs4 import BeautifulSoup

import coloredlogs
import verboselogs

import os
import sys

level_styles = {'debug': {'color': 8},
                'info': {},
                'warning': {'color': 11},
                'error': {'color': 'red'},
                'critical': {'bold': True, 'color': 'red'},

                'spam': {'color': 'green', 'faint': True},
                'verbose': {'color': 'blue'},
                'notice': {'color': 'magenta'},
                'success': {'bold': True, 'color': 'green'},
                }

logfmtstr = "%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s"
logfmt = coloredlogs.ColoredFormatter(logfmtstr, level_styles=level_styles)

logger = verboselogs.VerboseLogger("@BENEFIXX")

coloredlogs.install(fmt=logfmtstr, stream=sys.stdout, level_styles=level_styles,
                    milliseconds=True, level='DEBUG', logger=logger)

class Proxy:
    def __init__(self, output, threads) -> None:
        self.output = output
        self.threads = threads
        self.proxy = []
        self.url_list = [
                                            "https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt",
                                            "https://github.com/ShiftyTR/Proxy-List/blob/master/http.txt",
                                            "https://github.com/ShiftyTR/Proxy-List/blob/master/https.txt",
                        ]

    def grab(self):
        proxies = []
        for url in self.url_list:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            for element in soup.find("table", {"class": "highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file"}).find_all("tr"):
                proxies.append(element.text.strip())
        logger.info(f"Нашел {len(proxies)} прокси")
        for proxy in proxies:
            self.proxy.append(proxy)
        return proxies

    def check(self):
        while len(self.proxy) > 0:
            try:
                proxy = self.proxy.pop()
                response = requests.get("https://httpbin.org/", proxies={"https": f"http://{proxy}", "http": f"http://{proxy}"})
                if response.status_code == 200:
                    if os.path.isfile("output.txt"):
                        with open("output.txt", "a", encoding="utf-8") as file:
                            logger.success(f"Нашел валидный прокси: {proxy}")
                            file.write(proxy + "\n")
                    else:
                        logger.error("Не нашел файл output.txt")
                        with open("output.txt", "w", encoding="utf-8") as file:
                            file.write("127.0.0.1:8000")
                            logger.success("Создал файл output.txt")
            except Exception as ex: pass

    def launch(self):
        self.grab()
        for u in self.url_list:
            logger.debug(f"PARSE: {u}")
        for th in range(self.threads + 1):
            threading.Thread(target=self.check).start()

    def save_html(self, response: str):
        with open("html.html", "w", encoding="utf-8") as file: file.write(response)

Proxy("output.txt", 300).launch()