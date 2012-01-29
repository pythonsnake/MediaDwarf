# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2012, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import copy

from sqlalchemy import (
    Table, Column, MetaData, Index,
    Integer, Float, Unicode, UnicodeText, DateTime, Boolean,
    ForeignKey, UniqueConstraint, PickleType)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, insert
from migrate import changeset

from mediagoblin.db.sql.base import GMGTableBase


# This one will get filled with local migrations
FULL_MIGRATIONS = {}


#######################################################
# Migration set 1: Define initial models, no migrations
#######################################################

Base1 = declarative_base(cls=GMGTableBase)

class Creature1(Base1):
    __tablename__ = "creature"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False, index=True)
    num_legs = Column(Integer, nullable=False)
    is_demon = Column(Boolean)

class Level1(Base1):
    __tablename__ = "level"

    id = Column(Unicode, primary_key=True)
    name = Column(Unicode)x
    description = Column(Unicode)
    exits = Column(PickleType)

SET1_MODELS = [Creature1, Level1]

SET1_MIGRATIONS = []

#######################################################
# Migration set 2: A few migrations and new model
#######################################################

Base2 = declarative_base(cls=GMGTableBase)

class Creature2(Base2):
    __tablename__ = "creature"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False, index=True)
    num_legs = Column(Integer, nullable=False)
    magical_powers = relationship("CreaturePower2")

class CreaturePower2(Base2):
    __tablename__ = "creature_power"

    id = Column(Integer, primary_key=True)
    creature = Column(
        Integer, ForeignKey('creature.id'), nullable=False)
    name = Column(Unicode)
    description = Column(Unicode)
    hitpower = Column(Integer, nullable=False)

class Level2(Base2):
    __tablename__ = "level"

    id = Column(Unicode, primary_key=True)
    name = Column(Unicode)
    description = Column(Unicode)

class LevelExit2(Base2):
    __tablename__ = "level_exit"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    from_level = Column(
        Unicode, ForeignKey('level.id'), nullable=False)
    to_level = Column(
        Unicode, ForeignKey('level.id'), nullable=False)

SET2_MODELS = [Creature2, CreaturePower2, Level2, LevelExit2]


@RegisterMigration(1, FULL_MIGRATIONS)
def creature_remove_is_demon(db_conn):
    """
    Remove the is_demon field from the creature model.  We don't need
    it!
    """
    metadata = MetaData(bind=db_conn.engine)
    creature_table = Table(
        'creature', metadata,
        autoload=True, autoload_with=db_conn.engine)
    creature_table.drop_column('is_demon')
    

@RegisterMigration(2, FULL_MIGRATIONS)
def creature_powers_new_table(db_conn):
    """
    Add a new table for creature powers.  Nothing needs to go in it
    yet though as there wasn't anything that previously held this
    information
    """
    metadata = MetaData(bind=db_conn.engine)
    creature_powers = Table(
        'creature_power', metadata,
        Column('id', Integer, primary_key=True),
        Column('creature', 
               Integer, ForeignKey('creature.id'), nullable=False),
        Column('name', Unicode),
        Column('description', Unicode),
        Column('hitpower', Integer, nullable=False))
    metadata.create_all(db_conn.engine)


@RegisterMigration(3, FULL_MIGRATIONS)
def level_exits_new_table(db_conn):
    """
    Make a new table for level exits and move the previously pickled
    stuff over to here (then drop the old unneeded table)
    """
    # First, create the table
    # -----------------------
    metadata = MetaData(bind=db_conn.engine)
    level_exits = Table(
        'level_exit', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode),
        Column('from_level',
               Integer, ForeignKey('level.id'), nullable=False),
        Column('to_level',
               Integer, ForeignKey('level.id'), nullable=False))
    metadata.create_all(db_conn.engine)

    # And now, convert all the old exit pickles to new level exits
    # ------------------------------------------------------------

    # Minimal representation of level table.
    # Not auto-introspecting here because of pickle table.  I'm not
    # sure sqlalchemy can auto-introspect pickle columns.
    levels = Table(
        'level', metadata,
        Column('id', Integer, primary_key=True),
        Column('exits', PickleType))

    # query over and insert
    result = db_conn.execute(
        select([levels], levels.c.exits!=None))

    for level in result:
        this_exit = level['exits']
        
        # Insert the level exit
        db_conn.execute(
            level_exits.insert().values(
                name=this_exit['name'],
                from_level=this_exit['from_level'],
                to_level=this_exit['to_level']))

    # Finally, drop the old level exits pickle table
    # ----------------------------------------------
    levels.drop_column('exits')    


