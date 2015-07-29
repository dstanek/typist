typist - Test time type checking
================================

.. image:: https://secure.travis-ci.org/dstanek/typist.png

**typist** is a test time tool that uses your Sphinx docstrings (you do document
your code right?) to ensure that your callables:

- are only called with the types they expect
- only return types they advertise
- only raise exceptions they advertise

Usage
-----

Right now you have to import typist and install it. The argument to install is
the top level package for the code you are interested in testing. In the
future I plan on creating plugins for test frameworks.

  .. code:: python

    import typist
    typist.install('keystone')

typist implements an `import hook`_ that will use Python's `AST`_ to add a
decorator to all of your callables. The decorator ensures the callable is
properly used based on its docstring type declarations. If your callable
doesn't have :param:, :returns or :raises: then it works just fine, it's
just not checked.

Type language                                                                                                      
-------------

Types will be pulled from the following formats:

  :param {type} varname: some descriptive text
  :rtype avarname: {types}
  :returns {types}: some descriptive text

`{type}` can be any valid Python type. Some examples:

- `int`
- `list`
- `:py:class:typist._import_hook.Finder`
- `typist._import_hook.Finder`

`{types}` can be a list of types separated by commas that includes an optional
'or'. All the same types as above can be used in the list. Some examples:

- `list` or None
- `int`, `float` or `long`
- `int`, `float`, `long`
- `typist._py.PY2` or `typist._py.PY3`
- `list` or `callable`

`callable` above is a special case. While technically it's not a type it does
describe the way an object should behave. Another special cases that doesn't
work yet, but may soon is `iterable`.

This languasge for specifying a type will grow a bit more rich for collections.
It would be really handy to allow the developer to specify parameterized types
like:

- `list<int>` - a `list` of `int`
- `dict<str,package.module.Class>` - a `dict` where the keys are strings and
  the values are instances of package.module.Class

Background
----------

The idea to write to this came to me when I was working on Python 3 support
for `Keystone`_. I wanted to ensure that the code was actually getting the
binary or text types that it expected. I was sick of the bullshit practice of
`.encode('utf8').decode('utf8')` (maybe I got that backwards) that made the
exceptions go away, but does nothing to solve the problem.

I didn't bother looking for something that was already implemented because I
wanted to learn a bit about import hooks. If you know of something better then
please let me know. If this is the best thing since sliced bread I'd also like
to know.

.. _Keystone: http://docs.openstack.org/developer/keystone/
.. _import hook: https://www.python.org/dev/peps/pep-0302/
.. _AST: https://docs.python.org/2/library/ast.html
