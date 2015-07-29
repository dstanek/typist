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

import inspect
import logging
import sys

import docutils.nodes
import docutils.parsers.rst
import docutils.utils

from typist import _py


logger = logging.getLogger('typist')


# TODO: maybe Sphinx can do this better?


class ParamType(object):

    def __init__(self):
        self.types = []
        self.callable = False

    def validate(self, argument):
        if not self.types:
            return True

        if isinstance(argument, tuple(self.types)):
            return True

        if self.callable and callable(argument):
            return True

        return False

    @classmethod
    def from_list(cls, obj, type_list):
        ptype = cls()
        for part in type_list:
            if part == 'or':
                continue

            part = part.rstrip(',')

            if part == 'callable':
                ptype.callable = True

            _type = _resolve_type(part)
            if _type:
                ptype.types.append(_type)
            else:
                # TODO: maybe a log message here?
                logger.error('could not resolve type declaration for %r' % obj)
                pass
        return ptype


class _FieldVisitor(docutils.nodes.SparseNodeVisitor):

    def __init__(self, document):
        self.parts = []
        docutils.nodes.NodeVisitor.__init__(self, document)

    def visit_Text(self, node):
        self.parts.extend(node.strip().split(' '))


class _DocStringVisitor(docutils.nodes.SparseNodeVisitor):
    # Others are possible, but in Keystone we only use 'param'. For more
    # info see: http://sphinx-doc.org/domains.html#info-field-lists
    PARAM_FIELD_TAGS = set(['param'])
    TYPE_FIELD_TAGS = set(['type'])
    RTYPE_FIELD_TAGS = set(['rtype'])

    UNKNOWN = object()

    def __init__(self, document, obj):
        self.obj = obj
        self.params = {}
        self.returns = []
        docutils.nodes.NodeVisitor.__init__(self, document)

    def visit_field(self, node):
        name_node, value_node = node.children

        tag = name_node.children[0].astext().split()[0]
        if tag in self.PARAM_FIELD_TAGS:
            self._process_params(name_node)
        elif tag in self.TYPE_FIELD_TAGS:
            try:
                self._process_param_type(name_node, value_node)
            except Exception as e:
                logger.warning('failed parsing :type: for %r: %r', self.obj, e)
                raise
        elif tag in self.RTYPE_FIELD_TAGS:
            self._process_return_type(value_node)

        raise docutils.nodes.SkipChildren

    def _multi_values(self, parts):
        for part in parts:
            if part == 'or':
                continue
            part = part.rstrip(',')
            _type = _resolve_type(part)
            if _type:
                yield _type
            else:
                # TODO: maybe a log message here?
                pass

    def _process_params(self, name_node):
        visitor = _FieldVisitor(self.document)
        name_node.walk(visitor)
        try:
            tag, _type, name = visitor.parts
            self.params[name] = ParamType.from_list(self.obj, visitor.parts)
        except ValueError:
            # TODO: maybe a warning here? or UNKNOWN?
            pass  # hopefully this is defined with a 'type' later
            # raise

    def _process_param_type(self, name_node, value_node):
        visitor = _FieldVisitor(self.document)
        name_node.walk(visitor)
        tag, name = visitor.parts

        visitor = _FieldVisitor(self.document)
        value_node.walk(visitor)
        self.params[name] = ParamType.from_list(self.obj, visitor.parts)

    def _process_return_type(self, value_node):
        visitor = _FieldVisitor(self.document)
        value_node.walk(visitor)
        self.returns = tuple(self._multi_values(visitor.parts))


def parse(obj):
    docstring = inspect.getdoc(obj)
    if docstring is None:
        return {}, ()

    parser = docutils.parsers.rst.Parser()
    settings = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)).get_default_values()
    document = docutils.utils.new_document('', settings)

    visitor = _DocStringVisitor(document, obj)
    parser.parse(docstring, document)
    document.walk(visitor)
    return visitor.params, tuple(visitor.returns)


def _resolve_type(_type):  # noqa
    if isinstance(_type, type):
        return _type

    if _type == 'None':
        return type(None)

    if _type == 'string':
        _type = 'str'

    if _py.PY2 and _type == 'str':
        return unicode

    if _type in __builtins__:
        return __builtins__[_type]

    try:
        type_ = eval(_type)
        if isinstance(type_, type):
            return type_
    except:
        pass

    try:
        module = __import__(_type)
    except ImportError:
        if '.' not in _type:
            # TODO: maybe an error here?
            return
    else:
        return sys.modules[_type]

    module_name, object_name = _type.rsplit('.', 1)
    module = _resolve_type(module_name)
    try:
        attr = getattr(module, object_name)
    except AttributeError:
        # TODO: the docstring is likely incorrect
        return None

    if isinstance(attr, type):
        return attr

    return None