# A hack!  At this point we freeze-fame and get just a partial list of
# migrations

SET2_MIGRATIONS = copy.copy(FULL_MIGRATIONS)

#######################################################
# Migration set 3: Final migrations
#######################################################

Base3 = declarative_base(cls=GMGTableBase)

class Creature3(Base3):
    __tablename__ = "creature"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False, index=True)
    num_limbs= Column(Integer, nullable=False)

class CreaturePower3(Base3):
    __tablename__ = "creature_power"

    id = Column(Integer, primary_key=True)
    creature = Column(
        Integer, ForeignKey('creature.id'), nullable=False, index=True)
    name = Column(Unicode)
    description = Column(Unicode)
    hitpower = Column(Float, nullable=False)
    magical_powers = relationship("CreaturePower3")

class Level3(Base3):
    __tablename__ = "level"

    id = Column(Unicode, primary_key=True)
    name = Column(Unicode)
    description = Column(Unicode)

class LevelExit3(Base3):
    __tablename__ = "level_exit"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    from_level = Column(
        Unicode, ForeignKey('level.id'), nullable=False, index=True)
    to_level = Column(
        Unicode, ForeignKey('level.id'), nullable=False, index=True)


SET3_MODELS = [Creature3, CreaturePower3, Level3, LevelExit3]


@RegisterMigration(4, FULL_MIGRATIONS)
def creature_num_legs_to_num_limbs(db_conn):
    """
    Turns out we're tracking all sorts of limbs, not "legs"
    specifically.  Humans would be 4 here, for instance.  So we
    renamed the column.
    """
    metadata = MetaData(bind=db_conn.engine)
    creature_table = Table(
        'creature', metadata,
        autoload=True, autoload_with=db_conn.engine)
    creature_table.c.num_legs.alter(name=u"num_limbs")


@RegisterMigration(5, FULL_MIGRATIONS)
def level_exit_index_from_and_to_level(db_conn):
    """
    Index the from and to levels of the level exit table.
    """
    metadata = MetaData(bind=db_conn.engine)
    level_exit = Table(
        'level_exit', metadata,
        autoload=True, autoload_with=db_conn.engine)
    Index('ix_from_level', level_exit.c.from_level).create(engine)
    Index('ix_to_exit', level_exit.c.to_exit).create(engine)


@RegisterMigration(6, FULL_MIGRATIONS)
def creature_power_index_creature(db_conn):
    """
    Index our foreign key relationship to the creatures
    """
    metadata = MetaData(bind=db_conn.engine)
    creature_power = Table(
        'creature_power', metadata,
        autoload=True, autoload_with=db_conn.engine)
    Index('ix_creature', creature_power.c.creature).create(engine)


@RegisterMigration(7, FULL_MIGRATIONS)
def creature_power_hitpower_to_float(db_conn):
    """
    Convert hitpower column on creature power table from integer to
    float.

    Turns out we want super precise values of how much hitpower there
    really is.
    """
    metadata = MetaData(bind=db_conn.engine)
    creature_power = Table(
        'creature_power', metadata,
        autoload=True, autoload_with=db_conn.engine)
    creature_power.c.hitpower.alter(type=Float)


