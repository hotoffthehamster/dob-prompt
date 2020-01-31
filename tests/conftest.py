# This file exists within 'dob-prompt':
#
#   https://github.com/hotoffthehamster/dob-prompt
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

"""
Fixtures available to the tests/.

- In general, fixtures should return a single instance.

- If a fixture is a factory, its name should reflect that.

- A fixture that is parametrized should be suffixed with
  ``_parametrized`` to imply it has increased complexity.
"""

import os
import pytest

# FIXME/2020-01-31: Move shared dob/tests/conftest.py code to dob/dob/tests/
#   and then get rid of ConfigObj dependency here, and the non-DRY code below.
from configobj import ConfigObj

from pytest_factoryboy import register

from nark.config import decorate_config

# import dob_prompt.dob_prompt as dob_prompt

from dob.config.fileboss import default_config_path
from dob.controller import Controller

from nark.tests import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


@pytest.fixture
def config_root(nark_config, dob_config):
    """Provide a generic baseline configuration."""
    config_root = decorate_config(nark_config)
    config_root.update(dob_config)
    config = config_root.as_dict()
    return config


# This method essentially same as: nark:tests/conftest.py::base_config.
@pytest.fixture
def nark_config(tmpdir):
    """
    Provide a backend config fixture. This can be passed to a controller directly.

    That means this fixture represents the the result of all typechecks and
    type conversions.
    """
    # FETREQ/2020-01-09: (lb): Support dot-notation in dict keys on `update`.
    # - For now, create deep dictionary; not flat with dotted key names.
    return {
        'db': {
            'orm': 'sqlalchemy',
            'engine': 'sqlite',
            'path': ':memory:',
            # MAYBE/2019-02-20: (lb): Support for alt. DBMS is wired, but not tested.
            #   'host': '',
            #   'port': '',
            #   'name': '',
            #   'user': '',
            #   'password': '',
        },
        'dev': {
            'lib_log_level': 'WARNING',
            'sql_log_level': 'WARNING',
        },
        'time': {
            # 2019-02-20: (lb): Note that allow_momentaneous=False probably Bad Idea,
            #                   especially for user upgrading from legacy hamster db.
            'allow_momentaneous': True,

            # MAYBE/2019-02-20: (lb): I don't day_start, so probably broke; needs tests.
            #   'day_start': datetime.time(hour=0, minute=0, second=0).isoformat(),
            #   'day_start': datetime.time(hour=5, minute=0, second=0).isoformat(),
            'day_start': '',

            # MAYBE/2019-02-20: (lb): Perhaps test min-delta, another feature I !use!
            #   'fact_min_delta': '60',
            'fact_min_delta': '0',

            # FIXME/2019-02-20: (lb): Implement tzawareness/tz_aware/timezone sanity.
            'tz_aware': False,

            # FIXME/2019-02-20: (lb): Needs testing, e.g.,
            #   'default_tzinfo': 'America/Menominee',
            'default_tzinfo': '',
        },
    }


@pytest.fixture
def dob_config(tmpdir):
    """
    Provide a client config fixture. This can be passed to a controller directly.

    That means this fixture represents the the result of all typechecks and
    type conversions.
    """
    return {
        # FIXME/2019-02-20: (lb): Test with missing config values; I know, bugs!

        # FIXME/2019-02-20: (lb): Clarify: Use bool, or string? True, or 'True'?
        # 'editor.centered': '',
        'editor.centered': 'True',

        'editor.lexer': '',

        # Devmode catch_errors could be deadly under test, as it sets a trace trap.
        'dev.catch_errors': False,

        'term.editor_suffix': '',

        # The default export path is '', i.e., local directory. Use /tmp instead.
        # 'term.export_path': '',  # Default.
        'term.export_path': os.path.join(tmpdir.mkdir('export').strpath, 'export'),

        # Disable color, otherwise tests will have to look for color codes.
        'log.use_color': False,

        # Don't log to console, otherwise tests have to deal with that noise.
        # 'log_console': True,  # Default.
        'log.use_console': False,

        # The default log filename does not need to be changed.
        # 'log_filename': 'dob.log',  # Default.
        # See also:
        #  'logfile_path': '',  # Generated value.

        # 'dev.cli_log_level': 'WARNING',  # Default.
        # 2019-02-20 11:15: I need to see where py.test of Carousel is hanging!
        'dev.cli_log_level': 'DEBUG',

        'fact.separators': '',  # [,:\n]

        'term.show_greeting': False,

        'editor.styling': '',

        'term.use_color': False,
        'term.use_pager': False,
    }


