.. highlight:: rst

Reference
=========

Directives
----------

The Erlang domain provides the following directives.

.. rst:directive:: .. erl:module:: module_name

   This directive marks the beginning of the description of a module.

   This directive will also cause an entry in the global module index.

   It has ``:platform:``, ``:synopsis:``, ``:deprecated:`` and ``:noindex``
   options as same as :rst:dir:`py:module`.

   ``:platform: LIST``
     Comma separated list of the platforms
   ``:synopsis: TEXT``
     One sentence description for the module's purose.
   ``:deprecated:``
     Mark a module as deprecated.
   ``:noindex:``
     Prevent being shown in the general index.

   .. seealso::

     * :rst:dir:`py:module`
     * :ref:`sphinx:basic-domain-markup` (``:noindex:`` option)


.. rst:directive:: .. erl:currentmodule:: module_name

   Switch to the module without creating new module definition.

   .. seealso::

     * :rst:dir:`py:currentmodule`

The following directives are provided for module level contents:

.. rst:directive:: .. erl:function:: func_name(Arg1, Arg2, ...) -> Result

   Describes a module-level function. Usage of this directive is almost as same as Python's one.

   Erlang domain can accept functions whose names are same.
   To identify these, Erlang have arity information.

   Additionary, Erlang domain also accepts `flavor name`_ experimentally.

   A function signature consists of followings:

   * Module name followed by colon. (optional)
   * Function name. (mandatory)
   * Argument list (``(Arg1, Arg2, ...)``) or arity (``/arity``). (optional, but should write)
   * `Flavor name`_. (optional, experimental)
   * ``when`` description. (optional)
   * Return annoration (``-> Result``). (optional)

   Example::

      .. erl:module:: io

      .. erl:function:: nl() -> ok

         Output newline.

      .. erl:function:: put_chars(Chars) -> ok

         Output characters without formatting.

         :param Chars:  characters to be output.
         :type  Chars:  unicode:chardata()
         :rtype:  ``ok``

      .. erl:function:: format(Fmt[, Args]) -> ok

         Output message with formatting, like ``printf`` in C.

         :param Fmt:   format string.
         :type  Fmt:   io:format()
         :param Args:  characters to be output.
         :type  Args:  [:erl:type:`term()`]
         :rtype:  ``ok``

      .. erl:function:: format(Device, Fmt, Args) -> ok

         Output message into ``Device`` with formatting, like ``fprintf`` in C.

         :param Device:  output target.
         :type  Device:  io:device()
         :param Fmt:     format string.
         :type  Fmt:     io:format()
         :param Args:    characters to be output.
         :type  Args:    [:erl:type:`term()`]
         :rtype: ``ok``

   These functions can be referenced by :rst:role:`erl:func`, for example::

      * :erl:func:`io:nl/0`, :erl:func:`io:nl()`
      * :erl:func:`io:put_chars/1`, :erl:func:`io:put_chars(Chars)`
      * :erl:func:`io:format/1`
      * :erl:func:`io:format/2`
      * :erl:func:`io:format/3`

   .. seealso::

      * :rst:role:`erl:func`
      * :rst:dir:`py:function`


.. rst:directive:: .. erl:type:: type_name(Arg1, Arg2, ...)

   Describes a type.

   A type signature consists of followings:

   * Module name followed by colon. (optional)
   * Type name. (mandatory)
   * Argument list (``(Arg1, Arg2, ...)``) or arity (``/arity``). (optional, but should write)
   * `Flavor name`_. (optional, experimental)
   * ``when`` description. (optional)

   For example::

     .. erl:module:: unicode

     .. erl:type:: chardata()

     .. erl:module:: orddict

     .. erl:type:: orddict(Key, Value)

        :param Key:    type of the keys of the dict.
        :type  Key:    term()
        :param Value:  type of the values of the dict.
        :type  Value:  term()

   Types can be referenced by :rst:role:`erl:type`, for example::

      * :erl:type:`unicode:chardata/0`, :erl:type:`unicode:chardata()`
      * :erl:type:`orddict:orddict/2`, :erl:type:`orddict:orddict(K, V)`

   .. seealso::

      * :rst:role:`erl:type`


.. rst:directive:: .. erl:opaque:: opaque_type_name(Arg1, Arg2, ...)

   Describes an opaque type.

   The objects declared by this directive belong to the same
   namespace of the objects declared by :rst:dir:`erl:type` directives.

   Opaque type signatures take same format as a :rst:dir:`erl:type` directive.

   For example::

     .. erl:module:: gb_trees

     .. erl:opaque:: tree(Key, Value)

        :param Key:    type of the keys of the tree.
        :type  Key:    term()
        :param Value:  type of the values of the tree.
        :type  Value:  term()

   Opaque types also can be referenced by :rst:role:`erl:type`, for example::

      * :erl:type:`gb_trees:tree/2`, :erl:type:`gb_trees:tree(K, V)`

   .. seealso::

      * :rst:role:`erl:type`


