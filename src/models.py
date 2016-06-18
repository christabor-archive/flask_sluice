"""SQL models for the sluice front-end."""

from __future__ import absolute_import

from sqlalchemy import (
    Column,
    Date,
    Enum,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def enum2list(enum):
    """Extract fileds from an enum for use in a form or anything else."""
    props = [(x, x) for x in vars(enum) if not x.startswith('__')]
    return props


def create_schemas(db):
    """Create all initial schemas."""
    Base.metadata.create_all(db)


class OutputFormat(Enum):
    """Prospector output format."""

    emacs = 'emacs'
    grouped = 'grouped'
    json = 'json'
    pylint = 'pylint'
    text = 'text'
    xunit = 'xunit'
    yaml = 'yaml'


class Strictness(Enum):
    """Prospector strictness levels."""

    verylow = 'verylow'
    low = 'low'
    medium = 'medium'
    high = 'high'
    veryhigh = 'veryhigh'


class BaseMixin:
    """Mixin for universal SQL config."""


class TestRun(Base, BaseMixin):
    """Represents a test run by prospector."""

    __tablename__ = 'testrun'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    created_by = Column(String(255))
    pathname = Column(String(255))
    strictness = Column(Strictness(name='strictness'))
    output = Column(OutputFormat(name='output'))
    results = Column(JSON())
