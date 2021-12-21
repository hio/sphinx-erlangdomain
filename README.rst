=============
Erlang Domain
=============

:author: SHIBUKAWA Yoshiki <yoshiki at shibu.jp>

About
=====

This is the Erlang domain for Sphinx.
Since version 1.0, Sphinx delivers a new feature -- Domain.
It will enable other language support except Python and C language.

This extension provides directives and roles to write Erlang documents.

The Erlang domain (name **erl**) supports following objects:

* Modules (:rst:dir:`erl:module`, :rst:role:`erl:mod`)
* Functions (:rst:dir:`erl:function`, :rst:role:`erl:func`)
* Types and opaque types (:rst:dir:`erl:type`, :rst:dir:`erl:opaque`, :rst:role:`erl:type`)
* Records (:rst:dir:`erl:record`, :rst:role:`erl:record`)
* Macros (:rst:dir:`erl:macro`, :rst:role:`erl:macro`)
* Callbacks (:rst:dir:`erl:callback`, :rst:role:`erl:callback`)

URLs
====

:PyPI: http://pypi.python.org/pypi/sphinxcontrib-erlangdomain
:Detail Document: http://packages.python.org/sphinxcontrib-erlangdomain

Quick Sample
============

This is source:

  .. code-block:: rst

    .. erl:module:: lists

    .. erl:function:: append(ListOfLists) -> List1

       :type ListOfLists:  [[*term()*]]
       :rtype:  [*term()*]

       Returns a list in which all the sub-lists of ListOfLists
       have been appended. For example:

       .. code-block:: erlang

          > lists:append([[1, 2, 3], [a, b], [4, 5, 6]]).
          [1,2,3,a,b,4,5,6]

    .. erl:function:: append(List1, List2) -> List3

       :param List1:  First Item.
       :type  List1:  [*term()*]
       :param List2:  Second Item.
       :type  List2:  [*term()*]
       :rtype:  [*term()*]

       Returns a new list List3 which is made from the elements
       of List1 followed by the elements of List2. For example:

       .. code-block:: erlang

          > lists:append("abc", "def").
          "abcdef"

       ``lists:append(A, B)`` is equivalent to ``A ++ B``.

Results:

    .. erl:module:: lists

    .. erl:function:: append(ListOfLists) -> List1

       :type ListOfLists:  [[*term()*]]
       :rtype:  [*term()*]

       Returns a list in which all the sub-lists of ListOfLists
       have been appended. For example:

       .. code-block:: erlang

          > lists:append([[1, 2, 3], [a, b], [4, 5, 6]]).
          [1,2,3,a,b,4,5,6]

    .. erl:function:: append(List1, List2) -> List3

       :param List1:  First Item.
       :type  List1:  [*term()*]
       :param List2:  Second Item.
       :type  List2:  [*term()*]
       :rtype:  [*term()*]

       Returns a new list List3 which is made from the elements
       of List1 followed by the elements of List2. For example:

       .. code-block:: erlang

          > lists:append("abc", "def").
          "abcdef"

       ``lists:append(A, B)`` is equivalent to ``A ++ B``.

.. note::
   This content is copied from http://www.erlang.org/doc/man/lists.html

------------------

From other place, you can create cross reference like that:

  .. code-block:: rst

    Looking at how :erl:func:`lists:append/1`
    or ``++`` would be implemented in plain Erlang,
    it can be seen clearly that the first list is copied.

Results:

    Looking at how :erl:func:`lists:append/1`
    or ``++`` would be implemented in plain Erlang,
    it can be seen clearly that the first list is copied.

.. note::
   This content is copied from http://erlang.org/doc/efficiency_guide/listHandling.html

-----------

Install
=======

.. code-block:: bash

   $ pip3 install -U sphinxcontrib-erlangdomain
