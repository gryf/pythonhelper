Pythonhelper
============

This was a mirror of `http://www.vim.org/scripts/script.php?script_id=435`_.

This Vim plugin helps in Python development by placing a name of current class,
method or function under the cursor on the status line in normal and insert
mode.

Installation
------------

To use this plugin either ``+python`` or ``+python3`` feature compiled in vim is
required. To check it, issue ``:version`` in vim instance and look for python
entries.

To install it, any kind of Vim package manager can be used, like NeoBundle_,
Pathogen_, Vundle_ or vim-plug_.

For manual installation, copy subdirectories from this repository to your
``~/.vim`` directory.

Next, place one of the available functions either on your ``.vimrc``:

.. code:: vim

   set statusline=[....]\ %{TagInStatusLine()}\ [.....]

or under ``~/.vim/ftplugin/python/your_file.vim``:

.. code:: vim

   setlocal statusline=[....]\ %{TagInStatusLine()}\ [.....]

Functions, which may be placed on the status line are as follows:

* ``TagInStatusLine`` - shows name and type of the tag, i.e.:

  .. code::

     ClassName.some_method_name (method)

* ``TagInStatusLineTag`` - shows only the name:

  .. code::

     ClassName.some_method_name

* ``TagInStatusLineType`` - shows only the tag type:

  .. code::

     method

Restart vim, and you all set.

Changelog
---------

+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Version | Date       | Author         | Notes                                                                                                                                                                                     |
+=========+============+================+===========================================================================================================================================================================================+
| 1.1     | 2016-12-10 | Roman Dobosz   | Fixed python3 enabled vim (without python2)                                                                                                                                               |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1.0     | 2016-05-30 | Roman Dobosz   | Rewrite python part (simplifying the code, clean it up, separate from vimscript, add some tests), make it Python3 compatible, lots of other changes                                       |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|         | 2012-02-12 | cheater        | `Several bug fixes`_, code cleanup, docs update                                                                                                                                           |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|         | 2010-02-13 | Oluf Lorenzen  | `Updated the way how to display information on status line`_                                                                                                                              |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.83    | 2010-01-04 | Michal Vitecek | Added support for the CursorHoldI event so that the class/method/function is recognized also in Insert mode                                                                               |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.82    | 2009-07-10 | Michal Vitecek | fixed a bug when nested functions/classes were not properly detected                                                                                                                      |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.81    | 2003-03-13 | Michal Vitecek | fixed a small bug in indent level recognition                                                                                                                                             |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.80    | 2002-10-18 | Michal Vitecek | removed the dependency on exuberant ctags which parsed the python source code wrongly anyways. From now on only VIM with python support is needed. This might greatly help windoze users. |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.72    | 2002-10-03 | Michal Vitecek | fixed problem with parsing ctags output on python files that use tabs                                                                                                                     |
|         |            |                | when there is a syntax error in the file and ctags parses it incorrectly a warning is displayed in the command line                                                                       |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.71    | 2002-10-02 | Michal Vitecek | fixed problem with undefined window-bound variable w:PHStatusLine when a window has been split into two.                                                                                  |
|         |            |                | unbound event BufWinEnter because it's not needed because of the above change now                                                                                                         |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.70    | 2002-10-02 | Michal Vitecek | Initial upload                                                                                                                                                                            |
+---------+------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

License
-------

Originally, there was no licence whatsoever, so I've put it under under 3-clause
BSD license. See LICENSE file for details.

.. _Pathogen: https://github.com/tpope/vim-pathogen
.. _Vundle: https://github.com/gmarik/Vundle.vim
.. _NeoBundle: https://github.com/Shougo/neobundle.vim
.. _vim-plug: https://github.com/junegunn/vim-plug
.. _http://www.vim.org/scripts/script.php?script_id=435: http://www.vim.org/scripts/script.php?script_id=435
.. _Updated the way how to display information on status line: https://github.com/Finkregh/pythonhelper/commit/49d018fdc638f759a4d3d89f97ba5d26baddb1cd
.. _Several bug fixes: https://github.com/Finkregh/pythonhelper/pull/2
