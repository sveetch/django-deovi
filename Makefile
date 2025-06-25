PYTHON_INTERPRETER=python3
VENV_PATH=.venv

FRONTEND_DIR=frontend
SANDBOX_DIR=sandbox
STATICFILES_DIR=$(SANDBOX_DIR)/static-sources

PYTHON_BIN=$(VENV_PATH)/bin/python
PIP_BIN=$(VENV_PATH)/bin/pip
FLAKE_BIN=$(VENV_PATH)/bin/flake8
PYTEST_BIN=$(VENV_PATH)/bin/pytest
SPHINX_RELOAD_BIN=$(PYTHON_BIN) docs/sphinx_reload.py
TOX_BIN=$(VENV_PATH)/bin/tox
TWINE_BIN=$(VENV_PATH)/bin/twine

DJANGO_MANAGE=manage.py

PACKAGE_NAME=django-deovi
PACKAGE_SLUG=django_deovi
APPLICATION_NAME=django_deovi

# Formatting variables, FORMATRESET is always to be used last to close formatting
FORMATBLUE:=$(shell tput setab 4)
FORMATGREEN:=$(shell tput setab 2)
FORMATRED:=$(shell tput setab 1)
FORMATBOLD:=$(shell tput bold)
FORMATRESET:=$(shell tput sgr0)

help:
	@echo "Please use 'make <target> [<target>...]' where <target> is one of"
	@echo
	@echo "  Cleaning"
	@echo "  ========"
	@echo
	@echo "  clean                      -- to clean EVERYTHING (Warning)"
	@echo "  clean-var                  -- to clean all data (Warning)"
	@echo "  clean-doc                  -- to clean documentation builds"
	@echo "  clean-backend-install      -- to clean Python side installation"
	@echo "  clean-frontend-install     -- to clean frontend installation"
	@echo "  clean-frontend-build       -- to clean frontend built files"
	@echo "  clean-pycache              -- to clean all Python cache files recursively"
	@echo
	@echo "  Documentation"
	@echo "  ============="
	@echo
	@echo "  docs                       -- to build documentation"
	@echo "  livedocs                   -- to run a 'live reloaded' server for documentation"
	@echo
	@echo "  Installation"
	@echo "  ============"
	@echo
	@echo "  freeze-dependencies        -- to write installed dependencies versions in frozen.txt"
	@echo "  install                    -- to install this project with virtualenv and Pip"
	@echo
	@echo "  Django commands"
	@echo "  ==============="
	@echo
	@echo "  run                        -- to run Django development server"
	@echo "  check-migrations           -- to check for pending application migrations (do not write anything)"
	@echo "  migrations                 -- to create new migrations for application after changes"
	@echo "  migrate                    -- to apply demo database migrations"
	@echo "  superuser                  -- to create a superuser for Django admin"
	@echo "  po                         -- to update every PO files from application for enabled languages"
	@echo "  mo                         -- to build MO files from application PO files"
	@echo
	@echo "  Search indexes commands"
	@echo "  ======================="
	@echo
	@echo "  search-build               -- to (Re)Build search engine indexes"
	@echo "  search-update              -- to update search engine indexes"
	@echo
	@echo "  Deployment"
	@echo "  =========="
	@echo
	@echo "  build-deployment           -- to build all deployment configurations defined in settings"
	@echo "  deploy                     -- to build and deploy all configurations"
	@echo
	@echo "  Frontend commands"
	@echo "  ================="
	@echo
	@echo "  css                        -- to build uncompressed CSS from Sass sources"
	@echo "  watch-css                  -- to watch for Sass changes to rebuild CSS"
	@echo "  css-prod                   -- to build compressed and minified CSS from Sass sources"
	@echo "  js                         -- to build uncompressed Javascript from sources"
	@echo "  watch-js                   -- to watch for Javascript sources changes to rebuild assets"
	@echo "  js-prod                    -- to build minified JS assets"
	@echo "  frontend                   -- to build uncompressed frontend assets (CSS, JS, etc..)"
	@echo "  frontend-prod              -- to build minified frontend assets (CSS, JS, etc..)"
	@echo
	@echo "  Quality"
	@echo "  ======="
	@echo
	@echo "  check-release              -- to check package release before uploading it to PyPi"
	@echo "  flake                      -- to launch Flake8 checking"
	@echo "  quality                    -- to launch run quality tasks and checks"
	@echo "  test                       -- to launch base test suite using Pytest"
	@echo "  test-initial               -- to launch base test suite using Pytest and re-initialized database"
	@echo "  tox                        -- to launch tests for every Tox environments"
	@echo
	@echo "  Release"
	@echo "  ======="
	@echo
	@echo "  release                    -- to release latest package version on PyPi"
	@echo

clean-pycache:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning Python cache <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf .pytest_cache
	find . -type d -name "__pycache__"|xargs rm -Rf
	find . -name "*\.pyc"|xargs rm -f
.PHONY: clean-pycache

clean-backend-install:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning installation <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(VENV_PATH)
	rm -Rf $(PACKAGE_SLUG).egg-info
.PHONY: clean-install

clean-doc:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning documentation <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf docs/_build
.PHONY: clean-doc

clean-var:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Cleaning data from 'var/' directory <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf var
.PHONY: clean-var

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

clean: clean-var clean-doc clean-backend-install clean-frontend-install clean-frontend-build clean-pycache
.PHONY: clean

create-var-dirs:
	@mkdir -p var/db
	@mkdir -p var/static/css
	@mkdir -p var/media
	@mkdir -p var/media-production
	@mkdir -p $(SANDBOX_DIR)/media
	@mkdir -p $(STATICFILES_DIR)/css
.PHONY: create-var-dirs

