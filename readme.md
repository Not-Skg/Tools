Simple example script showing how to send native macOS notifications using terminal‑notifier.
It serves as a utility component that I reuse in other projects such as Sentry‑Leak, automation scripts, or cron jobs.

Requirements
	•	macOS with Homebrew installed
	•	terminal-notifier

Usage

```bash
python3 notifier.py "Title" -s "Subtitle" -m "Message"
```