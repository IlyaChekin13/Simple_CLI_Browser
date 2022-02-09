from hstest.stage_test import *
import requests
import os
import shutil
import sys
if sys.platform.startswith("win"):
    import _locale
    # pylint: disable=protected-access
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class TextBasedBrowserTest(StageTest):

    def generate(self):

        dir_for_files = 'tb_tabs'
        return [
            TestCase(
                stdin='bloomberg.com\nexit',
                attach='bloomberg.com',
                args=[dir_for_files]
            ),
            TestCase(
                stdin='docs.python.org\nexit',
                attach='docs.python.org',
                args=[dir_for_files]
            )
        ]

    def compare_pages(self, output_page, ideal_page):
        ideal_page = ideal_page.split('\n')
        for line in ideal_page:
            if line.strip() not in output_page:
                return False, line.strip()
        return True, ""

    def _check_files(self, path_for_tabs: str, ideal_page: str):
        """
        Helper which checks that browser saves visited url in files and
        provides access to them.

        :param path_for_tabs: directory which must contain saved tabs
        :param ideal_page: HTML code of the needed page
        """

        path, dirs, filenames = next(os.walk(path_for_tabs))

        for file in filenames:
            print("file: {}".format(file))
            with open(os.path.join(path_for_tabs, file), 'r', encoding='utf-8') as tab:
                try:
                    content = tab.read()
                except UnicodeDecodeError:
                    raise WrongAnswer('An error occurred while reading your saved tab. '
                                      'Perhaps you used the wrong encoding?')
                is_page_saved_correctly, wrong_line = self.compare_pages(content, ideal_page)
                if not is_page_saved_correctly:
                    raise WrongAnswer(f"The following line is missing from the file {file}:\n"
                                      f"\'{wrong_line}\'\n"
                                      f"Make sure you output the needed web page to the file\n"
                                      f"and save the file in the utf-8 encoding.")

    @staticmethod
    def get_page(url):

        url = f'https://{url}'
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/70.0.3538.77 Safari/537.36"
        try:
            page = requests.get(url, headers={'User-Agent': user_agent})
        except requests.exceptions.ConnectionError:
            raise WrongAnswer(f"An error occurred while tests tried to connect to the page {url}.\n"
                              f"Please try again a bit later.")
        return page.text

    def check(self, reply, attach):

        # Incorrect URL
        if attach is None:
            if '<p>' in reply:
                return CheckResult.wrong('You haven\'t checked whether the URL was correct')
            else:
                return CheckResult.correct()

        # Correct URL
        if isinstance(attach, str):
            path_for_tabs = os.path.join(os.curdir, 'tb_tabs')

            if not os.path.isdir(path_for_tabs):
                return CheckResult.wrong("There is no directory for tabs")

            ideal_page = TextBasedBrowserTest.get_page(attach)
            self._check_files(path_for_tabs, ideal_page)

            try:
                shutil.rmtree(path_for_tabs)
            except PermissionError:
                return CheckResult.wrong("Impossible to remove the directory for tabs. \n"
                                         "Perhaps you haven't closed some file?")

            is_page_printed_correctly, wrong_line = self.compare_pages(reply, ideal_page)
            if not is_page_printed_correctly:
                return CheckResult.wrong(f"The following line in missing from your console output:\n"
                                         f"\'{wrong_line}\'\n"
                                         f"Make sure you output the needed web page to the console.")

            return CheckResult.correct()


TextBasedBrowserTest().run_tests()
