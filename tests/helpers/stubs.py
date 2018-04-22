__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


class GitStub:
    def pull(self):
        return "Already up to date."


class RepoStub:
    git = GitStub()


repo_stub = RepoStub()
