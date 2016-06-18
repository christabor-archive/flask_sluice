"""Commands for interfacing with the prospector module."""

import json
import subprocess


def get_results(path, strictness='veryhigh', output='json', asdict=True):
    """Execute the prospector module from the shell."""
    opts = dict(
        path=path,
        strictness=strictness,
        output=output)
    cmd = ('prospector {path} '
           '--strictness {strictness} '
           '--output-format {output}'.format(**opts))
    res = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    res = res.stdout.read()
    # The json module can also be used for yaml
    if asdict and output in ['json', 'yaml']:
        return dict(json.loads(res))
    return res
