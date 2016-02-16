# issuefs

Exposing Github issues as filesystem objects since yesterday.

### Dependencies

* FUSE implementation for your platform - for Mac OSX, [OSXFUSE](https://osxfuse.github.io/) is tested
* Python
* Python modules, documented in ```requirements.txt```

### To test:

```
./issuefs.py --repo=<reponame> --username=<username> --password=<password> --mount=<mountpoint>
```