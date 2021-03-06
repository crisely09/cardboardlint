# -*- coding: utf-8 -*-
# Cardboardlint is a cheap lint solution for pull requests.
# Copyright (C) 2011-2017 The Cardboardlint Development Team
#
# This file is part of Cardboardlint.
#
# Cardboardlint is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Cardboardlint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Linter using pylint.

This test calls the pylint program, see http://docs.pylint.org/index.html.
"""
from __future__ import print_function

import json

from cardboardlint.common import Message, run_command, Linter


__all__ = ['linter_pylint']


DEFAULT_CONFIG = {
    # Filename filter rules
    'filefilter': ['+ *.py', '+ scripts/*'],
    # Optional path to the config file.
    'config': None
}


def run_pylint(config, filenames):
    """Linter for checking pylint results.

    Parameters
    ----------
    config : dict
        Dictionary that contains the configuration for the linter
    filenames : list
        A list of filenames to check

    Returns
    -------
    messages : list
        The list of messages generated by the external linter.

    """
    # get Pylint version
    command = ['pylint', '--version']
    version_info = ''.join(run_command(command, verbose=False)[0].split('\n')[:2])
    print('USING              : {0}'.format(version_info))

    def has_failed(returncode, _stdout, _stderr):
        """Determine if pylint ran correctly."""
        return not 0 <= returncode < 32

    messages = []
    if len(filenames) > 0:
        command = ['pylint'] + filenames
        command += ['--jobs=2', '--output-format=json']
        if config['config'] is not None:
            command += ['--rcfile={0}'.format(config['config'])]
        output = run_command(command, has_failed=has_failed)[0]
        if len(output) > 0:
            for plmap in json.loads(output):
                charno = plmap['column']
                if charno in [0, -1]:
                    charno = None
                messages.append(Message(
                    plmap['path'], plmap['line'], charno,
                    '{0} {1}'.format(plmap['symbol'], plmap['message'])))
    return messages


# Pylint should be considered dynamic, which is in practice only true for projects with
# extension modules.
# pylint: disable=invalid-name
linter_pylint = Linter('pylint', run_pylint, DEFAULT_CONFIG, style='dynamic', language='python')
