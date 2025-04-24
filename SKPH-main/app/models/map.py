from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.extensions import db


class Coordinates(db.Model):
    __tablename__ = 'coordinates'
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Coordinates({self.x}, {self.y})"


class POI(db.Model):
    __tablename__ = 'poi'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    coordinates_id = Column(Integer, ForeignKey('coordinates.id'))
    coordinates = relationship('Coordinates', backref='poi')
    status = Column(Boolean, default=True)  # Status jako boolean
    type_of_poi = Column(String)  # Nowa kolumna na typ punktu

    def __init__(self, name: str, coordinates: Coordinates,
                 type_of_poi: str, status: bool = True):
        self.name = name
        self.coordinates = coordinates
        self.type_of_poi = type_of_poi
        self.status = status

    def __repr__(self):
        return (f"{self.name} ({self.coordinates.x}, {self.coordinates.y}, "
                f"Type: {self.type_of_poi}, Status: {self.status})")


class DangerArea(db.Model):
    __tablename__ = 'danger_area'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Boolean, default=True)  # Status jako boolean
    coordinates = Column(JSON)

    def __init__(self, name: str, coordinates: list, status: bool = True):
        self.name = name
        self.coordinates = coordinates
        self.status = status

    def __repr__(self):
        return f"DangerArea({self.name}, Status: {self.status})"


class ReliefArea(db.Model):
    __tablename__ = 'relief_area'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Boolean, default=True)
    coordinates = Column(JSON)

    def __init__(self, name: str, coordinates: list, status: bool = True):
        self.name = name
        self.coordinates = coordinates
        self.status = status

    def __repr__(self):
        return f"ReliefArea({self.name}, Status: {self.status})"
