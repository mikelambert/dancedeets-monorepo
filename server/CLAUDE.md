# DanceDeeets Server

There's a main deployment server and a main batch server, both exist in our production deployments.

There's also a basic "tutorials" server that one can run without the whole dancedeets setup, for simple iteration/demos.

# Tutorials Server

This is a standalone Node.js Express server that serves the DanceDeets tutorials application without requiring the Python/GAE backend.

## Quick Start

```bash
# 1. Install dependencies
npm install --legacy-peer-deps --ignore-scripts

# 2. Build the frontend bundles
npx webpack --config webpack.config.tutorials.js

# 3. Start the server
node tutorialsServer.js
```

The server will start on `http://localhost:3000`

### Running the Server

```bash
# Default port (3000)
node tutorialsServer.js

# Custom port
PORT=8080 node tutorialsServer.js
```

### Restarting After Changes

If the server is already running:
```bash
lsof -ti:3000 | xargs kill -9 2>/dev/null && node tutorialsServer.js
```

Or for a clean rebuild and restart:
```bash
npx webpack --config webpack.config.tutorials.js && \
lsof -ti:3000 | xargs kill -9 2>/dev/null && \
node tutorialsServer.js
```

# Main Server

## Docker Layering Strategy

The deployment uses a multi-layer Docker image hierarchy to optimize build times. Each layer is pushed to GCR and changes only need to rebuild from the layer that changed (and all layers above it).

### Image Hierarchy (bottom to top)

```
python:3.11-slim-bookworm (official Python base)
    └── gae-py-js        (adds Node.js 20 LTS)
        └── gae-nginx    (adds nginx)
            └── gae-geos (adds GEOS/Shapely libs)
                └── gae-binaries (adds imagemagick, gifsicle, Pillow deps)
                    └── gae-modules (adds core Python deps: pylibmc, google-cloud-*, etc.)
                        └── gae-modules-py (adds app Python deps: Flask, tweepy, etc.)
                            └── [main Dockerfile] (just copies app code)
```

### Why This Matters

1. **Fast app deploys**: The main `Dockerfile` only does `ADD . /app/` - no package installs. All dependencies are pre-baked in `gae-modules-py`.

2. **Layer caching**: If you only change app code, GAE pulls the cached `gae-modules-py` image and just adds your code on top. This takes seconds instead of 10+ minutes.

3. **Infrequent base rebuilds**: You only need to rebuild base layers when:
   - `gae-modules/requirements.txt` changes (core deps)
   - `gae-modules-py/requirements.txt` changes (app deps)
   - System packages need updating (apt-get installs)

### Building Base Images

Use gulp tasks to build and push base images:

```bash
# Build ALL layers from scratch (slow, rarely needed)
gulp buildDocker

# Build from a specific layer and everything above it
gulp buildDocker:gae-modules-py   # Just rebuild Python app deps
gulp buildDocker:gae-modules      # Rebuild core deps + app deps

# Build just ONE specific layer
gulp buildDocker:one:gae-modules-py
```

Each `docker/<layer>/build.sh` builds and pushes to `gcr.io/dancedeets-hrd/<layer>`.

### Deploying the App

The main `Dockerfile` should be minimal:

```dockerfile
FROM gcr.io/dancedeets-hrd/gae-modules-py

ADD . /app/
```

Then deploy with:
```bash
./build_tools/buildpush.sh
# or: gcloud app deploy
```

GAE builds the image in the cloud, pulling the cached base and just copying your code.

## Gulp Commands

You can find all commands in `server/gulpfile.babel.js`:

- `gulp buildDocker` - Build all Docker layers
- `gulp buildDocker:<layer>` - Build from a specific layer up
- `gulp buildDocker:one:<layer>` - Build just one layer
