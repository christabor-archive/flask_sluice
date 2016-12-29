"""Flask WTForm models."""

from flask_wtf import Form

from wtforms import (
    SelectField,
    TextField,
    HiddenField,
)
from wtforms.validators import DataRequired

import models


strictness = [('', '')] + models.enum2list(models.Strictness)
output = [('', '')] + models.enum2list(models.OutputFormat)


class ProspectorResultsForm(Form):
    """A form for generating results from the prospector analysis tool."""

    name = TextField(u'Project name', validators=[DataRequired()])
    github_url = TextField(u'Github url', validators=[DataRequired()])
    strictness = SelectField(
        u'Strictness level',
        choices=strictness,
        validators=[DataRequired()])
    output = SelectField(
        u'Output format',
        choices=output,
        validators=[DataRequired()],
    )
    path = TextField(u'Filepath (e.g. ./foo/bar.py)',
                     validators=[DataRequired()])

    def validate_path(self, field):
        """Validate file path name."""
        # Folders are ok
        if '.' in field.data:
            # Python ending files only.
            if not field.data.endswith('.py'):
                raise ValueError('Only python files are allowed.')


class SearchForm(ProspectorResultsForm):
    """Searching."""

    action = HiddenField(default='search')
