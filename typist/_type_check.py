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

import functools
import inspect
import logging

from typist import _docstring


logger = logging.getLogger('typist')


def ensure_types(f):  # noqa
    params, returns = _docstring.parse(f)
    spec = inspect.getargspec(f)

    if not any([params, returns]):
        # nothing to check
        return f

    @functools.wraps(f)
    def decorate(*args, **kwargs):
        # validate arguments
        args_to_validate = dict(zip(spec.args, args))
        args_to_validate.update(kwargs)
        for name, value in args_to_validate.items():
            ptype = params.get(name)
            if ptype is None:
                logger.warning('wft? your docs are wrong!')
                continue
            if not ptype.validate(value):
                msg = ('expected %r for %r in %r; found %r'
                       % (ptype.types, name, f.__name__, type(value)))
                raise AssertionError(msg)

        try:
            retval = f(*args, **kwargs)
        except Exception:
            # TODO: validate exceptions
            raise

        # validate return values
        logger.debug('checking returns; actual=%r; against=%r',
                     retval, returns)
        if returns and not isinstance(retval, returns):
            msg = '%r returned %r; %r was expected'
            raise AssertionError(msg % (f.__name__, type(retval), returns))
        return retval

    return decorate
