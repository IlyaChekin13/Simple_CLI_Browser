import requests
import sys
import os
import re
regex_url = r'[https?://www\.]?.*\..*'


class Browser:

    def __init__(self, args):
        self.arg = args[1]
        self.hist = []

    def create_dir(self):
        """Create the directory with saved pages"""
        if not os.access(self.arg, os.F_OK):
            os.mkdir(self.arg)
        os.chdir(self.arg)

    def go(self):
        """main algorithm"""
        self.create_dir()
        while True:
            user_inp = str(input())
            url = self.cheking_url(user_inp)
            file_path = self.arg + "\\" + user_inp
            if re.findall(regex_url, url):
                req = requests.get(url)
                print(req.text)
                with open(user_inp, "w") as f:
                    f.write(req.text)
            elif os.path.isfile(file_path):
                with open(user_inp) as f:
                    print(f.read())
            elif user_inp == "back":
                self.back()
            elif user_inp == "exit":
                break
            else:
                print("URL Error")

    @staticmethod
    def cheking_url(inp):
        if not inp[:8] == "https://":
            return "https://" + inp

    def back(self):
        try:
            print(self.hist.pop(-2))
#           looks like cheating with stack :)
        except IndexError:
            pass


def main():
    my_browser = Browser(sys.argv)
    my_browser.go()


if __name__ == "__main__":
    main()
