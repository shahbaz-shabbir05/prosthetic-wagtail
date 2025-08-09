# TASKA Website
This repository contains the TASKA Prosthetic website, powered by the [Wagtail CMS](https://wagtail.org/). 

## Development
The development environment is containerised and has been tested with [Podman](https://podman.io/) on Windows, although
you should also be able to use Docker or a UNIX-based operating system for development.

### Starting / Building
Starting (and, if required, building) your dev environment is as easy as running `podman compose up` in your terminal.
Include the `-d` flag if you want to run your containers in the background, or omit the flag to follow your containers' output
in the terminal.

### Containers
The environment is made up of several containers:

* **django**: The main application server, powered by [Django](https://www.djangoproject.com/). Access it via localhost:8000.
* **worker**: The task queue worker, powered by [RQ](https://rq.readthedocs.io/en/latest/)
* **database**: The database server, powered by [Postgres](https://www.postgresql.org/)
* **tailwind**: The CSS compiler, powered by [Tailwind](https://tailwindcss.com/)
* **static**: The static file server, powered by [Lighttpd](https://www.lighttpd.net/). Access it via localhost:8001.
 
### Development Scripts
The following scripts are available:

* **scripts/managepy.bat**: A wrapper for [Django's manage.py](https://docs.djangoproject.com/en/4.0/ref/django-admin/) - use from your Windows terminal to interact with Django running in the container.
* **scripts/poetry.bat**: A wrapper for [Poetry](https://python-poetry.org/) - use from your Windows terminal to interact with Poetry running in the Django container.
* **scripts/npm.bat**: A wrapper for [NPM](https://www.npmjs.com/) - use from your Windows terminal to interact with NPM running in the tailwind container.

For example, to access the Django shell, run `scripts/managepy.bat shell`. Or to install a Django package, run `scripts/managepy.bat add <package_name>`.

### Building the static site
You will need to build the static site once before you can access it. To do this, run `scripts/managepy.bat build_async`.

From then on, static pages will automatically rebuild once a page is published or modified. 

## Architecture
Our website is a fairly simple Wagtail application, with a few notable tweaks:

* We are using our own `localize_crowdin` app to manage translations through [CrowdIn](https://crowdin.com/), TASKA's default translation service.
* We are building a static version of our website whenever a page is published or modified. The static version is intended to be deployed to global CDNs. The Django version is only meant for internal use and content management, and not for end-users.
* We are using [RQ](https://rq.readthedocs.io/en/latest/) as our task queue worker. The worker is used for asynchronous tasks, such as building static pages or dealing with the translation service

## Known issues
### CSS styles don't apply
If you find that your CSS styles don't apply, they are likely not being picked up by the Tailwind CSS processor.

The Tailwind processor will parse class names from your HTML files, but cannot parse classes when combined with Jinja template tags. When you try to add class names conditionally, you will have to use duplicate html attributes. See the examples below.

If this doesn't work, ensure the tailwind parser has successfully restarted after you have changed your HTML or CSS files. You can always restart the tailwind container and re-test.

#### DO
```html
<div
  {% if foo %}
  class="foo"
  {% else %}
  class="bar"
  {% endif %}
>
```

#### DON'T
```html
<!-- Tailwind will be unable to parse the class names because they don't have whitespace around them -->
<div class="{% if foo %}foo{% else %}bar{% endif %}">

<!-- The linter will strip the whitespace, before Tailwind starts parsing the file -->
<div class="{% if foo %} foo {% else %} bar {% endif %}">

<!-- Prettier will fail to work because one of the <div>s is not closed -->
{% if foo %}
<div class="foo">
{% else %}
<div class="bar">
{% endif %}
```

### Upgrading packages
Poetry doesn't yet provide a nice way for upgrading packages beyond the version constraints defined in `pyproject.toml`.

Install the `poetry-plugin-up` [plugin](https://github.com/MousaZeidBaker/poetry-plugin-up and) by running `scripts/poetry.bat self add poetry-plugin-up`. You can then follow the instructions in the plugin's repository to upgrade installed packages. Remember to use `scripts/poetry.bat` and not your host system's poetry installation!

## Deployment

Changes merged into the `main` branch are automatically deployed to the shared ECS cluster in AWS eu-central-1, which is accessable as https://djcms.taska.nz. Changes made to content on this site are uploaded to https://static-djcms.taska.nz/ (running on BunnyCDN).