.. rst:directive:: .. erl:record:: #record_name{}

   Describes a record.

   Record signature consists of followings:

   * Module name followed by colon. (optional)
   * Record name. (mandatory)
   * Record body (``{ field description, ... }``) or arity (``/arity``). (optional)

   For example::

     .. erl:module:: file

     .. erl:record:: #file_info{}

        :param size:  size of the file.
        :type  size:  :type:`non_neg_integer()` | undefined
        :param type:  type of the file.
        :type  type:  ``device`` | ``directory`` | ``other`` | ``regular`` | ``symlink`` | ``undefined``

        ...

   Records can be referenced by :rst:role:`erl:record`, for example::

      * :erl:record:`file:#file_info{}`

   .. seealso::

      * :rst:role:`erl:record`


.. rst:directive:: .. erl:macro:: ?MACRO_NAME(Arg1, Arg2, ...) -> Result

   Describes a macro.

   Macro signature consists of followings:

   * Module name followed by colon. (optional)
   * Macro name. (mandatory)
   * Argument list (``(Arg1, Arg2, ...)``) or arity (``/arity``). (optional)
   * `Flavor name`_. (optional, experimental)
   * ``when`` description. (optional)
   * Return annoration (``-> ...``). (optional)

   For example::

     .. erl:module:: eunit

     .. erl:macro:: ?TEST

        This macro is always defined (to true, unless previously defined
        by the user to have another value) whenever EUnit is enabled at
        compile time.

     .. erl:macro:: ?assertEqual(Expect, Expr)

        Evaluates the expressions *Expect* and *Expr* and compares the
        results for equality, if testing is enabled. If the values are
        not equal, an informative exception will be generated.

        :param Expect:  an expected value.
        :type  Expect:  *A*
        :param Expr:    an actual value.
        :type  Expr:    *A*


   Macros can be referenced by :rst:role:`erl:macro`, for example::

      * :erl:macro:`eunit:?TEST`
      * :erl:macro:`eunit:?assertEqual/2`

   .. seealso::

      * :rst:role:`erl:macro`


.. rst:directive:: .. erl:callback:: callback_name(Arg1, Arg2, ...) -> Result

   Describes a callback function.

   Callbacks have an own namespace which is separated from
   :rst:dir:`erl:function`.

   Callback signature takes same format as :rst:dir:`erl:function`.

   For example::

     .. erl:module:: gen_event

     .. erl:callback:: handle_event(Event, State) -> Result

        Handles an event.

        :param Event:  the event.
        :type  Event:  term()
        :param State:  current state.
        :type  State:  term()
        :rtype:
          {``ok``, *NewState*} | {``ok``, *NewState*, ``hibernate``}
          | {``swap_handler``, *Args1*, *NewState*, *Handler2*, *Args2*} | ``remove_handler``

   Callbacks can be referenced by :rst:role:`erl:callback`, for example::

      * :erl:callback:`gen_event:handle_event/2`

   .. seealso::

      * :rst:role:`erl:callback`


Cross-referencing Erlang objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following roles refer to objects in modules and are possibly
hyperlinked if a matching identifier is found:

.. rst:role:: erl:mod

   Reference a module.

   For example::

     * :erl:mod:`lists`


.. rst:role:: erl:func

   Reference an Erlang function.

   Function reference signature has a same format as :rst:dir:`erl:function`.
   ``when`` clause and a return annoration are not used for searching a target.

   For example::

     * :erl:func:`lists:append/1`
     * :erl:func:`lists:append/2`

   .. seealso::

      * :rst:dir:`erl:function`


.. rst:role:: erl:type

   Reference a type or an opaque type.

   Type reference signature has a same format as :rst:dir:`erl:type` and
   :rst:dir:`erl:opaque`.
   ``when`` clause is not used for searching a target.

   For example::

     * :erl:type:`unicode:chardata/0` (public type)
     * :erl:type:`gb_trees:tree/2` (opaque type)

   .. seealso::

      * :rst:dir:`erl:type`
      * :rst:dir:`erl:opaque`


.. rst:role:: erl:record

   Reference a record.
   Actually, Erlang records have no namespaces.
   But Erlang domain handles with namespaces virtually.

   Record reference signature has a same format as :rst:dir:`erl:record`.

   For example::

     * :erl:record:`file:#file_info`

   .. seealso::

      * :rst:dir:`erl:record`


