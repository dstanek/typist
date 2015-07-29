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

import sys

from typist import _import_hook
from typist import _type_check


__version__ = '0.0.1'


def install(interesting_modules):
    # adding our decorator to the __builtins__ can that we can easily refer to
    # it later
    __builtins__['ensure_types'] = _type_check.ensure_types

    # sys.meta_path.append(_import_hook.Importer(package))
    sys.meta_path.insert(0, _import_hook.Finder(interesting_modules))
