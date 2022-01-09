from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
                       String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import *


class ServerDatabaseStorage:

    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.username = username
            self.last_login = datetime.now()

    class ActiveUsers:
        def __init__(self, user_id, ip, port, login_time):
            self.id = None
            self.ip = ip
            self.port = port
            self.user_id = user_id
            self.login_time = login_time

    class UsersLoginHistory:
        def __init__(self, user_id, login_time, ip, port):
            self.id = None
            self.ip = ip
            self.port = port
            self.user_id = user_id
            self.login_time = login_time

    class UsersContacts:
        def __init__(self, user_id, contact_id):
            self.id = None
            self.user_id = user_id
            self.contact_id = contact_id

    class UsersActivityHistory:
        def __init__(self, user_id):
            self.id = None
            self.user_id = user_id
            self.messages_sent = 0
            self.messages_received = 0

    def __init__(self, path):
        self.database_engine = create_engine(
            f'sqlite:///{path}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )

        self.metadata = MetaData()

        all_users_table = Table(
            'All_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String, unique=True),
            Column('last_login', DateTime)
        )

        active_users_table = Table(
            'Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('All_users.id'), unique=True),
            Column('ip', String),
            Column('port', Integer),
            Column('login_time', DateTime)
        )

        users_login_history_table = Table(
            'Users_login_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('All_users.id')),
            Column('login_time', DateTime),
            Column('ip', String),
            Column('port', String)
        )

        users_contacts_table = Table(
            'Users_contacts', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('All_users.id')),
            Column('contact', ForeignKey('All_users.id'))
        )

        users_activity_history_table = Table(
            'Users_activity_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('All_users.id')),
            Column('messages_sent', Integer),
            Column('messages_received', Integer)
        )

        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.UsersLoginHistory, users_login_history_table)
        mapper(self.UsersContacts, users_contacts_table)
        mapper(self.UsersActivityHistory, users_activity_history_table)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port):
        user_existing_check = self.session.query(self.AllUsers).filter_by(username=username)
        if user_existing_check.count():
            user = user_existing_check.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_activity_history = self.UsersActivityHistory(user.id)
            self.session.add(user_activity_history)

        new_active_user = self.ActiveUsers(user.id, ip, port, datetime.now())
        self.session.add(new_active_user)

        user_login_history = self.UsersLoginHistory(user.id, datetime.now(), ip, port)
        self.session.add(user_login_history)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        sender_id = self.session.query(self.AllUsers).filter_by(username=sender).first().id
        recipient_id = self.session.query(self.AllUsers).filter_by(username=recipient).first().id
        sender_row = self.session.query(self.UsersActivityHistory).filter_by(user_id=sender_id).first()
        sender_row.messages_sent += 1
        recipient_row = self.session.query(self.UsersActivityHistory).filter_by(user_id=recipient_id).first()
        recipient_row.messages_received += 1

        self.session.commit()

    def add_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(username=user).first()
        contact = self.session.query(self.AllUsers).filter_by(username=contact).first()

        if not contact or self.session.query(self.UsersContacts).filter_by(user_id=user.id, contact_id=contact.id).count():
            return

        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(username=user).first()
        contact = self.session.query(self.AllUsers).filter_by(username=contact).first()

        if not contact:
            return

        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user_id == user.id,
            self.UsersContacts.contact_id == contact.id
        ).delete()
        self.session.commit()

    def all_users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def users_login_history_list(self, username=None):
        query = self.session.query(
            self.AllUsers.username,
            self.UsersLoginHistory.login_time,
            self.UsersLoginHistory.ip,
            self.UsersLoginHistory.port
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)
        return query.all()

    def users_contacts_list(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).one()
        query = self.session.query(self.UsersContacts, self.AllUsers.username). \
            filter_by(user_id=user.id). \
            join(self.AllUsers, self.UsersContacts.contact_id == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    def users_activity_history_list(self, username=None):
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login,
            self.UsersActivityHistory.messages_sent,
            self.UsersActivityHistory.messages_received
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerDatabaseStorage()
    test_db.user_login('client_1', '192.168.1.4', 8080)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    print('--- Active users ---')
    print(test_db.active_users_list())
    test_db.user_logout('client_1')
    print('--- Active users after logout client_1 ---')
    print(test_db.active_users_list())
    print('--- Log history ---')
    print(test_db.users_login_history_list())
    print('--- All users ---')
    print(test_db.all_users_list())
    print('--- Users contact ---')
    print(test_db.users_contacts_list('client_2'))
    print('--- Users activity history ---')
    print(test_db.users_activity_history())

