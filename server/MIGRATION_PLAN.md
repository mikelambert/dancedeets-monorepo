# MapReduce/Pipeline Migration Plan

This document outlines the migration from legacy App Engine MapReduce/Pipeline to modern Google Cloud services.

## Migration Progress

| Phase | Status | Jobs Migrated |
|-------|--------|---------------|
| Phase 1: Infrastructure | ✅ COMPLETE | Framework, Dockerfile, requirements |
| Phase 2: Simple Mapper Jobs | ✅ COMPLETE | 6/6 jobs |
| Phase 3: GCS Output Jobs | ✅ COMPLETE | 5/5 jobs |
| Phase 4: MapReduce Pipeline Jobs | ✅ COMPLETE | 3/4 jobs (find_access_tokens pending) |
| Phase 5: Cloud Workflows | ✅ COMPLETE | 1 workflow + 3 jobs |
| Phase 6: Code Cleanup | ✅ COMPLETE | Old mapreduce code removed |

## Cleanup Completed

The following original files have been cleaned up to remove mapreduce/pipeline code:

**Files modified (old mapreduce code removed, core functions retained):**
- `notifications/added_events.py` - Kept `promote_events_to_user()`, removed mapreduce handler
- `sitemaps/events.py` - Kept `generate_sitemap_entry()`, removed mapreduce handler
- `ml/gprediction.py` - Kept `predict()`, `get_predict_service()`, removed MR wrappers
- `users/user_event_tasks.py` - Kept `update_user_qualities()`, removed mapreduce handler
- `users/user_tasks.py` - Kept `fetch_and_save_fb_user()`, removed mapreduce handler
- `search/email_events.py` - Kept `email_for_user()`, removed mapreduce wrapper
- `pubsub/pubsub_tasks.py` - Kept social handlers, removed `PostJapanEventsHandler` MR code
- `rankings/rankings.py` - Kept utility functions, removed all mapreduce code
- `event_scraper/auto_add.py` - Kept classification logic, removed MR wrappers (added optional `metrics` param)
- `event_scraper/thing_db.py` - Kept Source model and helpers, removed MR pipeline code
- `event_scraper/thing_scraper2.py` - Replaced with deprecation stub
- `classes/class_pipeline.py` - Replaced with deprecation stub

**Files deleted (fully migrated to Cloud Run Jobs):**
- `logic/mr_dump.py` → `jobs/dump_potential_events.py`
- `logic/unique_attendees.py` → `jobs/count_unique_attendees.py`
- `ml/mr_prediction.py` → `jobs/classify_events_ml.py`

**Compat layer status:**
- `compat/` directory retained with `LEGACY_APIS_ENABLED = False`
- Provides stub implementations for imports that still reference mapreduce utilities
- `json_util.JsonProperty` still used by Source model
- Can be removed in future cleanup after all references are updated

### New Files Created

**Framework (`server/dancedeets/jobs/`):**
- `__init__.py` - Module exports
- `base.py` - Job, BatchJob, JobRunner classes
- `fb_utils.py` - Facebook API token handling
- `metrics.py` - JobMetrics, GroupedMetrics
- `gcs_output.py` - GCSOutputWriter
- `runner.py` - CLI entry point

**Phase 2 Jobs:**
- `notify_users.py` - Push notifications by timezone
- `post_japan_events.py` - Post Japan events to social
- `compute_rankings.py` - City/country rankings
- `compute_user_stats.py` - User event statistics
- `refresh_users.py` - Refresh Facebook profiles
- `send_weekly_emails.py` - Weekly digest emails

**Phase 3 Jobs:**
- `generate_sitemaps.py` - XML sitemap generation
- `dump_potential_events.py` - Export to CSV
- `generate_training_data.py` - ML training data
- `classify_events_ml.py` - ML classification
- `auto_add_events.py` - Auto-add dance events

**Phase 4 Jobs:**
- `count_unique_attendees.py` - Unique RSVPs by city
- `update_source_stats.py` - Source quality metrics
- `scrape_and_classify.py` - Scrape and classify events

