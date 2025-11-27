# App Engine Flexible Deployment Guide

This guide documents the development loop for deploying the DanceDeets application to Google App Engine Flexible Environment and monitoring deployments for success or failure.

## Prerequisites

- gcloud CLI installed and configured
- Authenticated with Google Cloud: `gcloud auth login`
- Project set to `dancedeets-hrd`: `gcloud config set project dancedeets-hrd`

## Deployment Process

### 1. Deploy to App Engine Flexible

```bash
# Deploy to App Engine (takes 5-15 minutes)
gcloud app deploy app.yaml --project=dancedeets-hrd --quiet
```

**What happens during deployment:**
1. Files are uploaded to Google Cloud Storage
2. Docker image is built using Cloud Build (uses `Dockerfile`)
3. Image is pushed to Container Registry
4. New version is created and traffic is routed to it
5. Health checks are performed on the new instances

### 2. Monitor Deployment Progress

**Option A: Watch deployment in real-time**
```bash
# The deploy command shows progress automatically
# Look for these stages:
# - File upload
# - Docker build (Step #1, Step #2, etc.)
# - Image push
# - Instance startup
```

**Option B: Check deployment operations**
```bash
# List recent operations
gcloud app operations list --project=dancedeets-hrd --limit=5

# Get detailed status of latest operation
gcloud app operations describe <OPERATION_ID> --project=dancedeets-hrd
```

### 3. Check Deployment Status

**Check if deployment succeeded:**
```bash
# View versions
gcloud app versions list --project=dancedeets-hrd --service=default

# Check current serving version
gcloud app browse --project=dancedeets-hrd
```

**View instances:**
```bash
# List running instances
gcloud app instances list --project=dancedeets-hrd --service=default
```

## Monitoring for Errors

### 1. Check Build Logs

If deployment fails during the build phase:

```bash
# Get the Cloud Build ID from the operation
gcloud app operations describe <OPERATION_ID> --project=dancedeets-hrd

# View build logs
gcloud builds log <BUILD_ID> --project=dancedeets-hrd
```

### 2. Check Container Startup Logs

If deployment fails during container startup (error code 9):

```bash
# Get operation details with full error message
gcloud app operations describe <OPERATION_ID> --project=dancedeets-hrd

# The error message will show:
# - Python import errors
# - Module not found errors
# - Application crashes
# - Health check failures
```

### 3. Check Application Logs

Once deployed, monitor application logs:

```bash
# Stream logs in real-time
gcloud app logs tail --project=dancedeets-hrd --service=default

# Read recent logs
gcloud app logs read --project=dancedeets-hrd --service=default --limit=100

# Filter for errors
gcloud app logs read --project=dancedeets-hrd --service=default --limit=100 | grep ERROR
```

### 4. Check Health Endpoint

```bash
# Test the health check endpoint
curl https://dancedeets-hrd.appspot.com/_ah/health
```

## Common Failure Patterns

### Error Code 9: Worker Failed to Boot

This means the application crashed during startup before passing health checks.

**How to diagnose:**
```bash
# Get full error details
gcloud app operations describe <OPERATION_ID> --project=dancedeets-hrd
```

**Common causes:**
1. **ModuleNotFoundError** - Missing Python dependencies
   - Check `requirements.txt` has all needed packages
   - Check for legacy `google.appengine` imports that need migration
   - Check for missing compatibility stubs

2. **Import errors** - Code trying to import unavailable modules
   - MapReduce library (not available in Flexible)
   - Blobstore API (use Cloud Storage instead)
   - Legacy App Engine APIs

3. **Application crashes** - Errors in module-level code
   - Check syntax errors
   - Check for code that runs at import time

### Missing renderServer.js

This is a known issue with webpack not building properly.

**Current status:** The webpack build fails due to node-sass Python 2 dependency, but the Docker build continues with `|| true` so it doesn't fail the deployment.

**To fix:** Need to migrate from node-sass to sass (Dart Sass) in package.json

### Health Check Failures

If the app starts but fails health checks:

**Check:**
1. Is gunicorn starting? (check logs)
2. Is nginx configured correctly? (`nginx.conf`)
3. Is the `/_ah/health` endpoint responding?
4. Are there port conflicts? (nginx on 8080, gunicorn on 8085)

## Google Cloud Console Navigation

### View Deployment Status
1. Go to: https://console.cloud.google.com/appengine/versions?project=dancedeets-hrd
2. Select "default" service
3. Look for your version (format: YYYYMMDDTHHMMSS)
4. Check "Serving status" column

### View Instances
1. Go to: https://console.cloud.google.com/appengine/instances?project=dancedeets-hrd
2. Select "default" service
3. Should see 2 instances (per manual_scaling in app.yaml)