.. rst:role:: erl:macro

   Reference a macro.

   Macro reference signature has a same format as :rst:dir:`erl:macro`.
   ``when`` clause and a return annotation are not used for searching a target.

   For example::

      * :erl:macro:`eunit:?TEST`
      * :erl:macro:`eunit:?assertEqual/2`

   .. seealso::

      * :rst:dir:`erl:macro`


.. rst:role:: erl:callback

   Reference a callback

   Callback signature takes same format as :rst:role:`erl:func`.

   For example::

     * :erl:callback:`gen_event:handle_event/2`

   .. seealso::

      * :rst:dir:`erl:callback`


Options and fields for module level directives
----------------------------------------------

Available options:

``:noindex:``
  Prevent being shown in the general index.

``:deprecated:``
  Mark the object as deprecated.

``:module: MODULE``
  Temporary change of a module to which the object belogs.

``:flavor: FLAVOR``
  Experimantal feature.
  Same as `Flavor name`_ but not appeard in description text.

Example of options::

  .. erl:function:: func(Flag :: abc) -> Result
     :noindex:
     :deprecated:
     :module: some_mod
     :flavor: abc

     process ``abc`` feature.

Available fields:

``:param NAME:  DESC``
  Description of a parameter.

``:type  NAME:  TYPE``
  Type of a parameter.

  If the *TYPE* is plain text (no any markups), processed with
  :rst:role:`erl:type`.

``:returns:  DESC``
  Description of the return value.

``:rtype:  TYPE``
  Type of the return value.

  If the *TYPE* is plain text (no any markups), processed with
  :rst:role:`erl:type`.

``:raises NAME:  DESC``
  Description of an exception.

  If there is no corresponding ``:raisetype NAME:``, *NAME* is
  treated as *EXC_TYPE*. Could not use any markups in *NAME*.

  If *NAME* contains space char, unexpected result is rendered.

``:raisetype NAME:  EXC_TYPE``
  Type description for *NAME*.

  If the *EXC_TYPE* is plain text (no any markups), processed as
  following:

  * started with one of error class, ``error:``, ``throw:`` or ``exit:``,
    the error class is removed, output as plain text and continue to
    process rest part.
  * if consists of alphabets or digits only (``str.isalnum()``),
    outputed as literal.
  * otherwise, processed with :rst:role:`erl:type`.

Example of fields::

  .. erl:function:: func(Flag :: abc) -> Result

     process ``abc`` feature.

     :param Flag:  A flag.
     :type  Flag:  ``abc``
     :returns:  A result.
     :rtype:    result()
     :raises badarg:  If the argument is bad.
     :raises throw:some_exc():  Some exception.

Following directives are met as module level directives:

* :rst:dir:`erl:function`
* :rst:dir:`erl:type`
* :rst:dir:`erl:opaque`
* :rst:dir:`erl:record`
* :rst:dir:`erl:macro`
* :rst:dir:`erl:callback`


Restriction on intersphinx target
---------------------------------

When hyperlinking by intersphinx,
link targets have written in either of followings

#. ``module:name``
#. ``module:name/arity``
#. ``module:name(Arg1, Arg2, ...)``

Flavor name
-----------

.. caution::

  This feature is implemented experimentally.
  This feature may be changed or removed in future release without notice.

Erlang domain can take an additional name in each objects.
Flavor name is not a part of Erlang Language, introduced by Erlang domain
itself to identify function clauses.

For example::

  .. erl:function:: erlang:process_flag(Flag, Value) -> OldBoolean

  .. erl:function:: erlang:process_flag(Flag :: trap_exit, Boolean) @trap_exit -> OldBoolean

  .. erl:function:: erlang:process_flag(Flag :: error_handler, Module) @error_handler -> OldModule

  .. erl:function:: erlang:process_flag(Flag :: min_heap_size, MinHeapSize) @min_heap_size -> OldMinHeapSize

  * :erl:func:`erlang:process_flag/2`
  * :erl:func:`erlang:process_flag/2@trap_exit`
  * :erl:func:`erlang:process_flag/2@error_handler`
  * :erl:func:`erlang:process_flag/2@min_heap_size`

These clauses are identified by the portion of ``@trap_exit`` or
``@error_handler``, not by the erlang code ``Flag :: trap_exit``.

It can be wrapped with brackets (``[`` and ``]``) to hide from document
texts. e.g.::

  .. erl:function:: erlang:process_flag(Flag :: trap_exit, Boolean) [@trap_exit] -> OldBoolean

  * :erl:func:`erlang:process_flag/2[@trap_exit]`
