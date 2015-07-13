# Put your persistent store initializer functions in here
from .model import engine, Base


def init_flood_extents_db(first_time):
    """
    Initialize the flood extent db.
    """
    Base.metadata.create_all(engine)