def _insert_migration1_objects(session):
    """
    Test objects to insert for the first set of things
    """
    # Insert creatures
    session.add_all(
        [Creature1(name=u'centipede',
                   num_legs=100,
                   is_demon=False),
         Creature1(name=u'wolf',
                   num_legs=4,
                   is_demon=False),
         # don't ask me what a wizardsnake is.
         Creature1(name=u'wizardsnake',
                   num_legs=0,
                   is_demon=True)])

    # Insert levels
    session.add_all(
        [Level1(id=u'necroplex',
                name=u'The Necroplex',
                description=u'A complex full of pure deathzone.',
                exits={
                    'deathwell': 'evilstorm',
                    'portal': 'central_park'}),
         Level1(id=u'evilstorm',
                name=u'Evil Storm',
                description=u'A storm full of pure evil.',
                exits={}), # you can't escape the evilstorm
         Level1(id=u'central_park'
                name=u'Central Park, NY, NY',
                description=u"New York's friendly Central Park.",
                exits={
                    'portal': 'necroplex'})])

    session.commit()


def _insert_migration2_objects(session):
    """
    Test objects to insert for the second set of things
    """
    # Insert creatures
    session.add_all(
        [Creature2(
                name=u'centipede',
                num_legs=100),
         Creature2(
                name=u'wolf',
                num_legs=4,
                magical_powers = [
                    CreaturePower2(
                        name=u"ice breath",
                        description=u"A blast of icy breath!",
                        hitpower=20),
                    CreaturePower2(
                        name=u"death stare",
                        description=u"A frightening stare, for sure!",
                        hitpower=45)]),
         Creature2(
                name=u'wizardsnake',
                num_legs=0,
                magical_powers=[
                    CreaturePower2(
                        name=u'death_rattle',
                        description=u'A rattle... of DEATH!',
                        hitpower=1000),
                    CreaturePower2(
                        name=u'sneaky_stare',
                        description=u"The sneakiest stare you've ever seen!"
                        hitpower=300),
                    CreaturePower2(
                        name=u'slithery_smoke',
                        description=u"A blast of slithery, slithery smoke.",
                        hitpower=10),
                    CreaturePower2(
                        name=u'treacherous_tremors',
                        description=u"The ground shakes beneath footed animals!",
                        hitpower=0)])])

    # Insert levels
    session.add_all(
        [Level2(id=u'necroplex',
                name=u'The Necroplex',
                description=u'A complex full of pure deathzone.'),
         Level2(id=u'evilstorm',
                name=u'Evil Storm',
                description=u'A storm full of pure evil.',
                exits=[]), # you can't escape the evilstorm
         Level2(id=u'central_park'
                name=u'Central Park, NY, NY',
                description=u"New York's friendly Central Park.")])

    # necroplex exits
    session.add_all(
        [LevelExit2(name=u'deathwell',
                    from_level=u'necroplex',
                    to_level=u'evilstorm'),
         LevelExit2(name=u'portal',
                    from_level=u'necroplex',
                    to_level=u'central_park')])

    # there are no evilstorm exits because there is no exit from the
    # evilstorm
      
    # central park exits
    session.add_all(
        [LevelExit2(name=u'portal',
                    from_level=u'central_park',
                    to_level=u'necroplex')])

    session.commit()


