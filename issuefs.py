#!/usr/bin/env python

# Based on MIT-licensed code from:
# https://www.stavros.io/posts/python-fuse-filesystem/

import os
import sys
import errno
import click
import keyring

from github3 import login
from fuse import FUSE, FuseOSError, Operations

debug = False

class IssueFS(Operations):
    def __init__(self, repo, username, password):
        self.repo = repo
        self.username = username
        self.password = password

    def _contents(self, path):
        # Return contents of a given path
        # For now, return the issue title and body concatenated
        if debug: print '_contents path: %s' % (path)

        try:
            issue = int(path.strip('/').split('_')[0])
        except:
            return False

        if debug: print '_contents issue: %s' % (issue)

        # Get Github issue
        gh = login(self.username, self.password)
        issue = gh.issue(self.username, self.repo, issue)

        # Concatanate issue title and body and return as file content
        issue_contents = '%s \n %s' % (issue.title, issue.body)
        if debug: print '_contents issue_contents: %s' % (issue_contents)
        return issue_contents

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        if debug: print 'access mode: %s, path: %s ' % (mode, path)
        # Mock
        if False:
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        if debug: print 'chmod mode: %s, path: %s ' % (mode, path)
        # Mock
        return True

    def chown(self, path, uid, gid):
        if debug: print 'chown uid: %s, gid: %s, path: %s ' % (uid, gid, path)
        # Mock
        return True

    def getattr(self, path, fh=None):
        if debug: print 'getattr path: %s' % (path)

        # If path is a directory
        if path.endswith('/'):
            s = {'st_ctime': 1450647916.0, 'st_mtime': 1450647886.0, 'st_nlink': 19, 'st_mode': 16877, 'st_size': 0, 'st_gid': 20, 'st_uid': 501, 'st_atime': 1455426628.0}
        # Else if path is a hidden file
        elif ('/.' in path):
            s = {'st_ctime': 1450647916.0, 'st_mtime': 1450647886.0, 'st_nlink': 19, 'st_mode': 33188, 'st_size': 0, 'st_gid': 20, 'st_uid': 501, 'st_atime': 1455426628.0}
        # Else if path is anything else, assume it's an issue entry
        else:
            path_content = self._contents(path)
            s = {'st_ctime': 1450647916.0, 'st_mtime': 1450647886.0, 'st_nlink': 19, 'st_mode': 33188, 'st_size': len(path_content), 'st_gid': 20, 'st_uid': 501, 'st_atime': 1455426628.0}
        return s

    def readdir(self, path, fh):
        if debug: print 'readdir path: %s' % (path)

        # If root of device...
        if path == '/':
            # Add . and .. entries to children array
            children = ['.', '..']

            # Connect to Github
            gh = login(self.username, self.password)

            # Add issue "filename" to children array
            for issue in gh.iter_repo_issues(self.username, self.repo):
                issue_filename = ('%s_%s' % (issue.number, issue.title))[:255]
                children.append(issue_filename)

            # Return a generator object for each entry in children
            for entry in children:
                if debug: print entry
                yield entry

    def readlink(self, path):
        if debug: print 'readlink path: %s' % (path)
        # Mock
        return path

    def mknod(self, path, mode, dev):
        if debug: print 'mknod path: %s' % (path)
        # Mock
        return

    def rmdir(self, path):
        if debug: print 'rmdir path: %s' % (path)
        # Mock
        return path

    def mkdir(self, path, mode):
        if debug: print 'mkdir path: %s' % (path)
        # Mock
        return

    def statfs(self, path):
        if debug: print 'statfs path: %s' % (path)
        # Mocked up statfs return values for now
        # Mostly nonsensical but functional
        return {'f_bsize': 1048576, 'f_bavail': 0, 'f_favail': 7745916, 'f_files': 3, 'f_frsize': 4096, 'f_blocks': 29321728, 'f_ffree': 7745916, 'f_bfree': 0, 'f_namemax': 255, 'f_flag': 0}

    def unlink(self, path):
        if debug: print 'unlink path: %s' % (path)
        # Mock
        return

    def symlink(self, name, target):
        if debug: print 'symlink path: %s' % (path)
        # Mock
        return

    def rename(self, old, new):
        if debug: print 'rename path: %s' % (path)
        # Mock
        return

    def link(self, target, name):
        if debug: print 'link path: %s' % (path)
        # Mock
        return

    def utimens(self, path, times=None):
        if debug: print 'utimens path: %s' % (path)
        # Mock
        return

    # File methods
    # ============

    def open(self, path, flags):
        if debug: print 'open path: %s' % (path)
        # Mock
        return True

    def create(self, path, mode, fi=None):
        if debug: print 'create path: %s' % (path)
        # Mock
        return

    def read(self, path, length, offset, fh):
        if debug: print 'read data from %s - %s:%s' % (path, length, offset)
        # Retrieve contents, apply read offsets, and return
        # Added str() explicitly to return a byte array which read() expects
        return str(self._contents(path)[offset:offset+length])

    def write(self, path, buf, offset, fh):
        if debug: print 'write path: %s' % (path)
        # Mock
        return True

    def truncate(self, path, length, fh=None):
        if debug: print 'truncate path: %s' % (path)
        # Mock
        return True

    def flush(self, path, fh):
        if debug: print 'flush path: %s' % (path)
        # Mock
        return True

    def release(self, path, fh):
        if debug: print 'release path: %s' % (path)
        # Mock
        return True

    def fsync(self, path, fdatasync, fh):
        if debug: print 'fsync path: %s' % (path)
        # Mock
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
    # Ensure mountpoint already exists before mounting a FS to it
    if not os.path.exists(mount):
        os.makedirs(mount)

    # Create new FUSE filesystem at designated mountpoint using IssueFS
    FUSE(IssueFS(repo, username, password), mount, nothreads=True, foreground=True)


if __name__ == '__main__':
    new_issuefs()