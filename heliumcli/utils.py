import re

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "2.0.0"


def should_update(line, verification, start_needle, end_needle=""):
    needs_update = False

    if line.strip().startswith(start_needle) and line.strip().endswith(end_needle):
        if line.strip() != verification:
            needs_update = True

    return needs_update


def sort_tags(tags):
    # Remove tags that don't match semantic versioning
    version_tags = []

    for git_tag in tags:
        cleaned_tag = git_tag.tag.tag.lstrip("v")
        pattern = re.compile("^[0-9\.]*$")
        if pattern.match(cleaned_tag):
            version_tags.append(git_tag)

    version_tags.sort(key=lambda v: list(map(int, v.tag.tag.lstrip("v").split("."))))

    return version_tags
