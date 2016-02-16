#!/usr/bin/env python

# Based on MIT-licensed code from:
# https://www.stavros.io/posts/python-fuse-filesystem/

import os
import sys
import errno
import click
import hashlib
import keyring

from github3 import login
from fuse import FUSE, FuseOSError, Operations

debug = False

class IssueFS(Operations):
    def __init__(self, repo, username, password):
        self.repo = repo
        self.username = username
        self.password = password

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.repo, partial)
        return path

    def _contents(self, path):
        if debug: print '_contents path: %s' % (path)

        try:
            issue = int(path.strip('/').split('_')[0])
        except:
            return False

        if debug: print '_contents issue: %s' % (issue)

        gh = login(self.username, self.password)
        issue = gh.issue(self.username, self.repo, issue)
        issue_contents = '%s \n %s' % (issue.title, issue.body)
        if debug: print '_contents issue_contents: %s' % (issue_contents)
        return issue_contents

    def _hash(self, value):
        return hashlib.md5(value).hexdigest()


    # Filesystem methods
    # ==================

    def access(self, path, mode):
        # if debug: print 'access mode: %s, path: %s ' % (mode, path)
        if False:
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        if debug: print 'chmod mode: %s, path: %s ' % (mode, path)
        return True

    def chown(self, path, uid, gid):
        if debug: print 'chown uid: %s, gid: %s, path: %s ' % (uid, gid, path)
        return True

    def getattr(self, path, fh=None):
        if debug: print 'getattr path: %s' % (path)

        if (path.endswith('/')) or ('/.' in path):
            s = {'st_ctime': 1450647916.0, 'st_mtime': 1450647886.0, 'st_nlink': 19, 'st_mode': 16877, 'st_size': 0, 'st_gid': 20, 'st_uid': 501, 'st_atime': 1455426628.0}
        else:
            path_content = self._contents(path)
            size = len(path_content)
            s = {'st_ctime': 1450647916.0, 'st_mtime': 1450647886.0, 'st_nlink': 19, 'st_mode': 33188, 'st_size': size, 'st_gid': 20, 'st_uid': 501, 'st_atime': 1455426628.0}
        return s

    def readdir(self, path, fh):
        if debug: print 'readdir path: %s' % (path)

        if path == '/':
            dirents = ['.', '..']

            gh = login(self.username, self.password)
            for issue in gh.iter_repo_issues(self.username, self.repo):
                this_issue = ('%s_%s' % (issue.number, issue.title))[:255]
                dirents.append(this_issue)

            for r in dirents:
                if debug: print r
                if r.endswith('.pyc'):
                    pass
                else:
                    yield r

    def readlink(self, path):
        if debug: print 'readlink path: %s' % (path)
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.repo)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        if debug: print 'mknod path: %s' % (path)
        return

    def rmdir(self, path):
        if debug: print 'rmdir path: %s' % (path)
        full_path = self._full_path(path)
        return

    def mkdir(self, path, mode):
        if debug: print 'mkdir path: %s' % (path)
        return

    def statfs(self, path):
        if debug: print 'statfs path: %s' % (path)
        return {'f_bsize': 1048576, 'f_bavail': 0, 'f_favail': 7745916, 'f_files': 3, 'f_frsize': 4096, 'f_blocks': 29321728, 'f_ffree': 7745916, 'f_bfree': 0, 'f_namemax': 255, 'f_flag': 0}

    def unlink(self, path):
        if debug: print 'unlink path: %s' % (path)
        return

    def symlink(self, name, target):
        if debug: print 'symlink path: %s' % (path)
        return

    def rename(self, old, new):
        if debug: print 'rename path: %s' % (path)
        return

    def link(self, target, name):
        if debug: print 'link path: %s' % (path)
        return

    def utimens(self, path, times=None):
        if debug: print 'utimens path: %s' % (path)
        return

    # File methods
    # ============

    def open(self, path, flags):
        if debug: print 'open path: %s' % (path)
        return True

    def create(self, path, mode, fi=None):
        if debug: print 'create path: %s' % (path)
        return

    def read(self, path, length, offset, fh):
        if debug: print 'read data from %s - %s:%s' % (path, length, offset)
        the_contents = self._contents(path)
        the_contents = str(the_contents[offset:offset+length])
        return the_contents

    def write(self, path, buf, offset, fh):
        if debug: print 'write path: %s' % (path)
        return True

    def truncate(self, path, length, fh=None):
        if debug: print 'truncate path: %s' % (path)
        return True

    def flush(self, path, fh):
        if debug: print 'flush path: %s' % (path)
        return True

    def release(self, path, fh):
        if debug: print 'release path: %s' % (path)
        return True

    def fsync(self, path, fdatasync, fh):
        if debug: print 'fsync path: %s' % (path)
        return True

@click.command()
@click.option('--mount', prompt='Mount point',
              help='The path where the filesystem will be mounted.')
@click.option('--repo', prompt='Github repo name',
              help='The name of the Github repo to watch.')
@click.option('--username', prompt='Username',
              help='The username for the Github repo.')
@click.option('--password', prompt='Password',
              help='The password for the Github repo.')
def new_issuefs(mount, repo, username, password):
    if not os.path.exists(mount):
        os.makedirs(mount)
    FUSE(IssueFS(repo, username, password), mount, nothreads=True, foreground=True)


if __name__ == '__main__':
    new_issuefs()