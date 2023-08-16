VENV_PATH=.venv
PYTHON_INTERPRETER=python3

FRONTEND_DIR=frontend
SANDBOX_DIR=sandbox
STATICFILES_DIR=$(SANDBOX_DIR)/static-sources

PYTHON_BIN=$(VENV_PATH)/bin/python
PIP=$(VENV_PATH)/bin/pip
TWINE=$(VENV_PATH)/bin/twine
DJANGO_MANAGE=$(SANDBOX_DIR)/manage.py
FLAKE=$(VENV_PATH)/bin/flake8
PYTEST=$(VENV_PATH)/bin/pytest
SPHINX_RELOAD=$(VENV_PATH)/bin/python sphinx_reload.py
TOX=$(VENV_PATH)/bin/tox

DEMO_DJANGO_SECRET_KEY=samplesecretfordev
PACKAGE_NAME=django-deovi
PACKAGE_SLUG=`echo $(PACKAGE_NAME) | tr '-' '_'`
APPLICATION_NAME=django_deovi

# Formatting variables, FORMATRESET is always to be used last to close formatting
FORMATBLUE:=$(shell tput setab 4)
FORMATBOLD:=$(shell tput bold)
FORMATRESET:=$(shell tput sgr0)

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo
	@echo "  clean                         -- to clean EVERYTHING (Warning)"
	@echo "  clean-var                     -- to clean data (uploaded medias, database, etc..)"
	@echo "  clean-doc                     -- to remove documentation builds"
	@echo "  clean-backend-install         -- to clean backend installation"
	@echo "  clean-frontend-install        -- to clean frontend installation"
	@echo "  clean-frontend-build          -- to clean frontend built files"
	@echo "  clean-pycache                 -- to remove all __pycache__, this is recursive from current directory"
	@echo
	@echo "  install-backend               -- to install backend requirements with Virtualenv and Pip"
	@echo "  install-frontend              -- to install frontend requirements with Npm"
	@echo "  install                       -- to install this project with virtualenv and Pip"
	@echo "  freeze-dependencies           -- to write a frozen.txt file with installed dependencies versions"
	@echo
	@echo "  run                           -- to run Django development server"
	@echo "  migrate                       -- to apply demo database migrations"
	@echo "  migrations                    -- to create new migrations for application after changes"
	@echo "  superuser                     -- to create a superuser for Django admin"
	@echo
	@echo "  po                            -- to update every PO files from project sources"
	@echo "  mo                            -- to build MO files from PO files"
	@echo
	@echo "  css                           -- to build CSS with default environnement"
	@echo "  watch-css                     -- to launch watcher CSS with default environnement"
	@echo "  css-prod                      -- to build CSS with production environnement"
	@echo
	@echo "  icomoon                       -- to update icon font map and files from an Icomoon snapshot (icomoon.zip)"
	@echo
	@echo "  js                            -- to build distributed Javascript with default environnement"
	@echo "  watch-js                      -- to launch watcher for Javascript sources with default environnement"
	@echo "  js-prod                       -- to build distributed Javascript with production environnement"
	@echo
	@echo "  frontend                      -- to build frontend assets from sources (CSS and JS) with default environnement"
	@echo "  frontend-prod                 -- to build frontend assets from sources (CSS and JS) with production environnement"
	@echo
	@echo "  docs                          -- to build documentation"
	@echo "  livedocs                      -- to run livereload server to rebuild documentation on source changes"
	@echo
	@echo "  flake                         -- to launch Flake8 checking"
	@echo "  test                          -- to launch base test suite using Pytest"
	@echo "  test-initial                  -- to launch tests with pytest and re-initialized database (for after new application or model changes)"
	@echo "  quality                       -- to launch Flake8 checking and every tests suites"
	@echo
	@echo "  check-release                 -- to check package release before uploading it to PyPi"
	@echo "  release                       -- to release package for latest version on PyPi (once release has been pushed to repository)"
	@echo

clean-pycache:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Clear Python cache <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf .tox
	rm -Rf .pytest_cache
	find . -type d -name "__pycache__"|xargs rm -Rf
	find . -name "*\.pyc"|xargs rm -f
.PHONY: clean-pycache

clean-var:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning var/ directory <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf var
.PHONY: clean-var

clean-doc:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Clear documentation <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf docs/_build
.PHONY: clean-doc

clean-backend-install:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning backend install <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(PACKAGE_SLUG).egg-info
	rm -Rf $(VENV_PATH)
.PHONY: clean-backend-install

clean-backend-build:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning backend built files <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf dist
.PHONY: clean-backend-build

clean-frontend-build:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning frontend built files <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(STATICFILES_DIR)/webpack-stats.json
	rm -Rf $(STATICFILES_DIR)/css
	rm -Rf $(STATICFILES_DIR)/js
.PHONY: clean-frontend-build

clean-frontend-install:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning frontend install <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(FRONTEND_DIR)/node_modules
.PHONY: clean-frontend-install

clean: clean-var clean-doc clean-backend-install clean-backend-build clean-frontend-install clean-frontend-build clean-pycache
.PHONY: clean