def _insert_migration3_objects(session):
    """
    Test objects to insert for the third set of things
    """
    # Insert creatures
    session.add_all(
        [Creature3(
                name=u'centipede',
                num_limbs=100),
         Creature3(
                name=u'wolf',
                num_limbs=4,
                magical_powers = [
                    CreaturePower3(
                        name=u"ice breath",
                        description=u"A blast of icy breath!",
                        hitpower=20.0),
                    CreaturePower3(
                        name=u"death stare",
                        description=u"A frightening stare, for sure!",
                        hitpower=45.0)]),
         Creature3(
                name=u'wizardsnake',
                num_limbs=0,
                magical_powers=[
                    CreaturePower3(
                        name=u'death_rattle',
                        description=u'A rattle... of DEATH!',
                        hitpower=1000.0),
                    CreaturePower3(
                        name=u'sneaky_stare',
                        description=u"The sneakiest stare you've ever seen!"
                        hitpower=300.0),
                    CreaturePower3(
                        name=u'slithery_smoke',
                        description=u"A blast of slithery, slithery smoke.",
                        hitpower=10.0),
                    CreaturePower3(
                        name=u'treacherous_tremors',
                        description=u"The ground shakes beneath footed animals!",
                        hitpower=0.0)])],
        # annnnnd one more to test a floating point hitpower
        Creature3(
                name=u'deity',
                numb_limbs=30,
                magical_powers[
                    CreaturePower3(
                        name=u'smite',
                        description=u'Smitten by holy wrath!',
                        hitpower=9999.9))))

    # Insert levels
    session.add_all(
        [Level3(id=u'necroplex',
                name=u'The Necroplex',
                description=u'A complex full of pure deathzone.'),
         Level3(id=u'evilstorm',
                name=u'Evil Storm',
                description=u'A storm full of pure evil.',
                exits=[]), # you can't escape the evilstorm
         Level3(id=u'central_park'
                name=u'Central Park, NY, NY',
                description=u"New York's friendly Central Park.")])

    # necroplex exits
    session.add_all(
        [LevelExit3(name=u'deathwell',
                    from_level=u'necroplex',
                    to_level=u'evilstorm'),
         LevelExit3(name=u'portal',
                    from_level=u'necroplex',
                    to_level=u'central_park')])

    # there are no evilstorm exits because there is no exit from the
    # evilstorm
      
    # central park exits
    session.add_all(
        [LevelExit3(name=u'portal',
                    from_level=u'central_park',
                    to_level=u'necroplex')])

    session.commit()


def CollectingPrinter(object):
    def __init__(self):
        self.collection = []
    
    def __call__(self, string):
        self.collection.append(string)

    @property
    def combined_string(self):
        return u''.join(self.collection)


def create_test_engine():
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:', echo=False)
    sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return engine, Session


def assert_col_type(column, class):
    assert isinstance(column.type, class)


