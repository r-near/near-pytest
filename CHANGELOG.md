# CHANGELOG


## v0.7.1 (2025-03-20)

### Bug Fixes

- **models**: Proper handling for view methods
  ([`b4cb6e9`](https://github.com/r-near/near-pytest/commit/b4cb6e99dc801fae61468d09dd74ab4bcc4559bf))


## v0.7.0 (2025-03-20)

### Features

- Add requests-like API for contract responses ([#3](https://github.com/r-near/near-pytest/pull/3),
  [`5c44755`](https://github.com/r-near/near-pytest/commit/5c4475586f29eda7b7fabf4cb2cc2d449f259306))

* feat: Add requests-like API for contract responses

* Update tests

* Return a contract response here as well

* Fix bug with ints

* Cleanup

* Linting and types


## v0.6.0 (2025-03-19)

### Features

- Add modular fixtures approach for more intuitive pytest-native testing
  ([#5](https://github.com/r-near/near-pytest/pull/5),
  [`03e4547`](https://github.com/r-near/near-pytest/commit/03e4547b24cdfc9a67159e9118376d5436d7e89f))

* feat: add modular fixtures for more intuitive pytest-native testing

* Minor cleanup

* Linting

* Safer compiler

* localnet

* Add entrypoint for auto-loading fixtures

* Simplify README


## v0.5.4 (2025-03-14)

### Bug Fixes

- **deps**: Update NEARC
  ([`ec364d1`](https://github.com/r-near/near-pytest/commit/ec364d13fabcf0d9c9796d1befda80f3bc682b1d))


## v0.5.3 (2025-03-14)

### Bug Fixes

- **deps**: Update NEARC to latest
  ([`197c5aa`](https://github.com/r-near/near-pytest/commit/197c5aadf1e6c7a703db6890dac9e3ffb7841e25))

### Chores

- **deps**: Create dependabot.yml
  ([`6bcf9dc`](https://github.com/r-near/near-pytest/commit/6bcf9dc297bb9dc65e7cd94ce9747efc2ea22c93))


## v0.5.2 (2025-03-13)

### Bug Fixes

- **deps**: Update nearc
  ([`1ebbe6f`](https://github.com/r-near/near-pytest/commit/1ebbe6f67446a8981601eb6670bfd6fbf7ce2cfe))


## v0.5.1 (2025-03-12)

### Bug Fixes

- **deps**: New version of NEARC
  ([`1e954c1`](https://github.com/r-near/near-pytest/commit/1e954c185501348b123f6cc05113f1d4304384c7))


## v0.5.0 (2025-03-12)

### Features

- Support parallelization with pytest-xdist
  ([`4261bda`](https://github.com/r-near/near-pytest/commit/4261bdae3ec0b35c483e2bea4a377d06544020a7))


## v0.4.2 (2025-03-11)

### Bug Fixes

- **deps**: Use published dependency
  ([`091f13b`](https://github.com/r-near/near-pytest/commit/091f13beb0c06afc7f902047e6dafd2805d9cfe0))


## v0.4.1 (2025-03-11)

### Bug Fixes

- **tests**: Fix broken test
  ([`c010f7c`](https://github.com/r-near/near-pytest/commit/c010f7cd3b9582c81015b8c664c9da78cf281ed4))


## v0.4.0 (2025-03-11)

### Features

- **models**: Return tuple of results
  ([`4b9a387`](https://github.com/r-near/near-pytest/commit/4b9a38753f720a452409812922d0473fc79dd803))


## v0.3.0 (2025-03-11)

### Features

- **client**: Add a `view_account` method
  ([`f949b46`](https://github.com/r-near/near-pytest/commit/f949b46b77295970f9c3647978cbdd3f2454995a))


## v0.2.1 (2025-03-11)

### Bug Fixes

- **models**: Proper exception naming
  ([`23c9ad7`](https://github.com/r-near/near-pytest/commit/23c9ad77a4ebb84e3277df227e55dce9e637bbf0))


## v0.2.0 (2025-03-11)

### Features

- Support sub-accounts
  ([`0d1d871`](https://github.com/r-near/near-pytest/commit/0d1d871ad5c7c3d2c3f5313b74ca0434a054e4bc))


## v0.1.3 (2025-03-11)

### Bug Fixes

- **ci**: Add more caching
  ([`1d935dd`](https://github.com/r-near/near-pytest/commit/1d935dd974569cd996f5c08b282b5d567990e2ec))


## v0.1.2 (2025-03-11)

### Bug Fixes

- **ci**: Add build directory cache for tests
  ([`b3787e1`](https://github.com/r-near/near-pytest/commit/b3787e17ae28fa57ea83b3006c5109271bd63296))


## v0.1.1 (2025-03-11)

### Bug Fixes

- **ci**: Split lint and test jobs, add emcc
  ([`754e673`](https://github.com/r-near/near-pytest/commit/754e6735f8c069c237367984aac376cbaa81ce7d))

### Chores

- **docs**: Update README
  ([`6e2f663`](https://github.com/r-near/near-pytest/commit/6e2f66318fe004170e4a2ec8345d54563686c587))


## v0.1.0 (2025-03-11)

### Bug Fixes

- Test examples
  ([`6e52237`](https://github.com/r-near/near-pytest/commit/6e52237a97f725dc3102f4262cb721df05ef834b))

### Chores

- **docs**: Add README
  ([`9004ccc`](https://github.com/r-near/near-pytest/commit/9004ccc466274d0461889411cfae7eedff2a9e17))

### Features

- Add GitHub workflows
  ([`e2ccaa7`](https://github.com/r-near/near-pytest/commit/e2ccaa7fa191e3784c640b5c80b9f57989cdfd3d))

- Add verbose mode
  ([`0840873`](https://github.com/r-near/near-pytest/commit/0840873cb6d79a1afca587d5c4d4533a008aab1e))

- Better error logging
  ([`739a14f`](https://github.com/r-near/near-pytest/commit/739a14fac1bd1dffcfb034d354f49bbbff9740d6))

- Single-file compilation, better logging
  ([`693c253`](https://github.com/r-near/near-pytest/commit/693c2534eca4b31b0a379ead49d22fcaafae4a18))

### Refactoring

- Add typing
  ([`fd45b58`](https://github.com/r-near/near-pytest/commit/fd45b58333139f6c5f1608e96d2923e3346e9e04))

- Better docs, test info
  ([`17e08c1`](https://github.com/r-near/near-pytest/commit/17e08c196284386bdf1108620ec112109e6aa305))