**Phase 5 (Cloud Workflows):**
- `workflows/crawl_and_index_classes.yaml` - Orchestration workflow
- `start_spiders.py` - Start ScrapingHub spiders
- `reindex_classes.py` - Rebuild class search index
- `email_crawl_errors.py` - Send error reports

**Docker/Config:**
- `Dockerfile.jobs` - Cloud Run Jobs container
- `requirements-jobs.txt` - Job dependencies

---

## Migration Strategy

| Legacy Pattern | Modern Replacement |
|----------------|-------------------|
| `start_map()` (mapper only) | **Cloud Run Jobs** |
| `MapreducePipeline` (map+reduce) | **Cloud Run Jobs** (simple) or **Cloud Dataflow** (complex) |
| `Pipeline` orchestration | **Cloud Workflows** |
| Task Queues | **Cloud Tasks** (already compatible) |

---

## Phase 1: Infrastructure Setup

### Task 1.1: Create Cloud Run Job Base Image
- **File to create**: `server/cloud_run/Dockerfile.jobs`
- **Purpose**: Base Docker image for all batch jobs
- **Contents**: Python runtime, common dependencies, Datastore client, GCS client
- **Priority**: HIGH (blocking for all other migrations)

### Task 1.2: Create Job Runner Framework
- **File to create**: `server/dancedeets/jobs/base.py`
- **Purpose**: Base class for Cloud Run Jobs replacing mapreduce patterns
- **Features needed**:
  - Datastore entity iteration with cursor-based pagination
  - Parallel task execution (Cloud Run Jobs supports up to 10,000 parallel tasks)
  - Counter/metrics collection
  - GCS output writer
  - Facebook API token injection (port from `fb_mapreduce.py`)

### Task 1.3: Create Cloud Workflows Templates
- **File to create**: `server/workflows/`
- **Purpose**: YAML workflow definitions for orchestrated jobs
- **Priority**: MEDIUM (only needed for Pipeline migrations)

---

## Phase 2: Simple Mapper Jobs → Cloud Run Jobs

These jobs iterate over entities and perform side effects (no reduce step, no GCS output).

### Task 2.1: `notifications/added_events.py`
- **Current**: `promote_events_to_user` via `start_map()`
- **Entity**: `User` (filtered by timezone_offset)
- **Action**: Sends push notifications for new events
- **Migration**:
  1. Create `server/dancedeets/jobs/notify_users.py`
  2. Query users by timezone offset
  3. For each user: search events, create Android push notification
  4. Schedule via Cloud Scheduler (hourly, matching current cron)
- **Complexity**: LOW
- **Facebook API**: No

### Task 2.2: `pubsub/pubsub_tasks.py`
- **Current**: `map_post_jp_event` via `start_map()`
- **Entity**: `DBEvent` (filtered by TIME_FUTURE)
- **Action**: Posts Japan events to social media
- **Migration**:
  1. Create `server/dancedeets/jobs/post_japan_events.py`
  2. Query future events ending with 'Japan'
  3. Post to Twitter/social via pubsub module
- **Complexity**: LOW
- **Facebook API**: No

### Task 2.3: `rankings/rankings.py`
- **Current**: `count_event_for_city`, `count_user_for_city` via `start_map()`
- **Entity**: `DBEvent` or `User`
- **Action**: Counts events/users by city, stores in counters
- **Migration**:
  1. Create `server/dancedeets/jobs/compute_rankings.py`
  2. Use in-memory counters (dict) instead of mapreduce counters
  3. Query entities, increment counters by city/country
  4. Call `_compute_summary()` at job end
- **Complexity**: LOW
- **Facebook API**: No

### Task 2.4: `users/user_event_tasks.py`
- **Current**: `map_compute_user_stats` via `start_map()`
- **Entity**: `User`
- **Action**: Computes event statistics per user
- **Migration**:
  1. Create `server/dancedeets/jobs/compute_user_stats.py`
  2. Query all users
  3. For each: query PotentialEvent by source_ids, count by creating_method
  4. Update user properties
- **Complexity**: LOW
- **Facebook API**: No

