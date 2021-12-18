.. module:: inet

====
inet
====

Module
======

inet


Module Summary
==============

Access to TCP/IP protocols.


Description
===========

This module provides access to TCP/IP protocols.

...


Data Types
==========

.. type:: posix()

  ::

    posix() =
        eaddrinuse | eaddrnotavail | eafnosupport | ealready |
        econnaborted | econnrefused | econnreset | edestaddrreq |
        ehostdown | ehostunreach | einprogress | eisconn | emsgsize |
        enetdown | enetunreach | enopkg | enoprotoopt | enotconn |
        enotty | enotsock | eproto | eprotonosupport | eprototype |
        esocktnosupport | etimedout | ewouldblock | exbadport |
        exbadseq |
        file:posix()

  An atom that is named from the POSIX error codes used in Unix, and in the
  runtime libraries of most C compilers. See section `POSIX Error Codes`_.

  .. seealso::

    * :type:`file:posix()`


Exports
=======



POSIX Error Codes
=================

* ``e2big`` - Too long argument list
* ...
