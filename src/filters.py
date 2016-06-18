"""Template filters."""


def get_strictness_label(strictness):
    """Get the alert box/label coloring based on strictness."""
    levels = dict(
        low='info',
        medium='warning',
        high='danger',
        veryhigh='danger',
    )
    if strictness not in levels:
        return 'default'
    return levels[strictness]


def error_label(error):
    """Get the alert box/label coloring based on error found."""
    levels = dict()
    levels['wrong-import-position'] = 'info'
    levels['fatal'] = 'danger'
    levels['MC0001'] = 'warning'  # McCabe's cyclomatic complexity warning.
    if error not in levels:
        return 'warning'
    return levels[error]
