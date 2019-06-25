# release_0.7 CHANGELOG



## v0.7.1 (2019-06-12)

### New Features


### Bug Fixes
- create a missing directory during hot reload after a new plugin install





## v0.7.0 (2019-05-24)

### New Features
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support


### Bug Fixes
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)





