from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# User Class


class User(Base):

    '''
        This class is to create user table in the database
    '''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

# Company Class


class Company(Base):
    '''
        This Class is to create table in sqlite database
    '''
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

# Model Class


class Models(Base):
    '''
        This class is to create carmodels table it takes declarative
        base object as parameter
    '''
    __tablename__ = 'carmodels'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    image = Column(String(250))
    cc = Column(Integer)
    year = Column(Integer)
    colors = Column(String(250))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'colors': self.colors,
            'image': self.image,
            'cc': self.cc,
            'year': self.year,
        }

engine = create_engine('sqlite:///carmodels.db')
Base.metadata.create_all(engine)
