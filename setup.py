"""
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

from distutils.core import setup
import steam

setup(name = "steamodd",
      version = steam.__version__,
      description = "High level Steam API implementation with low level reusable core",
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
      license = steam.__license__)
