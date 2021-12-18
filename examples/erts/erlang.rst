.. module:: erlang

======
erlang
======

Module
======

erlang


Module Summary
==============

The Erlang BIFs and predefined types.


Description
===========

By convention, most Built-In Functions (BIFs) and all predefined types are
included in this module. Some of the BIFs and all of the predefined types
are viewed more or less as part of the Erlang programming language and are
**auto-imported**. Thus, it is not necessary to specify the module name.
For example, the calls ``atom_to_list(erlang)`` and
``erlang:atom_to_list(erlang)`` are identical.

Auto-imported BIFs are listed without module prefix. BIFs listed with
module prefix are not auto-imported.

Predefined types are listed in the `Predefined datatypes`_ section of this
reference manual and in the `Types and Function Specifications`_ section of
the Erlang Reference Manual.

.. _`Types and Function Specifications`:
  https://www.erlang.org/doc/reference_manual/typespec.html

BIFs can fail for various reasons. All BIFs fail with reason badarg if they are called with arguments of an incorrect type. The other reasons are described in the description of each individual BIF.

Some BIFs can be used in guard tests and are marked with "Allowed in guard tests".


Data Types
==========

Predefined datatypes
--------------------

.. type:: any()
  :auto_importable:

  All possible Erlang terms. Synonym for :type:`term()`.


.. type:: arity()
  :auto_importable:

  The arity of a function or type.


.. type:: atom()
  :auto_importable:

  An Erlang atom.


.. type:: binary()
  :auto_importable:

  An Erlang binary, that is, a bitstring with a size divisible by 8.

  ::

    binary() = <<_:_*8>>


.. type:: bitstring()
  :auto_importable:

  An Erlang bitstring.

  ::

    bitstring() = <<_:_*1>>


.. type:: boolean()
  :auto_importable:

  A boolean value.

  ::

    boolean() = true | false


.. type:: byte()
  :auto_importable:

  A byte of data represented by an integer.

  ::

    byte() = 0..255


.. type:: char()
  :auto_importable:

  An ASCII character or a unicode codepoint presented by an integer.

  ::

    char() = 0..1114111


.. type:: float()
  :auto_importable:

  An Erlang float.

  ::

    float() = float()


.. type:: function()
  :auto_importable:

  An Erlang fun.

  ::

    function() = function()


.. type:: identifier()
  :auto_importable:

  An unique identifier for some entity, for example a process, port or monitor.

  ::

    identifier() = pid() | port() | reference()


.. type:: integer()
  :auto_importable:

  An Erlang integer.


.. type:: iodata()
  :auto_importable:

  ::

    iodata() = iolist() | binary()

  A binary or list containing bytes and/or iodata.

  This datatype is used to represent data that is meant to be output using
  any I/O module. For example: :func:`file:write/2` or :func:`gen_tcp:send/2`.

  To convert an :type:`iodata()` term to :type:`binary()` you can use
  :func:`iolist_to_binary/1`. To transcode a :type:`string()` or
  :type:`unicode:chardata()` to :type:`iodata()` you can use
  :func:`unicode:characters_to_binary/1`.


.. type:: iolist()
  :auto_importable:

  A list containing bytes and/or iodata.

  ::

    iolist() =
        maybe_improper_list(byte() | binary() | iolist(),
                            binary() | [])

  This datatype is used to represent data that is meant to be output using
  any I/O module. For example: :func:`file:write/2` or
  :func:`gen_tcp:send/2`.

  In most use cases you want to use :type:`iodata()` instead of this type.


.. type:: list()
  :auto_importable:

  An Erlang list containing terms of any type.


.. type:: list(ContentType)
  :auto_importable:

  An Erlang list containing terms of the type *ContentType*.

  ::

    list(ContentType) = [ContentType]


.. type:: map()
  :auto_importable:

  An Erlang map containing any number of key and value associations.

  ::

    map() = #{any() => any()}


.. type:: maybe_improper_list()
  :auto_importable:

  An Erlang list that is not guaranteed to end with a :type:`[] <nil()>`,
  and where the list elements can be of any type.

  ::

    maybe_improper_list() = maybe_improper_list(any(), any())


.. type:: maybe_improper_list(ContentType, TerminationType)
  :auto_importable:

  An Erlang list, that is not guaranteed to end with a :type:`[] <nil()>`,
  and where the list elements are of the type *ContentType*.

  ::

    maybe_improper_list(ContentType, TerminationType) =
        maybe_improper_list(ContentType, TerminationType)


.. type:: mfa()
  :auto_importable:

  A three-tuple representing a ``Module:Function/Arity`` function signature.

  ::

    mfa() = {module(), atom(), arity()}


.. type:: module()
  :auto_importable:

  An Erlang module represented by an atom.

  ::

    module() = atom()


.. type:: neg_integer()
  :auto_importable:

  A negative integer.

  ::

    neg_integer() = integer() =< -1