venv:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Install virtual environment <---$(FORMATRESET)\n"
	@echo ""
	virtualenv -p $(PYTHON_INTERPRETER) $(VENV_PATH)
	# This is required for those ones using old distribution
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade setuptools

create-var-dirs:
	@mkdir -p var/db
	@mkdir -p var/media
	@mkdir -p var/static
	@mkdir -p $(SANDBOX_DIR)/media
	@mkdir -p $(STATICFILES_DIR)/fonts
.PHONY: create-var-dirs

icon-font:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Copying bootstrap-icons to staticfiles directory <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(STATICFILES_DIR)/fonts/icons
	cp -r $(FRONTEND_DIR)/node_modules/bootstrap-icons/font/fonts $(STATICFILES_DIR)/fonts/icons
.PHONY: icon-font

install-backend:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Installing backend requirements <---$(FORMATRESET)\n"
	@echo ""
	$(PIP) install -e .[breadcrumbs,dev,quality,doc,release]
.PHONY: install-backend

install-frontend:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Installing frontend requirements <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm install
	${MAKE} icon-font
.PHONY: install-frontend

install: venv create-var-dirs install-backend migrate install-frontend frontend
.PHONY: install

check-migrations:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Checking for pending project applications models migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) makemigrations --check --dry-run -v 3
.PHONY: check-migrations

migrations:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Making application migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) makemigrations $(APPLICATION_NAME)
.PHONY: migrations

migrate:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Apply pending migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) migrate
.PHONY: migrate

superuser:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Create new superuser <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) createsuperuser
.PHONY: superuser

reset-migrations:
	@echo ""
	@echo "==== Remove all application migrations and local databases ===="
	@echo ""
	rm -Rf $(APPLICATION_NAME)/migrations
	rm -Rf var/db/*.sqlite3
	${MAKE} migrations
.PHONY: reset-migrations

po:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Update PO from 'lotus' app <---$(FORMATRESET)\n"
	@echo ""
	@cd $(APPLICATION_NAME); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) makemessages -a --keep-pot --no-obsolete
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Update PO from sandbox <---$(FORMATRESET)\n"
	@echo ""
	@cd $(SANDBOX_DIR); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) makemessages -a --keep-pot --no-obsolete
.PHONY: po

mo:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build PO from 'lotus' app <---$(FORMATRESET)\n"
	@echo ""
	@cd $(APPLICATION_NAME); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) compilemessages --verbosity 3
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build PO from sandbox <---$(FORMATRESET)\n"
	@echo ""
	@cd $(SANDBOX_DIR); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) compilemessages --verbosity 3
.PHONY: mo

run:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Running development server <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) runserver 0.0.0.0:8001
.PHONY: run

css:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build CSS for development environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run-script css
.PHONY: css

watch-sass:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Watching Sass sources for development environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run-script watch-css
.PHONY: watch-sass

css-prod:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build CSS for production environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run-script css-prod
.PHONY: css-prod

js:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build distributed Javascript for development environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run js
.PHONY: js

watch-js:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Watching Javascript sources for development environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run watch-js
.PHONY: watch-js

js-prod:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build distributed Javascript for production environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run js-prod
.PHONY: js-prod

frontend: css js
.PHONY: frontend

frontend-prod: css-prod js-prod
.PHONY: frontend-prod

docs:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build documentation <---$(FORMATRESET)\n"
	@echo ""
	cd docs && make html
.PHONY: docs

livedocs:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Watching documentation sources <---$(FORMATRESET)\n"
	@echo ""
	$(SPHINX_RELOAD)
.PHONY: livedocs

flake:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Flake <---$(FORMATRESET)\n"
	@echo ""
	$(FLAKE) --statistics --show-source $(APPLICATION_NAME) sandbox tests
.PHONY: flake

test:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Tests <---$(FORMATRESET)\n"
	@echo ""
	$(PYTEST) -vv --reuse-db tests/
	rm -Rf var/media-tests/
.PHONY: test

test-initial:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Tests from zero <---$(FORMATRESET)\n"
	@echo ""
	$(PYTEST) -vv --reuse-db --create-db tests/
	rm -Rf var/media-tests/
.PHONY: test-initial

freeze-dependencies:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Freeze dependencies versions <---$(FORMATRESET)\n"
	@echo ""
	$(VENV_PATH)/bin/python freezer.py
.PHONY: freeze-dependencies

tox:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Launch tests with Tox environments <---$(FORMATRESET)\n"
	@echo ""
	$(TOX)
.PHONY: tox

build-package:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Build package <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf dist
	$(VENV_PATH)/bin/python setup.py sdist
.PHONY: build-package

release: build-package
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Release <---$(FORMATRESET)\n"
	@echo ""
	$(TWINE) upload dist/*
.PHONY: release

check-release: build-package
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Check package <---$(FORMATRESET)\n"
	@echo ""
	$(TWINE) check dist/*
.PHONY: check-release

quality: test-initial flake docs check-release check-migrations freeze-dependencies
	@echo ""
	@echo "♥ ♥ Everything should be fine ♥ ♥"
	@echo ""
.PHONY: quality
