#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""Special argparse module that allows to bypass abbrev mode."""

from __future__ import absolute_import
from argparse import *  # noqa
import sys


if sys.version_info < (3, 5):
    class ArgumentParser(ArgumentParser):  # noqa
        def __init__(self, *args, **kwargs):
            self.allow_abbrev = kwargs.pop("allow_abbrev", True)
            super(ArgumentParser, self).__init__(*args, **kwargs)

        def _get_option_tuples(self, option_string):
            if self.allow_abbrev:
                return super(ArgumentParser, self)._get_option_tuples(
                    option_string)
            return ()
