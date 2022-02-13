import requests
import sys
import os
import re
from bs4 import BeautifulSoup
from colorama import Fore, init, Style
init()
regex_url = r'[https?://www\.]?.*\..*'


class Browser:

    def __init__(self, args):
        self.arg = args[1]
        self.hist = []

    @staticmethod
    def cheking_url(inp):
        """add 'https://' if it's not included"""
        if not inp[:8] == "https://":
            return "https://" + inp
        else:
            return inp

    @staticmethod
    def req_parsing(url):
        """get request, pars content, and highlight the output"""
        req = requests.get(url)
        tags = ['p', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        soup = BeautifulSoup(req.content, 'html.parser').body.descendants
        page = ""
        for descendant in soup:
            if descendant.name in tags:
                if descendant.name == 'a':
                    page += Fore.BLUE + descendant.get_text().strip() + "\n"
                else:
                    page += Style.RESET_ALL + descendant.get_text().strip() + "\n"
        return page

    def create_dir(self):
        """Create the directory with saved pages"""
        if not os.access(self.arg, os.F_OK):
            os.mkdir(self.arg)
        os.chdir(self.arg)

    def back(self):
        """return previous page"""
        try:
            print(self.hist.pop(-2))
#           looks like cheating with stack :)
        except IndexError:
            pass

    def go(self):
        """main algorithm"""
        self.create_dir()
        while True:
            user_inp = str(input())
            url = self.cheking_url(user_inp)
            file_path = self.arg + "\\" + user_inp
            if re.findall(regex_url, url):
                print(self.req_parsing(url))
                with open(user_inp, "w") as f:
                    f.write(self.req_parsing(url))
                    self.hist.append(self.req_parsing(url))
            elif os.path.isfile(file_path):
                with open(user_inp) as f:
                    print(f.read())
            elif user_inp == "back":
                self.back()
            elif user_inp == "exit":
                break
            else:
                print("Incorrect URL")


def main():
    my_browser = Browser(sys.argv)
    my_browser.go()


if __name__ == "__main__":
    main()
