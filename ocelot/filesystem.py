# -*- coding: utf-8 -*-
import appdirs
import hashlib
import os
import re
import unicodedata
import uuid

re_slugify = re.compile('[^\w\s-]', re.UNICODE)


def safe_filename(string):
    """Convert arbitrary strings to make them safe for filenames. Substitutes strange characters, and uses unicode normalization.

    Appends hash of `string` to avoid name collisions.

    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python"""
    safe = re.sub(
        '[-\s]+',
        '-',
        str(
            re_slugify.sub(
                '',
                unicodedata.normalize('NFKD', str(string))
            ).strip()
        )
    )
    if isinstance(string, str):
        string = string.encode("utf8")
    return safe + "." + hashlib.md5(string).hexdigest()


def create_dir(dirpath):
    """Create directory tree to `dirpath`; ignore if already exists"""
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    return dirpath


def check_dir(directory):
    """Returns ``True`` if given path is a directory and writeable, ``False`` otherwise."""
    return os.path.isdir(directory) and os.access(directory, os.W_OK)


def get_output_directory():
    """Get base directory for model run.

    Try the environment variable OCELOT_OUTPUT first, fall back to `appdirs <https://pypi.python.org/pypi/appdirs>`__"""
    try:
        env_var = create_dir(os.environ['OCELOT_OUTPUT'])
        assert env_var
        print("Using environment variable OCELOT_OUTPUT:\n", env_var)
        return env_var
    except:
        return create_dir(os.path.join(get_base_directory(), "model-runs"))


def get_cache_directory():
    """Get base directory where cache data (already extracted datasets) are saved.

    Creates directory is not already present."""
    return create_dir(os.path.join(get_base_directory(), "cache"))


def get_base_directory():
    """Get base directory where cache and output data are saved.

    Creates directory is not already present."""
    return create_dir(appdirs.user_data_dir("Ocelot", "ocelot_runs"))


class OutputDir(object):
    """OutputDir is responsible for creating and managing a model run output directory."""
    def __init__(self, dir_path=None):
        """Create the job id and output directory"""
        self.report_id = uuid.uuid4().hex
        if dir_path is None:
            dir_path = get_output_directory()
        self.directory = os.path.join(dir_path, self.report_id)
        try:
            create_dir(self.directory)
            assert check_dir(self.directory)
        except:
            raise OutputDirectoryError(
                "Can't find or write to output directory:\n\t{}".format(
                self.directory)
            )