def test_set1_to_set3():
    # Create / connect to database
    # ----------------------------

    engine, Session = create_test_engine()

    # Create tables by migrating on empty initial set
    # -----------------------------------------------

    printer = CollectingPrinter
    migration_manager = MigrationManager(
        '__main__', SET1_MODELS, SET1_MIGRATIONS, Session(),
        printer)

    # Check latest migration and database current migration
    assert migration_manager.latest_migration == 0
    assert migration_manager.database_current_migration == None

    result = migration_manager.init_or_migrate()

    # Make sure output was "inited"
    assert result == u'inited'
    # Check output
    assert printer.combined_string == (
        "-> Initializing main mediagoblin tables... done.\n")
    # Check version in database
    assert migration_manager.latest_migration == 0
    assert migration_manager.database_current_migration == 0

    # Install the initial set
    # -----------------------

    _insert_migration1_objects(Session())

    # Try to "re-migrate" with same manager settings... nothing should happen
    migration_manager = MigrationManager(
        '__main__', SET1_MODELS, SET1_MIGRATIONS, Session(),
        printer)
    assert migration_manager.init_or_migrate() == None

    # Check version in database
    assert migration_manager.latest_migration == 0
    assert migration_manager.database_current_migration == 0

    # Sanity check a few things in the database...
    metadata = MetaData(bind=db_conn.engine)

    # Check the structure of the creature table
    creature_table = Table(
        'creature', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(creature_table.c.keys()) == set(
        ['id', 'name', 'num_legs', 'is_demon'])
    assert_col_type(creature_table.c.id, Integer)
    assert_col_type(creature_table.c.name, Unicode)
    assert creature_table.c.name.nullable is False
    assert creature_table.c.name.index is True
    assert creature_table.c.name.unique is True
    assert_col_type(creature_table.c.num_legs, Integer)
    assert creature_table.c.num_legs.nullable is False
    assert_col_type(creature_table.c.is_demon, Boolean)

    # Check the structure of the level table
    level_table = Table(
        'level', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(level_table.c.keys()) == set(
        ['id', 'name', 'description', 'exits'])
    assert_col_type(level_table.c.id, Unicode)
    assert level_table.c.id.primary_key is True
    assert_col_type(level_table.c.name, Unicode)
    assert_col_type(level_table.c.description, Unicode)
    # Skipping exits... Not sure if we can detect pickletype, not a
    # big deal regardless.

    # Now check to see if stuff seems to be in there.
    creature = session.query(Creature1).filter_by(
        name=u'centipede').one()
    assert creature.num_legs == 100
    assert creature.is_demon == False

    creature = session.query(Creature1).filter_by(
        name=u'wolf').one()
    assert creature.num_legs == 4
    assert creature.is_demon == False

    creature = session.query(Creature1).filter_by(
        name=u'wizardsnake').one()
    assert creature.num_legs == 0
    assert creature.is_demon == True

    level = session.query(Level1).filter_by(
        id=u'necroplex')
    assert level.name == u'The Necroplex'
    assert level.description == u'A complex of pure deathzone.'
    assert level.exits == {
        'deathwell': 'evilstorm',
        'portal': 'central_park'}

    level = session.query(Level1).filter_by(
        id=u'evilstorm')
    assert level.name == u'Evil Storm'
    assert level.description == u'A storm full of pure evil.'
    assert level.exits == {}  # You still can't escape the evilstorm!

    level = session.query(Level1).filter_by(
        id=u'central_park')
    assert level.name == u'Central Park, NY, NY'
    assert level.description == u"New York's friendly Central Park."
    assert level.exits == {
        'portal': 'necroplex'}

    # Create new migration manager, but make sure the db migration
    # isn't said to be updated yet
    printer = CollectingPrinter
    migration_manager = MigrationManager(
        '__main__', SET3_MODELS, SET3_MIGRATIONS, Session(),
        printer)

    assert migration_manager.latest_migration == 3
    assert migration_manager.database_current_migration == 0

    # Migrate
    result = migration_manager.init_or_migrate()

    # Make sure result was "migrated"
    assert result == u'migrated'

    # TODO: Check output to user
    assert printer.combined_string == """\
-> Updating main mediagoblin tables...
   + Running migration 1, "creature_remove_is_demon"... done.
   + Running migration 2, "creature_powers_new_table"... done.
   + Running migration 3, "level_exits_new_table"... done."""
    
    # Make sure version matches expected
    migration_manager = MigrationManager(
        '__main__', SET3_MODELS, SET3_MIGRATIONS, Session(),
        printer)
    assert migration_manager.latest_migration == 3
    assert migration_manager.database_current_migration == 3

    # Check all things in database match expected

    # Check the creature table
    creature_table = Table(
        'creature', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(creature_table.c.keys()) == set(
        ['id', 'name', 'num_limbs'])
    assert_col_type(creature_table.c.id, Integer)
    assert_col_type(creature_table.c.name, Unicode)
    assert creature_table.c.name.nullable is False
    assert creature_table.c.name.index is True
    assert creature_table.c.name.unique is True
    assert_col_type(creature_table.c.num_legs, Integer)
    assert creature_table.c.num_legs.nullable is False

    # Check the CreaturePower table
    creature_power_table = Table(
        'creature_power', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(creature_power_table.c.keys()) == set(
        ['id', 'creature', 'name', 'description', 'hitpower'])
    assert_col_type(creature_power_table.c.id, Integer)
    assert_col_type(creature_power_table.c.creature, Integer)
    assert creature_power_table.c.creature.nullable is False
    assert_col_type(creature_power_table.c.name, Unicode)
    assert_col_type(creature_power_table.c.description, Unicode)
    assert_col_type(creature_power_table.c.hitpower, Float)
    assert creature_power_table.c.hitpower.nullable is False

    # Check the structure of the level table
    level_table = Table(
        'level', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(level_table.c.keys()) == set(
        ['id', 'name', 'description'])
    assert_col_type(level_table.c.id, Unicode)
    assert level_table.c.id.primary_key is True
    assert_col_type(level_table.c.name, Unicode)
    assert_col_type(level_table.c.description, Unicode)

    # Check the structure of the level_exits table
    level_exit_table = Table(
        'level_exit', metadata,
        autoload=True, autoload_with=db_conn.engine)
    assert set(level_exit_table.c.keys()) == set(
        ['id', 'name', 'from_level', 'to_level'])
    assert_col_type(level_exit_table.c.id, Integer)
    assert_col_type(level_exit_table.c.name, Unicode)
    assert_col_type(level_exit_table.c.from_level, Unicode)
    assert level_exit_table.c.from_level.nullable is False
    assert level_exit_table.c.from_level.indexed is True
    assert_col_type(level_exit_table.c.to_level, Unicode)
    assert level_exit_table.c.to_level.nullable is False
    assert level_exit_table.c.to_level.indexed is True

    # Now check to see if stuff seems to be in there.
    creature = session.query(Creature1).filter_by(
        name=u'centipede').one()
    assert creature.num_limbs == 100.0
    assert creature.creature_powers == []

    creature = session.query(Creature1).filter_by(
        name=u'wolf').one()
    assert creature.num_limbs == 4.0
    assert creature.creature_powers == []

    creature = session.query(Creature1).filter_by(
        name=u'wizardsnake').one()
    assert creature.num_limbs == 0.0
    assert creature.creature_powers == []

    pass


def test_set2_to_set3():
    # Create / connect to database
    # Create tables by migrating on empty initial set

    # Install the initial set
    # Check version in database
    # Sanity check a few things in the database

    # Migrate
    # Make sure version matches expected
    # Check all things in database match expected
    pass


def test_set1_to_set2_to_set3():
    # Create / connect to database
    # Create tables by migrating on empty initial set

    # Install the initial set
    # Check version in database
    # Sanity check a few things in the database

    # Migrate
    # Make sure version matches expected
    # Check all things in database match expected

    # Migrate again
    # Make sure version matches expected again
    # Check all things in database match expected again

    ##### Set2
    # creature_table = Table(
    #     'creature', metadata,
    #     autoload=True, autoload_with=db_conn.engine)
    # assert set(creature_table.c.keys()) == set(
    #     ['id', 'name', 'num_legs'])
    # assert_col_type(creature_table.c.id, Integer)
    # assert_col_type(creature_table.c.name, Unicode)
    # assert creature_table.c.name.nullable is False
    # assert creature_table.c.name.index is True
    # assert creature_table.c.name.unique is True
    # assert_col_type(creature_table.c.num_legs, Integer)
    # assert creature_table.c.num_legs.nullable is False

    # # Check the CreaturePower table
    # creature_power_table = Table(
    #     'creature_power', metadata,
    #     autoload=True, autoload_with=db_conn.engine)
    # assert set(creature_power_table.c.keys()) == set(
    #     ['id', 'creature', 'name', 'description', 'hitpower'])
    # assert_col_type(creature_power_table.c.id, Integer)
    # assert_col_type(creature_power_table.c.creature, Integer)
    # assert creature_power_table.c.creature.nullable is False
    # assert_col_type(creature_power_table.c.name, Unicode)
    # assert_col_type(creature_power_table.c.description, Unicode)
    # assert_col_type(creature_power_table.c.hitpower, Integer)
    # assert creature_power_table.c.hitpower.nullable is False

    # # Check the structure of the level table
    # level_table = Table(
    #     'level', metadata,
    #     autoload=True, autoload_with=db_conn.engine)
    # assert set(level_table.c.keys()) == set(
    #     ['id', 'name', 'description'])
    # assert_col_type(level_table.c.id, Unicode)
    # assert level_table.c.id.primary_key is True
    # assert_col_type(level_table.c.name, Unicode)
    # assert_col_type(level_table.c.description, Unicode)

    # # Check the structure of the level_exits table
    # level_exit_table = Table(
    #     'level_exit', metadata,
    #     autoload=True, autoload_with=db_conn.engine)
    # assert set(level_exit_table.c.keys()) == set(
    #     ['id', 'name', 'from_level', 'to_level'])
    # assert_col_type(level_exit_table.c.id, Integer)
    # assert_col_type(level_exit_table.c.name, Unicode)
    # assert_col_type(level_exit_table.c.from_level, Unicode)
    # assert level_exit_table.c.from_level.nullable is False
    # assert_col_type(level_exit_table.c.to_level, Unicode)

    pass
