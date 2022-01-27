Client side documentation
============================

Messaging client application. Supports
sending messages to users who are online, messages are encrypted
using the RSA algorithm with a key length of 2048 bit.

Supports command line arguments:

``python client.py {servername} {port} -n or --name {username} -p or -password {password}``

1. {server name} - message server address.
2. {port} - port on which connections are accepted
3. -n or --name - the username with which the system will be logged in.
4. -p or --password - user password.

client.py
~~~~~~~~~~

.. automodule:: client
   :members:
   :undoc-members:
   :show-inheritance:

client.add_contact.py
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.add_contact.AddContactDialog
   :members:
   :undoc-members:
   :show-inheritance:

client.client_db_storage.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.client_db_storage.ClientDatabaseStorage
   :members:
   :undoc-members:
   :show-inheritance:

client.delete_contact.py
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.delete_contact.DelContactDialog
   :members:
   :undoc-members:
   :show-inheritance:

client.main_window.py
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.main_window.ClientMainWindow
   :members:
   :undoc-members:
   :show-inheritance:

client.start_window.py
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.start_window.StartUserNameEnteringWindow
   :members:
   :undoc-members:
   :show-inheritance:

client.transport.py
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.transport.ClientTransport
   :members:
   :undoc-members:
   :show-inheritance:
