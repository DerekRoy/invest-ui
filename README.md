# invest-ui
[Invest UI](https://www.directory.exportingisgreat.gov.uk/)

[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

---

## Requirements

[Python 3.6](https://www.python.org/downloads/release/python-360/)

[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)


## Local installation

    $ git clone https://github.com/uktrade/invest-ui
    $ cd invest-ui
    $ make

## Running with Docker
Requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker

    $ brew link gettext --force (OS X only)
    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
`.env` files will be automatically created (with `env_writer.py` working of the `env.json` file) by `make docker_test`, based on host environment variables with `INVEST_UI` prefix.

## Directory Forms

Form submissions are powered by [directory-forms-api](https://github.com/uktrade/directory-forms-api). Set the api up locally then generate an API client [here](http://forms.trade.great:8011/admin/client/client/) and add the following entries to your `conf/.env` file.

| Environment variable                                  | Notes                             |
| ----------------------------------------------------- | --------------------------------- |
| DIRECTORY_FORMS_API_API_KEY                           | Populate from client `access_key` |
| DIRECTORY_FORMS_API_SENDER_ID                         | Populate from client `identifier` |

## Debugging

### Setup debug environment

    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test

## CSS development

### Requirements
[node](https://nodejs.org/en/download/)
[SASS](http://sass-lang.com/)
[gulp](https://gulpjs.com/)

	$ npm install

### Update CSS under version control

	$ gulp sass

### Rebuild the CSS files when the scss file changes

	$ gulp sass:watch

## Session

Signed cookies are used as the session backend to avoid database usage. Therefore storing non-trivial data must be avoided in the session, or else the browser will be exposed to the data.


[circle-ci-image]: https://circleci.com/gh/uktrade/invest-ui/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/invest-ui/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/invest-ui/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/invest-ui

