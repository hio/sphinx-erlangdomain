.. module:: gen_tcp

=======
gen_tcp
=======

Module
======

gen_tcp


Module Summary
==============


Interface to TCP/IP sockets.

Description
===========

This module provides functions for communicating with sockets using the
TCP/IP protocol.

...


Data Types
==========

...

.. type:: socket()

  As returned by :func:`accept/1`\ :func:`,2 <accept/2>` an
  :func:`connect/3`\ :func:`,4 <connect/4>`.


Exports
=======

.. function:: accept(ListenSocket) -> {ok, Socket} | {error, Reason}
  accept(ListenSocket, Timeout) -> {ok, Socket} | {error, Reason}

.. function:: connect(Address, Port, Options) -> {ok, Socket} | {error, Reason}
  connect(Address, Port, Options, Timeout) -> {ok, Socket} | {error, Reason}

.. function:: send(Socket, Packet) -> ok | {error, Reason}

  Sends a packet on a socket.

  :param Socket:  Socket.
  :type  Socket:  socket()
  :param Packet:  Packet data.
  :type  Packet:  ~erlang:iodata()
  :param Reason:  Error reason.
  :type  Reason:  ``closed`` | {``timeout``, *RestData*} | :type:`inet:posix()`
  :param RestData:  Rest data.
  :type  RestData:  ~erlang:binary()

  There is no send call with a time-out option, use socket option
  ``send_timeout`` if time-outs are desired. See section `Examples`_.

  The return value ``{error, {timeout, RestData}}`` can only be returned
  when ``inet_backend = socket``.

  .. note::

    Non-blocking send.

    If the user tries to send more data than there is room for in the OS
    send buffers, the 'rest data' is put into (inet driver) internal
    buffers and later sent in the background. The function immediately
    returns ok (**not** informing the caller that not all of the data was
    actually sent). Any issue while sending the 'rest data' is maybe
    returned later.

    When using ``inet_backend = socket``, the behaviour is different. There
    is **no** buffering done (like the inet-driver does), instead the
    caller will "hang" until all of the data has been sent or send timeout
    (as specified by the ``send_timeout`` option) expires (the function can
    hang even when using 'inet' backend if the internal buffers are full).

  If this happens when using ``packet =/= raw``, we have a partial package
  written. A new package therefor **must not** be written at this point, as
  there is no way for the peer to distinguish this from the data portion of
  the current package. Instead, set package to raw, send the rest data (as
  raw data) and then set package to the wanted package type again.


Examples
========

...
