"""
Localization related code
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

import os
from . import api

class LanguageError(api.APIError):
    pass

class LanguageUnsupportedError(LanguageError):
    pass

class language(object):
    """ Steam API localization tools and reference """

    # If there's a new language added feel free to add it here
    _languages = {"da_DK": "Danish",
                  "nl_NL": "Dutch",
                  "en_US": "English",
                  "fi_FI": "Finnish",
                  "fr_FR": "French",
                  "de_DE": "German",
                  "hu_HU": "Hungarian",
                  "it_IT": "Italian",
                  "ja_JP": "Japanese",
                  "ko_KR": "Korean",
                  "no_NO": "Norwegian",
                  "pl_PL": "Polish",
                  "pt_PT": "Portuguese",
                  "pt_BR": "Brazilian Portuguese",
                  "ro_RO": "Romanian",
                  "ru_RU": "Russian",
                  "zh_CN": "Simplified Chinese",
                  "es_ES": "Spanish",
                  "sv_SE": "Swedish",
                  "zh_TW": "Traditional Chinese",
                  "tr_TR": "Turkish"}

    _default_language = "en_US"

    def __init__(self, code=None):
        """ Raises LanguageUnsupportedError if the code isn't supported by the
        API or otherwise invalid, uses the default language if no code is given.
        'code' is an ISO language code. """
        self._code = None

        if not code:
            _system_language = os.environ.get("LANG", language._default_language).split('.')[0]
            if _system_language in language._languages.keys():
                self._code = _system_language
            else:
                self._code = language._default_language
        else:
            code = code.lower()
            for lcode, lname in language._languages.items():
                code_lower = lcode.lower()
                if code_lower == code or code_lower.split('_')[0] == code:
                    self._code = lcode
                    break

        try:
            self._name = language._languages[self._code]
        except KeyError:
            self._name = None
            raise LanguageUnsupportedError(code)

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name
