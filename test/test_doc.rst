===============
Acceptance Test
===============

If all links are valid, test is done successfully.

Global Target
=============

Here is erlang module's contents because no explicit :rst:dir:`erl:function`.

.. erl:function:: function_out_of_module

.. erl:type:: string()

.. erl:type:: atom()

.. //---
.. erl:module:: test_module

Single Module 'test_module'
===========================

Here are link targets for module :erl:mod:`test_module`.

.. erl:function:: module_function(Identifier) -> Status.

   test
   
   :param Identifier: Identify sender.
   :type  Identifier: ~erlang:string()
   :return: Some status.
   :rtype:  :erl:type:`~erlang:atom()`

.. erl:function:: variable_function(Name[, Optition]) -> ok.

   test

   :param Name: Identify sender.
   :type  Name: ~erlang:string()
   :param Option: Option param.
   :type  Option: ~erlang:atom()
   :rtype:  ok


.. erl:macro:: ?HostName
   
   Host name of test server.

.. erl:record:: #user_address

   It contains user name, e-mail, address and so on

Test Case 1 -- Access Without Module Name in Same Module
--------------------------------------------------------

* Test 1-1 -- ``erl:mod``, :erl:mod:`test_module`
* Test 1-2 -- ``erl:func``, :erl:func:`module_function/1`
* Test 1-3 -- ``erl:func``, :erl:func:`variable_function/1`
* Test 1-4 -- ``erl:func``, :erl:func:`variable_function/2`
* Test 1-5 -- ``erl:macro``, :erl:macro:`?HostName`
* Test 1-6 -- ``erl:record``, :erl:record:`#user_address`

Test Case 2 -- Access to Default Module Name
--------------------------------------------

* Test 2-1 -- ``erl:func``, :erl:func:`erlang:function_out_of_module/0`

.. //---
.. erl:module:: dummy_other_module

Test Case 3 -- Access With Module Name in Other Module
------------------------------------------------------

Here is the content of :erl:mod:`dummy_other_module` module.

* Test 3-1 -- ``erl:mod``, :erl:mod:`test_module`
* Test 3-2 -- ``erl:func``, :erl:func:`test_module:module_function`
* Test 3-3 -- ``erl:func``, :erl:func:`test_module:module_function/1`
* Test 3-4 -- ``erl:func``, :erl:func:`test_module:variable_function/1`
* Test 3-5 -- ``erl:func``, :erl:func:`test_module:variable_function/2`
* Test 3-6 -- ``erl:func``, :erl:func:`test_module:variable_function`
* Test 3-7 -- ``erl:macro``, :erl:macro:`test_module:?HostName`
* Test 3-8 -- ``erl:record``, :erl:record:`test_module:#user_address`