### Task 2.5: `users/user_tasks.py`
- **Current**: `map_load_fb_user` via `start_map()`
- **Entity**: `User` (optionally filtered by expired_oauth_token)
- **Action**: Refreshes user profile from Facebook
- **Migration**:
  1. Create `server/dancedeets/jobs/refresh_users.py`
  2. Query users (optionally skip expired tokens)
  3. For each: fetch LookupUser from FB, update Mailchimp, compute_derived_properties()
  4. Handle ExpiredOAuthToken exceptions
- **Complexity**: MEDIUM
- **Facebook API**: Yes (needs token handling)

### Task 2.6: `search/email_events.py`
- **Current**: `map_email_user` via `start_map()`
- **Entity**: `User`
- **Action**: Sends weekly event digest emails
- **Migration**:
  1. Create `server/dancedeets/jobs/send_weekly_emails.py`
  2. Query all users
  3. For each: search events, render HTML via render_server, send via Mandrill
  4. Update user.weekly_email_send_date
  5. Handle NoEmailException, ExpiredOAuthToken
- **Complexity**: MEDIUM
- **Facebook API**: Yes (needs token handling)

---

## Phase 3: Mapper Jobs with GCS Output → Cloud Run Jobs

These jobs iterate and write results to Google Cloud Storage.

### Task 3.1: `sitemaps/events.py`
- **Current**: `map_sitemap_event` via `start_map()` with output writer
- **Entity**: `DBEvent` (filtered by vertical, time_period)
- **Output**: XML sitemap to GCS
- **Migration**:
  1. Create `server/dancedeets/jobs/generate_sitemaps.py`
  2. Query events by filters
  3. Generate XML entries with lxml
  4. Write to GCS using google-cloud-storage client
  5. Handle file splitting if needed (sitemaps have size limits)
- **Complexity**: MEDIUM
- **Facebook API**: No

### Task 3.2: `logic/mr_dump.py`
- **Current**: `map_dump_fb_json` via `start_map()` with output writer
- **Entity**: `PotentialEvent` (filtered by looked_at=None)
- **Output**: CSV to GCS
- **Migration**:
  1. Create `server/dancedeets/jobs/dump_potential_events.py`
  2. Query PotentialEvents not yet looked at
  3. Batch fetch from Facebook API
  4. Write CSV rows to GCS
- **Complexity**: MEDIUM
- **Facebook API**: Yes (batch_fetch)

### Task 3.3: `ml/gprediction.py`
- **Current**: `map_training_data_for_pevents` via `start_map()` with output writer
- **Entity**: `PotentialEvent`
- **Output**: ML training data CSV to GCS
- **Migration**:
  1. Create `server/dancedeets/jobs/generate_training_data.py`
  2. Query PotentialEvents
  3. Fetch event details and attending from Facebook
  4. Extract training features
  5. Write to GCS
- **Complexity**: MEDIUM
- **Facebook API**: Yes

### Task 3.4: `ml/mr_prediction.py`
- **Current**: `map_classify_events` via `start_map()` with output writer
- **Entity**: `PotentialEvent` (filtered by looked_at=None)
- **Output**: Classification results to GCS
- **Migration**:
  1. Create `server/dancedeets/jobs/classify_events_ml.py`
  2. Query unprocessed PotentialEvents
  3. Batch Facebook API requests
  4. Call Google Prediction API
  5. Write results to GCS
- **Complexity**: HIGH (ML service integration)
- **Facebook API**: Yes

### Task 3.5: `event_scraper/auto_add.py`
- **Current**: `map_classify_events` via `start_map()` with output writer
- **Entity**: `PotentialEvent` (filtered by should_look_at, past_event)
- **Action**: Auto-adds dance events, writes results to GCS
- **Migration**:
  1. Create `server/dancedeets/jobs/auto_add_events.py`
  2. Query PotentialEvents matching criteria
  3. Run NLP classifier, attendee classifier
  4. Create DBEvent via add_entities.add_update_fb_event()
  5. Update PotentialEvent.looked_at, auto_looked_at
  6. Write summary to GCS
