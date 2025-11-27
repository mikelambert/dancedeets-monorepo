#!/usr/bin/env python3

import getpass
from itertools import chain
import json
import os
import re
import subprocess
import shutil

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

GCS_BUCKET = 'gs://dancedeets-static'

# Files that need unhashed versions in GCS because they're not in the manifest
# These are loaded by name in templates or other code
UNHASHED_FILES = [
    'jquery.js',
    'homepageReact.js',
    'common.css',  # CSS files are requested by unhashed name from templates
]


def get_static_files():
    manifest_path = 'dist/manifest.json'
    if not os.path.exists(manifest_path):
        print(f'Warning: {manifest_path} not found, skipping cleanup')
        return set()
    with open(manifest_path) as f:
        manifest = json.load(f)
    source_files = list(manifest.values())
    source_files = [os.path.abspath(os.path.join('dist/js', x)) for x in source_files]
    new_source_files = list(chain.from_iterable([x, '%s.map' % x] for x in source_files))
    return set(new_source_files)


all_static_files = get_static_files()


def cleanup(path):
    if not os.path.exists(path):
        print(f'Warning: {path} not found, skipping cleanup')
        return
    for filename in os.listdir(path):
        abs_filename = os.path.abspath(os.path.join(path, filename))
        if abs_filename not in all_static_files:
            print(f'Removing {abs_filename}')
            os.remove(abs_filename)


if all_static_files:
    cleanup('dist/js')
    cleanup('dist/css/')

# Find gsutil command
gsutil = shutil.which('gsutil')
if not gsutil:
    user = getpass.getuser()
    gsutil = f'/Users/{user}/google-cloud-sdk/bin/gsutil'
    if not os.path.exists(gsutil):
        print('Warning: gsutil not found, skipping static file upload')
        exit(0)

max_age = 60 * 60 * 24
# -h header
# -m run copies in parallel
# -P preserve mtimes
# -n don't overwrite existing files
# -z compress files on upload
# -R recursive

# Check if dist directories exist before uploading
if os.path.exists('dist/js') or os.path.exists('dist/css'):
    # Upload dist/* to bucket root (not dist/ folder, which would create dist/dist/...)
    # The app expects files at gs://dancedeets-static/js/... not gs://dancedeets-static/dist/js/...
    cmd = f'{gsutil} -m -h "Cache-Control:public,max-age={max_age}" cp -P -n -z svg,css,js,json,map -R dist/* gs://dancedeets-static/'
    subprocess.check_output(cmd, shell=True)

    paths = 'gs://dancedeets-static/img'
    cmd = f'{gsutil} -m setmeta -r -h "Cache-Control:public,max-age={max_age}" {paths}'
    subprocess.check_output(cmd, shell=True)
else:
    print('Warning: dist/js or dist/css not found, skipping upload')


def create_unhashed_copies():
    """Create unhashed copies of files that aren't in the manifest.

    Some files (like jquery.js, homepageReact.js, common.css) are requested by unhashed name
    but only exist with hashed names in GCS. This function finds the latest
    hashed version and copies it to the unhashed name.
    """
    print('=== Creating unhashed copies for files not in manifest ===')

    for filename in UNHASHED_FILES:
        base_name = filename.rsplit('.', 1)[0]  # e.g., 'jquery' from 'jquery.js'
        ext = filename.rsplit('.', 1)[1]  # e.g., 'js' or 'css'

        # Use correct subdirectory based on file extension
        subdir = 'css' if ext == 'css' else 'js'

        # List files matching the pattern (e.g., jquery.*.js or common.*.css)
        try:
            result = subprocess.check_output(
                f'{gsutil} ls "{GCS_BUCKET}/{subdir}/{base_name}."*".{ext}" 2>/dev/null || true',
                shell=True,
                text=True
            )

            # Find the hashed version (contains hash between name and extension)
            # e.g., jquery.a9ded2cac92ff464a1d7.js or common.2bddc9ed51d3782e06d54343e9ffcd88.css
            hashed_pattern = re.compile(rf'{base_name}\.[a-f0-9]+\.{ext}$')
            hashed_files = [
                line.strip() for line in result.strip().split('\n')
                if line.strip() and hashed_pattern.search(line)
            ]

            if hashed_files:
                # Use the first (or most recent) hashed file
                source_file = hashed_files[0]
                dest_file = f'{GCS_BUCKET}/{subdir}/{filename}'

                print(f'Copying {source_file} -> {dest_file}')
                cmd = f'{gsutil} cp "{source_file}" "{dest_file}"'
                subprocess.check_output(cmd, shell=True)
            else:
                print(f'Warning: No hashed version found for {filename}')

        except subprocess.CalledProcessError as e:
            print(f'Warning: Failed to process {filename}: {e}')


# Create unhashed copies for files not in manifest
create_unhashed_copies()
