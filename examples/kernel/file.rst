.. module:: file

====
file
====

Module
======

file


Module Summary
==============

File interface module.


Description
===========

This module provides an interface to the file system.

.. warning::

  File operations are only guaranteed to appear atomic when going through
  the same file server. A NIF or other OS process may observe intermediate
  steps on certain operations on some operating systems, eg. renaming an
  existing file on Windows, or :func:`write_file_info/2` on any OS at the
  time of writing.

...


Data Types
==========

...

.. type:: io_device()

  As returned by :func:`open/2`; pid() is a process handling I/O-protocols.

  ::

    io_device() = pid() | fd()


.. type:: posix()

  An atom that is named from the POSIX error codes used in Unix, and in the
  runtime libraries of most C compilers.

  ::

    posix() =
        eacces | eagain | ebadf | ebadmsg | ebusy | edeadlk |
        edeadlock | edquot | eexist | efault | efbig | eftype |
        eintr | einval | eio | eisdir | eloop | emfile | emlink |
        emultihop | enametoolong | enfile | enobufs | enodev |
        enolck | enolink | enoent | enomem | enospc | enosr | enostr |
        enosys | enotblk | enotdir | enotsup | enxio | eopnotsupp |
        eoverflow | eperm | epipe | erange | erofs | espipe | esrch |
        estale | etxtbsy | exdev


...

Exports
=======

...

.. function:: open(File, Modes) -> {ok, IoDevice} | {error, Reason}

  ...

...


.. function:: write(IoDevice, Bytes) -> ok | {error, Reason}.

  Writes *Bytes* to the file referenced by *IoDevice*.

  :param IoDevice:  Io device.
  :type  IoDevice:  :type:`io_device()` | :type:`~erlang:atom()`
  :param Bytes:  Bytes.
  :type  Bytes:  ~erlang:iodata()
  :param Reason:  Error reason.
  :type  Reason:  :type:`posix()` | badarg | terminated
  :rtype:  ``ok`` | {``error``, *Reason*}

  This function is the only way to write to a file opened in raw mode
  (although it works for normally opened files too). Returns ``ok`` if
  successful, and ``{error, Reason}`` otherwise.

  If the file is opened with ``encoding`` set to something else than
  ``latin1``, each byte written can result in many bytes being written to
  the file, as the byte range 0..255 can represent anything between one and
  four bytes depending on value and UTF encoding type.

  Typical error reasons:

  ``ebadf``
    The file is not opened for writing.

  ``enospc``
    No space is left on the device.

.. function:: write_file_info(Filename, FileInfo) -> ok | {error, Reason}.
.. function:: write_file_info(Filename, FileInfo, Opts) -> ok | {error, Reason}.

  Changes file information.

  ...
