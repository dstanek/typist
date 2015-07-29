# Copyright 2015 David Stanek <dstanek@dstanek.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""The import hooks that rig up the magic!

For more information on import hooks, please see:
    https://www.python.org/dev/peps/pep-0302/
"""

import imp
import logging
import os
import sys

from typist import _transformer


logger = logging.getLogger('typist')


class Finder(object):

    def __init__(self, interesting_packages):
        self._interesting_packages = interesting_packages

    def find_module(self, fullname, path=None):
        logger.debug('Finding fullname=%r path=%r', fullname, path)
        print('Finding fullname=%r path=%r', fullname, path)
        name_parts = fullname.split('.')
        if name_parts and name_parts[0] in self._interesting_packages:
            module_name = fullname.rsplit('.', 1)[-1]
            fp, pathname, description = imp.find_module(
                module_name, path or ['.'])
            logger.debug('Returning loader')
            return Loader(path)
        else:
            logger.debug('%r not found', fullname)
            return None


class Loader(object):

    def __init__(self, import_path):
        self._import_path = import_path or ['.']

    def load_module(self, fullname):
        logger.debug('Loading %s', fullname)

        if fullname in sys.modules:
            logger.debug('Returning cached module for %r', fullname)
            return sys.modules[fullname]

        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        mod.__name__ = fullname
        mod.__file__ = fullname

        module_name = fullname.rsplit('.', 1)[-1]
        fp, pathname, description = imp.find_module(
            module_name, self._import_path)
        if os.path.isdir(pathname):  # package
            pathname = os.path.join(pathname, '__init__.py')
            mod.__path__ = [os.path.dirname(pathname)]
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]

        if not fp:
            fp = open(pathname)

        code = fp.read()
        tree = _transformer.transform(code)

        fp.close()

        print(tree, self._import_path)
        exec(compile(tree, pathname, 'exec'), mod.__dict__)

        logger.debug('Module for %r created', fullname)
        return mod