### View Logs
1. Go to: https://console.cloud.google.com/logs/query?project=dancedeets-hrd
2. Select "GAE Application" resource
3. Filter by severity: Error, Warning, etc.

## Development Loop Summary

1. **Make code changes**
   - Fix imports
   - Update dependencies
   - Test locally if possible

2. **Deploy**
   ```bash
   gcloud app deploy app.yaml --project=dancedeets-hrd --quiet
   ```

3. **Monitor build** (5-10 minutes)
   - Watch for Docker build completion
   - Check for dependency installation errors

4. **Check startup** (1-2 minutes)
   - Watch for "Waiting for operation to complete"
   - If it times out waiting, check operation status

5. **Verify or debug**
   ```bash
   # If successful:
   gcloud app browse --project=dancedeets-hrd

   # If failed:
   gcloud app operations list --project=dancedeets-hrd --limit=1
   gcloud app operations describe <OPERATION_ID> --project=dancedeets-hrd
   ```

6. **Check logs for runtime errors**
   ```bash
   gcloud app logs tail --project=dancedeets-hrd
   ```

## Quick Reference Commands

```bash
# Deploy
gcloud app deploy app.yaml --project=dancedeets-hrd --quiet

# Check latest operation
gcloud app operations list --project=dancedeets-hrd --limit=1

# Get operation details (replace with actual operation ID)
gcloud app operations describe 2418243c-beac-4c8e-8cd7-b79ba03ae6c9 --project=dancedeets-hrd

# View logs
gcloud app logs tail --project=dancedeets-hrd

# List versions
gcloud app versions list --project=dancedeets-hrd

# List instances
gcloud app instances list --project=dancedeets-hrd

# View in browser
gcloud app browse --project=dancedeets-hrd
```

## Migration Notes

### Legacy APIs Replaced

The following legacy App Engine APIs have been replaced:

| Legacy API | Replacement | Status |
|------------|-------------|---------|
| `google.appengine.ext.db` | `google.cloud.ndb` | ✅ Migrated |
| `google.appengine.api.datastore_errors` | `google.cloud.ndb.exceptions` | ✅ Migrated |
| `google.appengine.runtime.apiproxy_errors` | Generic exception handling | ✅ Migrated |
| `google.appengine.ext.vendor` | requirements.txt | ✅ Wrapped with try/except |
| `google.appengine.api.search` | `dancedeets.util.search_compat` | ✅ Compatibility layer |
| `google.appengine.ext.blobstore` | `dancedeets.compat.blobstore` | ✅ Compatibility stub |
| `mapreduce` | `mapreduce` package (stub) | ✅ Compatibility stub |

### Compatibility Stubs

Created compatibility stubs for unavailable libraries:
- `/server/mapreduce/__init__.py` - MapReduce stub package
- `/server/dancedeets/util/mapreduce_stub.py` - MapReduce implementation
- `/server/dancedeets/util/search_compat.py` - Search API compatibility
- `/server/dancedeets/test_utils/testbed_compat.py` - Testbed compatibility

These allow the app to import legacy modules without crashing, even though the functionality is disabled.

## Troubleshooting Tips

1. **Always check the operation details first** - It contains the full error message
2. **Look for ModuleNotFoundError** - Usually means a missing compatibility stub
3. **Check for import-time errors** - Code that runs when modules are imported
4. **Verify health endpoint** - Application must respond to `/_ah/health`
5. **Check both Python and Node logs** - The app runs both gunicorn (Python) and renderServer (Node.js)
6. **Remember the 10-minute timeout** - If startup takes too long, deployment fails

## Example Debugging Session

Here's a real example of debugging a failed deployment:

```bash
# 1. Check latest operation
$ gcloud app operations list --project=dancedeets-hrd --limit=1
ID                                    START_TIME                STATUS
2418243c-beac-4c8e-8cd7-b79ba03ae6c9  2025-11-24T03:21:53.202Z  PENDING

# 2. Get detailed error
$ gcloud app operations describe 2418243c-beac-4c8e-8cd7-b79ba03ae6c9 --project=dancedeets-hrd
done: true
error:
  code: 9
  message: |
    ModuleNotFoundError: No module named 'mapreduce'
    File "/app/dancedeets/users/users.py", line 7, in <module>
        from mapreduce import context

# 3. Fix the issue
# Create compatibility stub at /server/mapreduce/__init__.py

# 4. Redeploy
$ gcloud app deploy app.yaml --project=dancedeets-hrd --quiet

# 5. Verify success
$ gcloud app versions list --project=dancedeets-hrd
SERVICE  VERSION          SERVING_STATUS  INSTANCES
default  20251123t223905  SERVING         2
```