@pytest.fixture
def config_instance(tmpdir, faker):
    """Provide a (dynamicly generated) ConfigObj instance."""

    def generate_config(**kwargs):
        cfg_dict = generate_dict(**kwargs)
        # configfile_path = os.path.join(tmpdir, 'dob.conf')
        configfile_path = default_config_path()
        config = ConfigObj(configfile_path)
        config.merge(cfg_dict)
        return config

    def generate_dict(**kwargs):
        cfg_dict = {}

        # ***

        cfg_db = {}
        cfg_dict['db'] = cfg_db

        cfg_db.setdefault('orm', kwargs.get('orm', 'sqlalchemy'))
        cfg_db.setdefault('engine', kwargs.get('engine', 'sqlite'))
        # HARDCODED: This filename value does not matter, really.
        db_path = os.path.join(tmpdir.strpath, 'dob.sqlite')
        cfg_db.setdefault('path', kwargs.get('path', db_path))
        cfg_db.setdefault('host', kwargs.get('host', ''))
        cfg_db.setdefault('port', kwargs.get('port', ''))
        cfg_db.setdefault('name', kwargs.get('name', ''))
        cfg_db.setdefault('user', kwargs.get('user', '')),
        cfg_db.setdefault('password', kwargs.get('password', ''))

        # ***

        cfg_dev = {}
        cfg_dict['dev'] = cfg_dev

        lib_log_level = kwargs.get('lib_log_level', 'WARNING')
        cfg_dev.setdefault('lib_log_level', lib_log_level)
        sql_log_level = kwargs.get('sql_log_level', 'WARNING')
        cfg_dev.setdefault('sql_log_level', sql_log_level)

        # ***

        cfg_time = {}
        cfg_dict['time'] = cfg_time

        # (lb): Need to always support momentaneous, because legacy data bugs.
        # cfg_time.setdefault('allow_momentaneous', 'False')
        cfg_time.setdefault('allow_momentaneous', 'True')

        # day_start = kwargs.get('day_start', '')
        day_start = kwargs.get('day_start', '00:00:00')
        cfg_time.setdefault('day_start', day_start)

        # fact_min_delta = kwargs.get('fact_min_delta', '0')
        fact_min_delta = kwargs.get('fact_min_delta', '60')
        cfg_time.setdefault('fact_min_delta', fact_min_delta)

        cfg_time.setdefault('tz_aware', kwargs.get('tz_aware', 'False'))
        # FIXME/2019-02-20: (lb): Fix timezones. And parameterize, e.g.,
        #  default_tzinfo = kwargs.get('default_tzinfo', 'America/Menominee')
        default_tzinfo = kwargs.get('default_tzinfo', '')
        cfg_time.setdefault('default_tzinfo', default_tzinfo)

        # ***

        cfg_editor = {}
        cfg_dict['editor'] = cfg_editor

        cfg_editor.setdefault('centered', False)
        cfg_editor.setdefault('lexer', '')
        cfg_editor.setdefault('styling', '')

        # ***

        cfg_fact = {}
        cfg_dict['fact'] = cfg_fact

        cfg_fact.setdefault('separators', '')  # [,:\n]

        # ***

        assert('dev' in cfg_dict)

        cli_log_level = kwargs.get('cli_log_level', 'warning')
        cfg_dev.setdefault('cli_log_level', cli_log_level)
        cfg_dev.setdefault('catch_errors', 'False')

        # ***

        cfg_log = {}
        cfg_dict['log'] = cfg_log

        cfg_log.setdefault('filename', kwargs.get('log_filename', faker.file_name()))
        # The log_filename is used to make log.filepath, which we don't need to set.
        cfg_log.setdefault('use_color', 'False')
        cfg_log.setdefault('use_console', kwargs.get('log_console', 'False'))

        # ***

        cfg_term = {}
        cfg_dict['term'] = cfg_term

        cfg_term.setdefault('export_path', '')
        cfg_term.setdefault('editor_suffix', '')
        cfg_term.setdefault('show_greeting', 'False')
        cfg_term.setdefault('use_color', 'True')
        cfg_term.setdefault('use_pager', 'False')

        # ***

        return cfg_dict

    return generate_config


def prepare_controller(config_root):
    controller = Controller()
    controller.wire_configience(config_root=config_root)
    return controller


@pytest.yield_fixture
def controller(config_root, mocker):
    """Provide a pseudo controller instance."""
    controller = prepare_controller(config_root=config_root)
    controller.ctx = mocker.MagicMock()
    controller.configurable = mocker.MagicMock()
    controller.standup_store()
    yield controller
    controller.store.cleanup()


@pytest.yield_fixture
def controller_with_logging(config_root, mocker):
    """Provide a pseudo controller instance with logging setup."""
    controller = prepare_controller(config_root=config_root)
    controller.ctx = mocker.MagicMock()
    controller.configurable = mocker.MagicMock()
    controller.setup_logging()
    controller.standup_store()
    yield controller
    controller.store.cleanup()

