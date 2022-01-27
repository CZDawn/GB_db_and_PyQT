Server side documentation
=========================

Messenger server module. Processes dictionaries - messages, stores public keys of clients.

Usage

The module supports command line arguments:

1. -p - Port on which connections are accepted
2. -a - Address from which connections are accepted.
3. --no_gui Run only basic functions, without a graphical shell.

server.py
~~~~~~~~~~

.. automodule:: server
   :members:
   :undoc-members:
   :show-inheritance:

server.add_user.py
~~~~~~~~~~~~~~~~~~

.. autoclass:: server.add_user.RegisterUser
   :members:
   :undoc-members:
   :show-inheritance:

server.config_window.py
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.config_window.ConfigWindow
   :members:
   :undoc-members:
   :show-inheritance:

server.core.py
~~~~~~~~~~~~~~

.. autoclass:: server.core.MessageProcessor
   :members:
   :undoc-members:
   :show-inheritance:

server.descriptors.py
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.descriptors.Port
   :members:
   :undoc-members:
   :show-inheritance:

server.main_window.py
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.main_window.MainWindow
   :members:
   :undoc-members:
   :show-inheritance:

server.remove_user.py
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.remove_user.DelUserDialog
   :members:
   :undoc-members:
   :show-inheritance:

server.server_db_storage.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.server_db_storage.ServerDatabaseStorage
   :members:
   :undoc-members:
   :show-inheritance:

server.server_gui.py
~~~~~~~~~~~~~~~~~~~~

.. automodule:: server.server_gui
   :members:
   :undoc-members:
   :show-inheritance:

server.stat_window.py
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.stat_window.StatWindow
   :members:
   :undoc-members:
   :show-inheritance:
