version := `cat version`

_default:
   @just --list

venv:
    #!/bin/bash
    if [ ! -d ".venv" ]; then
    uv venv
    . ./.venv/bin/activate
    uv pip install -r requirements.txt
    fi

install-tailwind:
    #!/bin/bash
    if [ ! -d "node_modules" ]; then
    npm install
    fi

setup: venv install-tailwind

clean:
    rm -rf output .markata

pwd:
    pwd
ls:
    ls ./.venv/bin

build: clean
    markata-go build

build-fast:
    markata-go build --fast

build-clean:
    markata-go build --clean

build-container:
    #!/usr/bin/env bash
    set -euxo pipefail
    version=$(cat version)
    podman build -t registry.wayl.one/rhiannonwalker-com -t registry.wayl.one/rhiannonwalker-com:$version -f container/Containerfile .
    podman push registry.wayl.one/rhiannonwalker-com
    podman push registry.wayl.one/rhiannonwalker-com:$version

watch:
    markata-go serve --fast --host 0.0.0.0 --port 8005


serve:
    markata-go serve --host 0.0.0.0 --port 8005
tailwind:
    tailwindcss --input tailwind/app.css --output static/app-{{version}}.css --minify
tailwind-dev:
    tailwindcss --input tailwind/app.css --output markout/app-{{version}}.css --minify

compile:
  uv pip compile requirements.in -o requirements.txt --refresh

delete-release:
    #!/usr/bin/env bash
    set -euo pipefail

    # Get the version
    VERSION=$(cat version)

    # Delete the release
    gh release delete "v$VERSION"

create-tag:
    #!/usr/bin/env bash
    VERSION=$(cat version)
    git tag -a "v$VERSION" -m "Release v$VERSION"
    git push origin "v$VERSION"

delete-tag:
    #!/usr/bin/env bash
    VERSION=$(cat version)
    git tag -d "v$VERSION"
    git push --delete origin "v$VERSION"

create-release:
    #!/usr/bin/env bash
    VERSION=$(cat version)
    # git add version
    # git add requirements.in
    # git add requirements.txt
    # git add tailwind/app.css
    # git add static/app-{{version}}.css
    ./scripts/get_release_notes.py "$VERSION" > release_notes.tmp
    gh release create "v$VERSION" \
        --title "v$VERSION" \
        --notes-file release_notes.tmp
    rm release_notes.tmp


release:
   #!/bin/bash
   # tailwindcss --input tailwind/app.css --output static/app-{{version}}.css
   # git add version
   # git add requirements.in
   # git add requirements.txt
   # git add tailwind/app.css
   # git add static/app-{{version}}.css
   # git commit -m "Release v$(cat version)"
   # git tag -a "v$(cat version)" -m "Release v$(cat version)"
    ./scripts/get_release_notes.py "$VERSION" > release_notes.tmp
    gh release create "v$VERSION" \
        --title "v$VERSION" \
        --notes-file release_notes.tmp \
    rm release_notes.tmp
   git push
   git push --tags

dev:
   uvx --with awscli aws s3 sync ./markout s3://k8s-pages/rwdev --delete

prod:
   uvx --with awscli aws s3 sync s3://k8s-pages/rwdev s3://k8s-pages/rw

get-fragmention:
    curl https://raw.githubusercontent.com/chapmanu/fragmentions/refs/heads/master/fragmention.min.js > static/fragmention.min.js
    curl https://raw.githubusercontent.com/kartikprabhu/fragmentioner/refs/heads/master/fragmentioner.js > static/fragmentioner.js