icon-font:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Copying bootstrap-icons to staticfiles directory <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(STATICFILES_DIR)/fonts/icons
	cp -r $(FRONTEND_DIR)/node_modules/bootstrap-icons/font/fonts $(STATICFILES_DIR)/fonts/icons
.PHONY: icon-font

venv:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Installing virtual environment <---$(FORMATRESET)\n"
	@echo ""
	virtualenv -p $(PYTHON_INTERPRETER) $(VENV_PATH)
.PHONY: venv

install-backend:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Installing everything for development <---$(FORMATRESET)\n"
	@echo ""
	$(PIP_BIN) install -e .[breadcrumbs,dev,quality,doc,doc-live,release]
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

check-django:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Running Django System check <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) check
.PHONY: check-django

migrations:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Making application migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) makemigrations $(APPLICATION_NAME)
.PHONY: migrations

check-migrations:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Checking for pending backend model migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) makemigrations --dry-run --check -v 3 $(APPLICATION_NAME)
.PHONY: check-migrations

reset-migrations:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Removing all application migrations and local databases <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf $(APPLICATION_NAME)/migrations
	rm -Rf var/db/*.sqlite3
	${MAKE} migrations
.PHONY: reset-migrations

migrate:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Applying pending migrations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) migrate
.PHONY: migrate

superuser:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Creating new superuser <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) createsuperuser
.PHONY: superuser

run:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Running development server <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) runserver 0.0.0.0:8001
.PHONY: run

po:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Updating PO from application <---$(FORMATRESET)\n"
	@echo ""
	@cd $(APPLICATION_NAME); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) makemessages -a --keep-pot --no-obsolete
.PHONY: po

mo:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building MO from application <---$(FORMATRESET)\n"
	@echo ""
	@cd $(APPLICATION_NAME); ../$(PYTHON_BIN) ../$(DJANGO_MANAGE) compilemessages --verbosity 3
.PHONY: mo

search-build:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> (Re)Building search indexes <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) rebuild_index -v 3 --noinput
.PHONY: search-build

search-update:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> (Re)Building search indexes <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) update_index -v 3 --remove
.PHONY: search-update

build-deployment:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building deployment configurations <---$(FORMATRESET)\n"
	@echo ""
	$(PYTHON_BIN) $(DJANGO_MANAGE) build_deployment --settings=sandbox.settings.production
.PHONY: build-deployment

deploy: build-deployment
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Deploying configurations <---$(FORMATRESET)\n"
	@echo ""
	sudo cp ./etc/010_django_deovi /etc/nginx/sites-available/
	sudo rm -f /etc/nginx/sites-enabled/010_django_deovi
	sudo ln -s /etc/nginx/sites-available/010_django_deovi /etc/nginx/sites-enabled/
	# TODO Run gunicorn script into a screen
	@printf "$(FORMATRED)$(FORMATBOLD)---> You will need now to run 'gunicorn_launcher.sh' script, remember to kill the previously runned identical script. <---$(FORMATRESET)\n"
.PHONY: deploy

css:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building CSS for development environment <---$(FORMATRESET)\n"
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
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building CSS for production environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run-script css-prod
.PHONY: css-prod

js:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building distributed Javascript for development environment <---$(FORMATRESET)\n"
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
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building distributed Javascript for production environment <---$(FORMATRESET)\n"
	@echo ""
	cd $(FRONTEND_DIR) && npm run js-prod
.PHONY: js-prod

frontend: css js
.PHONY: frontend

frontend-prod: css-prod js-prod
.PHONY: frontend-prod

docs:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building documentation <---$(FORMATRESET)\n"
	@echo ""
	cd docs && make html
.PHONY: docs

livedocs:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Watching documentation sources <---$(FORMATRESET)\n"
	@echo ""
	$(SPHINX_RELOAD_BIN)
.PHONY: livedocs

flake:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Running Flake <---$(FORMATRESET)\n"
	@echo ""
	$(FLAKE_BIN) --statistics --show-source $(APPLICATION_NAME) tests
.PHONY: flake

test:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Testing <---$(FORMATRESET)\n"
	@echo ""
	$(PYTEST_BIN) -vv --reuse-db tests/
	rm -Rf var/media-tests/
.PHONY: test

test-initial:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Testing from zero <---$(FORMATRESET)\n"
	@echo ""
	$(PYTEST_BIN) -vv --reuse-db --create-db tests/
	rm -Rf var/media-tests/
.PHONY: test-initial

freeze-dependencies:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Freeze dependencies versions <---$(FORMATRESET)\n"
	@echo ""
	$(VENV_PATH)/bin/python freezer.py ${PACKAGE_NAME} --destination=frozen.txt
.PHONY: freeze-dependencies

build-package:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Building package <---$(FORMATRESET)\n"
	@echo ""
	rm -Rf dist
	$(VENV_PATH)/bin/python setup.py sdist
.PHONY: build-package

release: build-package
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Releasing package <---$(FORMATRESET)\n"
	@echo ""
	$(TWINE_BIN) upload dist/*
.PHONY: release

check-release: build-package
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Checking package <---$(FORMATRESET)\n"
	@echo ""
	$(TWINE_BIN) check dist/*
.PHONY: check-release

tox:
	@echo ""
	@printf "$(FORMATBLUE)$(FORMATBOLD)---> Launching all Tox environments <---$(FORMATRESET)\n"
	@echo ""
	$(TOX_BIN)
.PHONY: tox

quality: check-django check-migrations test-initial flake docs check-release freeze-dependencies
	@echo ""
	@printf "$(FORMATGREEN)$(FORMATBOLD) ♥ ♥ Everything should be fine ♥ ♥ $(FORMATRESET)\n"
	@echo ""
	@echo ""
.PHONY: quality