.. type:: nil()
  :auto_importable:

  The empty :type:`list()`.

  ::

    nil() = []


.. type:: no_return()
  :auto_importable:

  The type used to show that a function will **never** return a value, that
  is it will **always** throw an exception.

  ::

    no_return() = none()


.. type:: node()
  :auto_importable:

  An Erlang `node`_ represented by an atom.

  ::

    node() = atom()

  .. _`node`:
    https://www.erlang.org/doc/reference_manual/distributed.html#nodes


.. type:: non_neg_integer()
  :auto_importable:

  A non-negative integer, that is any positive integer or 0.

  ::

    non_neg_integer() = integer() >= 0


.. type:: none()
  :auto_importable:

  This type is used to show that a function will **never** return a value;
  that is it will **always** throw an exception.

  ::

    none() = none()

  In a spec, use :type:`no_return()` for the sake of clarity.


.. type:: nonempty_binary()
  :auto_importable:

  A :type:`binary()` that contains some data.

  ::

    nonempty_binary() = <<_:8, _:_*8>>


.. type:: nonempty_bitstring()
  :auto_importable:

  A :type:`bitstring()` that contains some data.

  ::

    nonempty_bitstring() = <<_:1, _:_*1>>


.. type:: nonempty_improper_list(ContentType, TerminationType)
  :auto_importable:

  A :type:`maybe_improper_list/2` that contains some items.

  ::

    nonempty_improper_list(ContentType, TerminationType) =
        nonempty_improper_list(ContentType, TerminationType)


.. type:: nonempty_list()
  :auto_importable:

  A :type:`list()` that contains some items.

  ::

    nonempty_list() = [any(), ...]


.. type:: nonempty_list(ContentType)
  :auto_importable:

  A :type:`list(ContentType)` that contains some items.

  ::

    nonempty_list(ContentType) = [ContentType, ...]


.. type:: nonempty_maybe_improper_list()
  :auto_importable:

  A :type:`maybe_improper_list()` that contains some items.

  ::

    nonempty_maybe_improper_list() =
        nonempty_maybe_improper_list(any(), any())


.. type:: nonempty_maybe_improper_list(ContentType, TerminationType)
  :auto_importable:

  A :type:`maybe_improper_list(ContentType, TerminationType)` that contains
  some items.

  ::

    nonempty_maybe_improper_list(ContentType, TerminationType) =
        nonempty_maybe_improper_list(ContentType, TerminationType)


.. type:: nonempty_string()
  :auto_importable:

  A :type:`string()` that contains some characters.

  ::

    nonempty_string() = [char(), ...]


.. type:: number()
  :auto_importable:

  An Erlang number.

  ::

    number() = integer() | float()


.. type:: pid()
  :auto_importable:

  An Erlang process identifier.


.. type:: port()
  :auto_importable:

  An Erlang port identifier.


.. type:: pos_integer()
  :auto_importable:

  An integer greater than zero.

  ::

    pos_integer() = integer() >= 1


.. type:: reference()
  :auto_importable:

  An Erlang reference.


.. type:: string()
  :auto_importable:

  A character string represented by a list of ASCII characters or unicode
  codepoints.

  ::

    string() = [char()]

.. type:: term()
  :auto_importable:

  All possible Erlang terms. Synonym for :type:`any()`.

  ::

    term() = any()


.. type:: timeout()
  :auto_importable:

  A timeout value that can be passed to a receive expression.

  ::

    timeout() = infinity | integer() >= 0


.. type:: tuple()
  :auto_importable:

  An Erlang tuple.

  ::

    tuple() = tuple()


Other Datatypes
---------------


Exports
=======

.. function:: abs(Float) [@float] -> float().
  abs(Int) [@int] -> integer() >= 0.
  :auto_importable:

  Returns an integer or float that is the arithmetical absolute value of
  *Float* or *Int*.

  :param Int:  A value.
  :type  Int:  integer()
  :rtype:  :type:`float()` | :type:`integer()`
  :raises badarg: The argument is not a number.

  For example::

    > abs(-3.33).
    3.33
    > abs(-3).
    3

  Allowed in guard tests.


.. function:: iolist_to_binary(IoListOrBinary) -> binary().
  :auto_importable:

  Returns a binary that is made from the integers and binaries in
  *IoListOrBinary*.

  :param IoListOrBinary:  Data.
  :type  IoListOrBinary:  :type:`iolist()` | :type:`binary()`
  :rtype:  binary()

  For example::

    > Bin1 = <<1,2,3>>.
    <<1,2,3>>
    > Bin2 = <<4,5>>.
    <<4,5>>
    > Bin3 = <<6>>.
    <<6>>
    > iolist_to_binary([Bin1,1,[2,3,Bin2],4|Bin3]).
    <<1,2,3,1,2,3,4,5,4,6>>
