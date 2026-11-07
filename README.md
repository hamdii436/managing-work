# Planning and tracking your work with GitHub Projects and Issues

## Abstractttt

Learn how GitHub Issues and project planning capabilities balance structure and flexibility for complex software development. Get hands-on with the redesigned GitHub Issues experience and other enhancements and discover practical techniques for leveraging markdown-based issue templates and custom sections that adapt to your team's unique workflows. Perfect for developers and DevOps practitioners seeking to streamline collaboration without sacrificing visibility or accountability.

## Background 

This lab was created to support Microsoft Build 2025. A version for general public use will be published in a future release.

## Requirements

Currently, this lab requires the environment provided at Microsoft Build 2025.  In the future is should be available for use any GitHub organization.

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

@chrisreddington @dmckinstry

## Support

Please refer to the SUPPORT.md file for details.

## Hourly AI music and YouTube prototype

The optional `automation/` package generates a music-generation prompt and YouTube
metadata with Gemini Pro, sends the prompt to an external music-generation API, renders
the returned audio as an MP4 with ffmpeg, and can upload the video, add it to a playlist,
and measure a sequential two-title experiment.

**Gemini generates text, not music or images.** The thumbnail prompt is metadata only;
an image must be supplied with `CONTENT_IMAGE_PATH`, and an optional already-generated
thumbnail image can be supplied with `THUMBNAIL_IMAGE_PATH`. This scaffold does not
generate audio or assert that any generated track is cleared for commercial use. Review
the chosen music provider's terms, output, and licensing before publication.

### Setup

1. Install the project dependencies (`requests` and `python-dotenv` are already listed
   in `requirements.txt`) and install ffmpeg separately.
2. Copy `.env.example` to `.env`. Fill in `GEMINI_API_KEY`, choose `MUSIC_GENRE`,
   optionally add a YouTube Data API key (`YOUTUBE_API_KEY`, for keyword discovery), and
   `CONTENT_IMAGE_PATH`. Keep real credentials out of source control.
3. Configure `MUSIC_API_URL` and, if required, `MUSIC_API_TOKEN` for a music provider.
   No vendor is selected or bundled. The adapter expects `POST {MUSIC_API_URL}/jobs`
   with `{"prompt":"..."}` and a JSON response `{"id":"job-id"}`; it polls
   `GET {MUSIC_API_URL}/jobs/{job-id}` until `{"status":"completed","audio_url":"https://..."}`.
   `running`, `failed`, and `cancelled` statuses are supported. Adapt this boundary to the
   provider's real authentication, request, polling, and output format. The provider must
   grant permission to download the resulting audio. `MUSIC_POLL_INTERVAL_SECONDS` and
   `MUSIC_JOB_TIMEOUT_SECONDS` control polling.
4. To upload, configure a Google OAuth **user** client ID, secret, and refresh token in
   `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN`. Authorize
   the channel owner with the YouTube Data API upload and playlist scopes and the
   YouTube Analytics read-only scope for title experiments. Service-account upload is
   not assumed or supported. In Google Cloud, enable YouTube Data API v3 and YouTube
   Analytics API, create an OAuth client, and obtain an offline refresh token for the
   channel owner with scopes `youtube.upload`, `youtube.force-ssl`, and
   `yt-analytics.readonly`. Store the refresh token only in the local `.env`. Set
   `YOUTUBE_PLAYLIST_ID` if desired.

### Run

Run one pipeline cycle:

```powershell
python scripts/run_hourly_pipeline.py --once
```

Set `SCHEDULER_ENABLED=true` and run the same script without `--once` to process one
cycle per wall-clock hour. The default daily content limit is 8; `DAILY_CONTENT_LIMIT`
is configurable from 1 to 10 per UTC day. The cap applies to generated/rendered content
even when publishing is disabled. The local SQLite database atomically reserves slots,
so concurrent scheduler processes cannot exceed the cap. A per-hour record prevents
rerunning a completed slot. Known generation failures are marked retryable. If the
process stops abruptly during generation, inspect local artifacts and the database
before reconciling the slot. If an upload is interrupted before YouTube returns the
video ID, or a request fails ambiguously, that slot remains reserved; check the channel
and reconcile it before retrying to avoid duplicate uploads.

Uploads are opt-in: publishing is off unless `PUBLISH_ENABLED=true`. When enabled,
`YOUTUBE_PRIVACY_STATUS` defaults to `private`; use `unlisted` or `public` only after
review and configuration. Publishing requires user OAuth credentials and a working
music API and ffmpeg installation. Keep the scheduler process and its SQLite file
persistent; the daily cap and de-duplication state live in that file.

### Keyword discovery and title experiments

When `YOUTUBE_API_KEY` is configured, the prototype searches recent (seven-day),
high-view YouTube videos for the selected genre and extracts recurring title terms.
These are only YouTube search-result discovery signals, not measured search-volume data
or a guarantee of what is trending. Without that key the pipeline continues with no
discovery terms. Gemini uses any discovered terms as optional context for tags and SEO
keywords; review generated metadata for accuracy and relevance.

YouTube does not provide a native title A/B endpoint in this scaffold, and the standard
YouTube Analytics API does not expose thumbnail/title impression click-through rate.
The prototype applies the first title, waits `TITLE_TEST_HOURS` (24 or a larger multiple
of 24), changes to the alternate title, and records views, estimated minutes watched,
average view duration, and likes through Analytics. Tests are aligned to full UTC calendar
days; the first measurement begins at the next UTC midnight after upload, and each
variant switch is aligned to the current UTC day. The configured period must be at least
one full day. The higher-view title is
selected only if both periods reach `TITLE_TEST_MIN_VIEWS` (100 by default); otherwise
the test is marked insufficient and the original title is restored. This compares
sequential periods, not randomized or simultaneous audiences, and views are not
impressions-normalized click-through rates. Audience changes and Analytics reporting
delays can bias results.

The prototype requires network access and valid Gemini/music/Google credentials for an
end-to-end run. Unit tests use local fakes and do not upload, call paid services, or
require credentials:

```powershell
pytest tests/test_music_automation.py -q
```
