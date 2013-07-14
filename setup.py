"""
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

from distutils.core import setup, Command
from distutils.errors import DistutilsOptionError
from unittest import TestLoader, TextTestRunner
import sys
import steam

class run_tests(Command):
    description = "Run the steamodd unit tests"

    user_options = [
            ("key=", 'k', "Your API key")
            ]

    def initialize_options(self):
        try:
            self.key = steam.api.key.get()
        except steam.api.APIKeyMissingError:
            self.key = None

    def finalize_options(self):
        if not self.key:
            raise DistutilsOptionError("API key is required")
        else:
            steam.api.key.set(self.key)

        # Generous timeout so slow server days don't cause failed builds
        steam.api.socket_timeout.set(20)

    def run(self):
        tests = TestLoader().discover("tests")
        results = TextTestRunner(verbosity = 2).run(tests)
        sys.exit(int(not results.wasSuccessful()))

setup(name = "steamodd",
      version = steam.__version__,
      description = "High level Steam API implementation with low level reusable core",
      long_description = "Please see the `README <https://github.com/Lagg/steamodd/blob/master/README.md>`_ for a full description.",
      packages = ["steam"],
      author = steam.__author__,
      author_email = steam.__contact__,
      url = "https://github.com/Lagg/steamodd",
      classifiers = [
          "License :: OSI Approved :: ISC License (ISCL)",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python"
          ],
      license = steam.__license__,
      cmdclass = {"run_tests": run_tests})
