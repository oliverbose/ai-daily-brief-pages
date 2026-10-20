# Daily AI Brief — public episode delivery

Candidate feed: https://oliverbose.github.io/ai-daily-brief-pages/feed.xml

This repository holds a minimal manual migration workflow for testing GitHub Pages audio delivery. It copies the latest three real editions from the current public feed, preserves their audio bytes and GUIDs, and excludes the test episode. It does not generate speech or run on a daily schedule.

Audio is held only in the deployed Pages site and the normal one-day deployment artifact. MP3 files are never committed. The private application and narration inbox remain private; this trial requires no source credential or OpenAI key.

Run **Pages playback trial** manually from Actions. Playback and seeking must be verified at the Pages URL and on Playrun/Garmin before production transfer. Netlify remains the working publisher during this trial.