- **Complexity**: HIGH (multiple classifiers, entity creation)
- **Facebook API**: Yes

---

## Phase 4: MapReduce Pipeline Jobs → Cloud Run Jobs or Dataflow

These have both map and reduce steps.

### Task 4.1: `logic/unique_attendees.py`
- **Current**: `MapreducePipeline` with mapper + reducer
- **Map**: Emits (city, attendee_id) from each event
- **Reduce**: Counts unique attendees per city
- **Migration Options**:
  - **Option A (Cloud Run Jobs)**: Single job with in-memory aggregation
    1. Create `server/dancedeets/jobs/count_unique_attendees.py`
    2. Query all FB events
    3. Use `dict[city, set[attendee_id]]` for uniqueness
    4. Write final counts to GCS
  - **Option B (Cloud Dataflow)**: Apache Beam pipeline (if scale demands)
- **Complexity**: MEDIUM
- **Facebook API**: Yes (batch_fetch for attending)

### Task 4.2: `event_scraper/thing_db.py`
- **Current**: `MapreducePipeline` - counts events per source
- **Map**: `explode_per_source_count` - emits counts per source
- **Reduce**: `combine_source_count` - sums and updates Source entities
- **Migration**:
  1. Create `server/dancedeets/jobs/update_source_stats.py`
  2. Query all PotentialEvents
  3. Aggregate counts by source_id in memory
  4. Batch update Source entities
- **Complexity**: MEDIUM
- **Facebook API**: Yes

### Task 4.3: `event_scraper/thing_scraper2.py`
- **Current**: `MapreducePipeline` - scrapes sources then processes events
- **Map**: `scrape_sources_for_events` - discovers events from sources
- **Reduce**: `process_events` - classifies discovered events
- **Migration**:
  1. Create `server/dancedeets/jobs/scrape_and_classify.py`
  2. Query all Sources (filtered by min_potential_events)
  3. Scrape each source for events
  4. Process through event_pipeline.process_discovered_events()
- **Complexity**: HIGH (multi-stage, external scraping)
- **Facebook API**: Yes

### Task 4.4: `events/find_access_tokens.py`
- **Current**: Complex multi-stage `MapreducePipeline`
- **Stages**: Find events → Combine → Find tokens → Save
- **Migration**:
  1. This is best migrated to **Cloud Workflows** orchestrating multiple Cloud Run Jobs
  2. Create workflow: `server/workflows/find_access_tokens.yaml`
  3. Create jobs:
     - `server/dancedeets/jobs/find_events_needing_tokens.py`
     - `server/dancedeets/jobs/test_user_tokens.py`
     - `server/dancedeets/jobs/save_valid_tokens.py`
  4. Workflow coordinates: job1 → job2 → job3
- **Complexity**: HIGH (multi-stage orchestration)
- **Facebook API**: Yes

---

## Phase 5: Custom Pipeline Jobs → Cloud Workflows

### Task 5.1: `classes/class_pipeline.py`
- **Current**: `CrawlAndIndexClassesJob` Pipeline with 4 stages
- **Stages**:
  1. `start_spiders` - Triggers ScrapingHub spiders
  2. `WaitForJobs` - Polls for completion (30s retries)
  3. `ReindexClasses` - Rebuilds class search index
  4. `EmailErrors` - Sends error report via Mandrill
- **Migration**:
  1. Create workflow: `server/workflows/crawl_and_index_classes.yaml`
  2. Create Cloud Run Jobs:
     - `server/dancedeets/jobs/start_spiders.py`
     - `server/dancedeets/jobs/reindex_classes.py`
     - `server/dancedeets/jobs/email_crawl_errors.py`
  3. Use Cloud Workflows built-in retry/polling for WaitForJobs
  4. Wire up: start_spiders → poll_completion → reindex → email_errors
- **Complexity**: MEDIUM (mostly orchestration)
- **Facebook API**: No

---

## Phase 6: Utility Module Updates

### Task 6.1: Port `util/fb_mapreduce.py`
- **Current**: Facebook token injection for mapreduce
- **New**: `server/dancedeets/jobs/fb_utils.py`
- **Features to port**:
  - `get_fblookup()` - Get FBLookup with access token
  - `get_multiple_tokens()` - Token rotation for long jobs
  - Batch Facebook API request handling

