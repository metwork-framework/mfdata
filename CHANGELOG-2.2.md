# release_2.2 CHANGELOG

## v2.2.3 (2024-04-24)

### New Features

- add iniscripts, make and crontab as dependencies (backport #483) (#484)

## v2.2.2 (2024-04-05)

- No interesting change

## v2.2.1 (2024-04-03)

### Bug Fixes

- stop plugins before nginx stop (#481)

## v2.2.0 (2023-11-28)

### New Features

- keep original file name in trash directory (#449)
- add sonarqube check (#468)
- revert: remove sonarqube ci (we will use automatic analysis) (#469)

### Bug Fixes

- fix possibility to change plugin release
- template sftp send - Authentication (publickey) failed. (fix #457) (#458)
- fix .releaseignore to ignore .git folder when releasing plugins (#465)
- remove useless folder templates in installed plugins (#476)


