from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Raster

from .utilities import get_persistent_store_engine

engine = get_persistent_store_engine('flood_extents')
SessionMaker = sessionmaker(bind=engine)

Base = declarative_base()

class FloodExtent(Base):
    """
    SQLAlchemy table definition for storing flood extent rasters.
    """
    __tablename__ = 'flood_extents'

    # Columns
    id = Column(Integer, primary_key=True)
    username = Column(String)
    raster = Column(Raster)

    def __init__(self, username, wkb):
        """
        Constructor
        """
        self.username = username
        self.raster = wkb