### Task 6.2: Port `util/mr.py`
- **Current**: Counter utilities for mapreduce
- **New**: `server/dancedeets/jobs/metrics.py`
- **Features**:
  - In-memory counter implementation
  - Optional Cloud Monitoring integration

### Task 6.3: Deprecate Compatibility Layer
- **Files**: `server/dancedeets/compat/mapreduce/`, `server/dancedeets/compat/pipeline/`
- **Action**: Once all jobs migrated, remove compat layer entirely

---

## Phase 7: Configuration & Deployment

### Task 7.1: Update `queue.yaml` → Cloud Tasks
- Migrate queue definitions to Cloud Tasks API
- Update queue references in job code

### Task 7.2: Create Cloud Run Job Definitions
- **File**: `server/cloudbuild.yaml` or Terraform configs
- Define all Cloud Run Jobs with resource limits

### Task 7.3: Create Cloud Scheduler Triggers
- Replace App Engine cron with Cloud Scheduler
- Schedule all periodic jobs

### Task 7.4: Create Cloud Workflows Definitions
- Deploy workflow YAML files
- Set up workflow triggers

### Task 7.5: Update `batch.yaml`
- Either remove (if batch service no longer needed) or update for Cloud Run

---

## File-by-File Migration Checklist

| File | Current Pattern | Target | Priority | Complexity | FB API |
|------|-----------------|--------|----------|------------|--------|
| `notifications/added_events.py` | start_map | Cloud Run Job | HIGH | LOW | No |
| `pubsub/pubsub_tasks.py` | start_map | Cloud Run Job | MEDIUM | LOW | No |
| `rankings/rankings.py` | start_map | Cloud Run Job | MEDIUM | LOW | No |
| `users/user_event_tasks.py` | start_map | Cloud Run Job | MEDIUM | LOW | No |
| `users/user_tasks.py` | start_map | Cloud Run Job | MEDIUM | MEDIUM | Yes |
| `search/email_events.py` | start_map | Cloud Run Job | MEDIUM | MEDIUM | Yes |
| `sitemaps/events.py` | start_map+output | Cloud Run Job | HIGH | MEDIUM | No |
| `logic/mr_dump.py` | start_map+output | Cloud Run Job | LOW | MEDIUM | Yes |
| `ml/gprediction.py` | start_map+output | Cloud Run Job | LOW | MEDIUM | Yes |
| `ml/mr_prediction.py` | start_map+output | Cloud Run Job | LOW | HIGH | Yes |
| `event_scraper/auto_add.py` | start_map+output | Cloud Run Job | HIGH | HIGH | Yes |
| `logic/unique_attendees.py` | MapreducePipeline | Cloud Run Job | LOW | MEDIUM | Yes |
| `event_scraper/thing_db.py` | MapreducePipeline | Cloud Run Job | MEDIUM | MEDIUM | Yes |
| `event_scraper/thing_scraper2.py` | MapreducePipeline | Cloud Run Job | HIGH | HIGH | Yes |
| `events/find_access_tokens.py` | Multi-stage Pipeline | Cloud Workflows | LOW | HIGH | Yes |
| `classes/class_pipeline.py` | Custom Pipeline | Cloud Workflows | MEDIUM | MEDIUM | No |

---

## Recommended Migration Order

1. **Infrastructure** (Task 1.1-1.3) - Required first
2. **Simple side-effect jobs** (Task 2.1-2.4) - Quick wins, no FB API
3. **FB API jobs** (Task 2.5-2.6) - After FB token handling is ported
4. **GCS output jobs** (Task 3.1) - Sitemaps are user-facing
5. **Event processing jobs** (Task 3.5, 4.3) - Core functionality
6. **ML jobs** (Task 3.2-3.4) - Lower priority, complex
7. **Pipeline orchestration** (Task 5.1, 4.4) - After individual jobs work
8. **Cleanup** (Task 6.3, 7.x) - Final phase
