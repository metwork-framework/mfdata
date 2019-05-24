# release_0.7 CHANGELOG


## [Unreleased]

### New Features
- add optional mqtt 3.1.1 incoming messages support
- port "extra_daemon" feature from mfserv to mfdata
- incase of failure during failure policy, delete file and tags
- add missing initialization and description of some atributes
- port redis_service feature of mfserv to mfdata
- add keep-tags and keep-tags-suffix when failure-policy is move
- introduce log management with mfadmin


### Bug Fixes
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- fix typo
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix building issues with proxy
- don't clean nginx upload tmp directory
- catch some magic exception with some exotic files





