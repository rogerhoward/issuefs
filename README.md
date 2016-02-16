# issuefs

Exposing Github issues as filesystem objects since yesterday.

__PLEASE__ do not use this. Ever. It's likely to blow up your computer, delete your Github repo, make you bald, and kick a puppy.

### Dependencies

* FUSE implementation for your platform - for Mac OSX, [OSXFUSE](https://osxfuse.github.io/) is tested
* Python
* Python modules, documented in ```requirements.txt```

### To test:

```
./issuefs.py --repo=<reponame> --username=<username> --password=<password> --mount=<mountpoint>
```