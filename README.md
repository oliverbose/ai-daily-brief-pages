# Daily AI Brief public publisher

Feed: https://oliverbose.github.io/ai-daily-brief-pages/feed.xml

This repository owns the sole production workflow. The application and narration inbox remain in the private source repository. Only the complete verified three-episode site is uploaded to Pages. No transcripts, private application files, credentials or speech chunks are public artifacts. MP3s are never committed.

The workflow is gated by `PUBLISHING_ENABLED=true`. Configure `PRIVATE_SOURCE_READ_TOKEN` (fine-grained access to the private source repository, Contents: read only) and `OPENAI_API_KEY` as encrypted Actions secrets. The application checkout is pinned to a reviewed commit; the day's input checkout is independently pinned when fetched. Keep the migration trial workflow retired when activating production.

One timezone-aware schedule runs at 08:30 Europe/Berlin. Pushes do not publish. Use manual dispatch for late narration or recovery, with a reason. A historical report also requires `historical=true`. To reuse a completed deployment artifact, supply its `recovery_run_id`; speech is not called. Without an artifact, explicitly select `allow_regeneration` because paid work may repeat. Artifacts have one-day retention and are not backups.

Latest three successful report dates are retained; older enclosure links can stop working. Check GitHub failure notifications and workflow runs. Public repository schedules may be disabled after 60 days without repository activity. There is no independent watchdog. Playrun Playlist insertion remains manual; verify Garmin synchronization separately.
