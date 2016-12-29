"""SQL models for the sluice front-end."""

from __future__ import absolute_import

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def enum2list(enum):
    """Extract fileds from an enum for use in a form or anything else."""
    props = [(x, x) for x in vars(enum) if not x.startswith('__')]
    return props


class OutputFormat(object):
    """Prospector output format."""

    emacs = "emacs"
    grouped = "grouped"
    json = "json"
    pylint = "pylint"
    text = "text"
    xunit = "xunit"
    yaml = "yaml"


class Strictness(object):
    """Prospector strictness levels."""

    verylow = "verylow"
    low = "low"
    medium = "medium"
    high = "high"
    veryhigh = "veryhigh"
