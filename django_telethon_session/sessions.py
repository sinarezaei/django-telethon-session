import datetime
from enum import Enum

from telethon.tl import types
from telethon.sessions.memory import MemorySession
from telethon import utils
from telethon.crypto import AuthKey
from telethon.tl.types import (
    InputPhoto, InputDocument, PeerUser, PeerChat, PeerChannel
)
from django_telethon_session.models import TelethonEntity, TelethonSentFile, TelethonSession, TelethonUpdateState


class _SentFileType(Enum):
    DOCUMENT = 0
    PHOTO = 1

    @staticmethod
    def from_type(cls):
        if cls == InputDocument:
            return _SentFileType.DOCUMENT
        elif cls == InputPhoto:
            return _SentFileType.PHOTO
        else:
            raise ValueError('The cls must be either InputDocument/InputPhoto')


class DjangoSession(MemorySession):
    """This session contains the required information to login into your
       Telegram account. NEVER give the saved session file to anyone, since
       they would gain instant access to all your messages and contacts.

       If you think the session has been compromised, close all the sessions
       through an official Telegram client to revoke the authorization.
    """

    def __init__(self):
        super().__init__()
        # print('django session init')
        self.save_entities = True

        # db_sessions = TelethonSession.objects.all()
        # if db_sessions.count() > 0:
        #     db_session = db_sessions[0]
        db_session = TelethonSession.objects.all().first()
        if db_session is not None:
            self._dc_id = db_session.dc_id
            self._server_address = db_session.server_address
            self._port = db_session.port
            self._takeout_id = db_session.takeout_id

            akey = db_session.auth_key
            if isinstance(akey, memoryview):
                akey = akey.tobytes()
            self._auth_key = AuthKey(data=akey)
            # print('django session init finish 1')
        else:
            self._update_session_table()
            self.save()
            # print('django session init finish 2')

        # print('django session init finish final')

        # self._conn = None
        # c = self._cursor()
        # c.execute("select name from sqlite_master "
        #           "where type='table' and name='version'")
        # if c.fetchone():
        #     # Tables already exist, check for the version
        #     c.execute("select version from version")
        #     version = c.fetchone()[0]
        #     if version < CURRENT_VERSION:
        #         self._upgrade_database(old=version)
        #         c.execute("delete from version")
        #         c.execute("insert into version values (?)", (CURRENT_VERSION,))
        #         self.save()
        #
        #     # These values will be saved
        #     c.execute('select * from sessions')
        #     tuple_ = c.fetchone()
        #     if tuple_:
        #         self._dc_id, self._server_address, self._port, key, \
        #             self._takeout_id = tuple_
        #         self._auth_key = AuthKey(data=key)
        #
        #     c.close()
        # else:
        #     # Tables don't exist, create new ones
        #     self._create_table(
        #         c,
        #         "version (version integer primary key)"
        #         ,
        #         """sessions (
        #             dc_id integer primary key,
        #             server_address text,
        #             port integer,
        #             auth_key blob,
        #             takeout_id integer
        #         )"""
        #         ,
        #         """entities (
        #             id integer primary key,
        #             hash integer not null,
        #             username text,
        #             phone integer,
        #             name text
        #         )"""
        #         ,
        #         """sent_files (
        #             md5_digest blob,
        #             file_size integer,
        #             type integer,
        #             id integer,
        #             hash integer,
        #             primary key(md5_digest, file_size, type)
        #         )"""
        #         ,
        #         """update_state (
        #             id integer primary key,
        #             pts integer,
        #             qts integer,
        #             date integer,
        #             seq integer
        #         )"""
        #     )
        #     c.execute("insert into version values (?)", (CURRENT_VERSION,))
        #     self._update_session_table()
        #     c.close()
        #     self.save()

    def clone(self, to_instance=None):
        # print('django session clone')
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        return cloned

    # def _upgrade_database(self, old):
    #     c = self._cursor()
    #     if old == 1:
    #         old += 1
    #         # old == 1 doesn't have the old sent_files so no need to drop
    #     if old == 2:
    #         old += 1
    #         # Old cache from old sent_files lasts then a day anyway, drop
    #         c.execute('drop table sent_files')
    #         self._create_table(c, """sent_files (
    #             md5_digest blob,
    #             file_size integer,
    #             type integer,
    #             id integer,
    #             hash integer,
    #             primary key(md5_digest, file_size, type)
    #         )""")
    #     if old == 3:
    #         old += 1
    #         self._create_table(c, """update_state (
    #             id integer primary key,
    #             pts integer,
    #             qts integer,
    #             date integer,
    #             seq integer
    #         )""")
    #     if old == 4:
    #         old += 1
    #         c.execute("alter table sessions add column takeout_id integer")
    #     if old == 5:
    #         # Not really any schema upgrade, but potentially all access
    #         # hashes for User and Channel are wrong, so drop them off.
    #         old += 1
    #         c.execute('delete from entities')
    #
    #     c.close()

    # @staticmethod
    # def _create_table(c, *definitions):
    #     for definition in definitions:
    #         c.execute('create table {}'.format(definition))

    # Data from sessions should be kept as properties
    # not to fetch the database every time we need it
    def set_dc(self, dc_id, server_address, port):
        # print('django session set_dc')
        # print('django session set_dc dc_id ' + str(dc_id))
        # print('django session set_dc server_address ' + str(server_address))
        # print('django session set_dc port ' + str(port))
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()

        # Fetch the auth_key corresponding to this data center
        # row = self._execute('select auth_key from sessions')
        # if row and row[0]:
        #     self._auth_key = AuthKey(data=row[0])
        # else:
        #     self._auth_key = None
        auth_keys = TelethonSession.objects.all()
        # print(auth_keys)
        if auth_keys and auth_keys[0]:
            # print(auth_keys[0].auth_key)
            # print(type(auth_keys[0].auth_key))
            akey = auth_keys[0].auth_key
            if isinstance(akey, memoryview):
                akey = akey.tobytes()
            self._auth_key = AuthKey(data=akey)
        else:
            self._auth_key = None

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        # print('django session auth_key')
        # print('django session auth_key value ' + str(value))
        # print('django session auth_key value ' + str(value.key))
        self._auth_key = value
        self._update_session_table()

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        # print('django session takeout_id')
        # print('django session takeout_id value ' + str(value))
        self._takeout_id = value
        self._update_session_table()

    def _update_session_table(self):
        # print('django session _update_session_table')
        # c = self._cursor()
        # While we can save multiple rows into the sessions table
        # currently we only want to keep ONE as the tables don't
        # tell us which auth_key's are usable and will work. Needs
        # some more work before being able to save auth_key's for
        # multiple DCs. Probably done differently.
        # c.execute('delete from sessions')
        TelethonSession.objects.all().delete()
        # c.execute('insert or replace into sessions values (?,?,?,?,?)', (
        #     self._dc_id,
        #     self._server_address,
        #     self._port,
        #     self._auth_key.key if self._auth_key else b'',
        #     self._takeout_id
        # ))
        # c.close()
        TelethonSession.objects.update_or_create(
            dc_id=self._dc_id,
            defaults={
                'server_address': self._server_address,
                'port': self._port,
                'auth_key': self._auth_key.key if self._auth_key is not None else b'',
                'takeout_id': self._takeout_id
            }
        )

    def get_update_state(self, entity_id):
        # print('django session get_update_state')
        # row = self._execute('select pts, qts, date, seq from update_state '
        #                     'where id = ?', entity_id)
        # if row:
        #     pts, qts, date, seq = row
        #     date = datetime.datetime.fromtimestamp(
        #         date, tz=datetime.timezone.utc)
        #     return types.updates.State(pts, qts, date, seq, unread_count=0)
        try:
            update_state = TelethonUpdateState.objects.get(pk=entity_id)

            date = datetime.datetime.fromtimestamp(update_state.date, tz=datetime.timezone.utc)
            return types.updates.State(update_state.pts, update_state.qts, date, update_state.seq, unread_count=0)
        except TelethonUpdateState.DoesNotExist:
            # return None
            pass

    def set_update_state(self, entity_id, state):
        # print('django session set_update_state')
        # self._execute('insert or replace into update_state values (?,?,?,?,?)',
        #               entity_id, state.pts, state.qts,
        #               state.date.timestamp(), state.seq)
        try:
            update_state = TelethonUpdateState.objects.get(identifier=entity_id)
        except TelethonUpdateState.DoesNotExist:
            update_state = TelethonUpdateState(identifier=entity_id)
        update_state.pts = state.pts
        update_state.qts = state.qts
        update_state.date = state.date.timestamp()
        update_state.seq = state.seq
        update_state.save()

    def save(self):
        """Saves the current session object as session_user_id.session"""
        # # This is a no-op if there are no changes to commit, so there's
        # # no need for us to keep track of an "unsaved changes" variable.
        # if self._conn is not None:
        #     self._conn.commit()
        # print('django session save')
        pass

    # def _cursor(self):
    #     """Asserts that the connection is open and returns a cursor"""
    #     if self._conn is None:
    #         self._conn = sqlite3.connect(self.filename,
    #                                      check_same_thread=False)
    #     return self._conn.cursor()

    # def _execute(self, stmt, *values):
    #     """
    #     Gets a cursor, executes `stmt` and closes the cursor,
    #     fetching one row afterwards and returning its result.
    #     """
    #     c = self._cursor()
    #     try:
    #         return c.execute(stmt, values).fetchone()
    #     finally:
    #         c.close()

    def close(self):
        """Closes the connection unless we're working in-memory"""
        # if self.filename != ':memory:':
        #     if self._conn is not None:
        #         self._conn.commit()
        #         self._conn.close()
        #         self._conn = None
        # print('django session close')
        pass

    def delete(self):
        """Deletes the current session file"""
        # if self.filename == ':memory:':
        #     return True
        # try:
        #     os.remove(self.filename)
        #     return True
        # except OSError:
        #     return False
        # print('django session delete')
        TelethonSession.objects.all().delete()
        TelethonUpdateState.objects.all().delete()
        TelethonSentFile.objects.all().delete()
        TelethonEntity.objects.all().delete()
        return True

    @classmethod
    def list_sessions(cls):
        """Lists all the sessions of the users who have ever connected
           using this client and never logged out
        """
        # print('django session list_sessions')
        # return [os.path.splitext(os.path.basename(f))[0]
        #         for f in os.listdir('.') if f.endswith(EXTENSION)]
        return [str(s) for s in TelethonSession.objects.all()]

    # Entity processing

    def process_entities(self, tlo):
        """Processes all the found entities on the given TLObject,
           unless .enabled is False.

           Returns True if new input entities were added.
        """
        # print('django session process_entities')
        if not self.save_entities:
            return

        # print(tlo)

        rows = self._entities_to_rows(tlo)
        if not rows:
            return

        # c = self._cursor()
        # try:
        #     c.executemany(
        #         'insert or replace into entities values (?,?,?,?,?)', rows)
        #     # id integer primary key,
        #     # hash integer not null,
        #     # username text,
        #     # phone integer,
        #     # name text
        # finally:
        #     c.close()
        # print(rows)
        try:
            entity = TelethonEntity.objects.get(identifier=rows[0][0])
        except TelethonEntity.DoesNotExist:
            entity = TelethonEntity(identifier=rows[0][0])
        entity.hash = rows[0][1]
        entity.username = rows[0][2]
        entity.phone = rows[0][3]
        entity.name = rows[0][4]
        entity.save()

    def get_entity_rows_by_phone(self, phone):
        # print('django session get_entity_rows_by_phone')
        try:
            entity = TelethonEntity.objects.get(phone=phone)
            return [entity.identifier, entity.hash]
        except TelethonEntity.DoesNotExist:
            return None
        # return self._execute(
        #     'select id, hash from entities where phone = ?', phone)

    def get_entity_rows_by_username(self, username):
        # print('django session get_entity_rows_by_username')
        try:
            entity = TelethonEntity.objects.get(username=username)
            return [entity.identifier, entity.hash]
        except TelethonEntity.DoesNotExist:
            return None
        # return self._execute(
        #     'select id, hash from entities where username = ?', username)

    def get_entity_rows_by_name(self, name):
        # print('django session get_entity_rows_by_name')
        try:
            entity = TelethonEntity.objects.get(name=name)
            return [entity.identifier, entity.hash]
        except TelethonEntity.DoesNotExist:
            return None
        # return self._execute(
        #     'select id, hash from entities where name = ?', name)

    # noinspection PyShadowingBuiltins
    def get_entity_rows_by_id(self, id, exact=True):
        # print('django session get_entity_rows_by_id')
        if exact:
            try:
                entity = TelethonEntity.objects.get(identifier=id)
                return [entity.identifier, entity.hash]
            except TelethonEntity.DoesNotExist:
                return None
            # return self._execute(
            #     'select id, hash from entities where id = ?', id)
        else:
            try:
                entity = TelethonEntity.objects.get(identifier__in=[
                    utils.get_peer_id(PeerUser(id)),
                    utils.get_peer_id(PeerChat(id)),
                    utils.get_peer_id(PeerChannel(id))
                ])
                return [entity.identifier, entity.hash]
            except TelethonEntity.DoesNotExist:
                return None
            # return self._execute(
            #     'select id, hash from entities where id in (?,?,?)',
            #     utils.get_peer_id(PeerUser(id)),
            #     utils.get_peer_id(PeerChat(id)),
            #     utils.get_peer_id(PeerChannel(id))
            # )

    # File processing

    def get_file(self, md5_digest, file_size, cls):
        # print('django session get_file')
        try:
            sent_file = TelethonSentFile.objects.get(md5_digest=md5_digest, file_size=file_size, file_type=_SentFileType.from_type(cls).value)
            return cls(sent_file.identifier, sent_file.hash)
        except TelethonSentFile.DoesNotExist:
            return None

        # row = self._execute(
        #     'select id, hash from sent_files '
        #     'where md5_digest = ? and file_size = ? and type = ?',
        #     md5_digest, file_size, _SentFileType.from_type(cls).value
        # )
        # if row:
        #     # Both allowed classes have (id, access_hash) as parameters
        #     return cls(row[0], row[1])

    def cache_file(self, md5_digest, file_size, instance):
        # print('django session cache_file')
        if not isinstance(instance, (InputDocument, InputPhoto)):
            raise TypeError('Cannot cache %s instance' % type(instance))

        try:
            sent_file = TelethonSentFile.objects.get(md5_digest=md5_digest, file_size=file_size, file_type=_SentFileType.from_type(type(instance)).value)
        except TelethonSentFile.DoesNotExist:
            sent_file = TelethonSentFile(md5_digest=md5_digest, file_size=file_size, file_type=_SentFileType.from_type(type(instance)).value)
        sent_file.file_id = instance.id
        sent_file.hash = instance.access_hash
        sent_file.save()

        # self._execute(
        #     'insert or replace into sent_files values (?,?,?,?,?)',
        #     md5_digest, file_size,
        #     _SentFileType.from_type(type(instance)).value,
        #     instance.id, instance.access_hash
        # )
