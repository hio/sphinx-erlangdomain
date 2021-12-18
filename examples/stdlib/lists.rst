.. module:: lists

=====
lists
=====


Module
======

lists


Module Summary
==============

List processing functions.


Description
===========

This module contains functions for list processing.

Unless otherwise stated, all functions assume that position numbering
starts at 1. That is, the first element of a list is at position 1.

Two terms ``T1`` and ``T2`` compare equal if ``T1 == T2`` evaluates to
``true``. They match if ``T1 =:= T2`` evaluates to ``true``.

Whenever an **ordering function** ``F`` is expected as argument, it is
assumed that the following properties hold of ``F`` for all x, y, and z:

* If x ``F`` y and y ``F`` x, then x = y (``F`` is antisymmetric).
* If x ``F`` y and y ``F`` z, then x ``F`` z (``F`` is transitive).
* x ``F`` y or y ``F`` x (``F`` is total).

An example of a typical ordering function is less than or equal to:
``=</2``.


Exports
=======

.. function:: all(Pred, List) -> Boolean.

  :param Pred:  A predicate function.
  :type  Pred:  fun((Elem :: *T*) -> :type:`~erlang:boolean()`)
  :param List:  Target list.
  :type  List:  [*T*]
  :param T:  Element type.
  :type  T:  ~erlang:term()
  :rtype:  ~erlang:boolean()

  Returns ``true`` if ``Pred(Elem)`` returns ``true`` for all elements
  ``Elem`` in List, otherwise ``false``. The ``Pred`` function must return
  a boolean.


.. function:: any(Pred, List) -> Boolean.

  :param Pred:  A predicate function.
  :type  Pred:  fun((Elem :: *T*) -> :type:`~erlang:boolean()`)
  :param List:  Target list.
  :type  List:  [*T*]
  :param T:  Element type.
  :type  T:  ~erlang:term()
  :rtype:  ~erlang:boolean()

  Returns ``true`` if ``Pred(Elem)`` returns ``true`` for at least one
  element ``Elem`` in ``List``. The ``Pred`` function must return a
  boolean.


.. function:: append(ListOfLists) -> List1.

  :param ListOfLists:  List of lists.
  :type  ListOfLists:  [*List*]
  :param List:  List.
  :type  List:  [*T*]
  :param List1:  Result list.
  :type  List1:  [*T*]
  :param T:  Element type.
  :type  T:  ~erlang:term()
  :rtype:  [*T*]

  Returns a list in which all the sublists of ``ListOfLists`` have been
  appended.

  Example::

    > lists:append([[1, 2, 3], [a, b], [4, 5, 6]]).
    [1,2,3,a,b,4,5,6]


.. function:: append(List1, List2) -> List3.

  :param List1:  First list.
  :type  List1:  [*T*]
  :param List1:  Second list.
  :type  List1:  [*T*]
  :param List1:  Result list.
  :type  List1:  [*T*]
  :param T:  Element type.
  :type  T:  ~erlang:term()
  :rtype:  [*T*]

  Returns a new list ``List3``, which is made from the elements of
  ``List1`` followed by the elements of ``List2``.

  Example::

    > lists:append("abc", "def").
    "abcdef"

  ``lists:append(A, B)`` is equivalent to ``A ++ B``.
