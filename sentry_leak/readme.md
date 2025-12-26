Sentry‑Leak is a lightweight Python script that automatically checks bonjourlafuite.eu.org for new data leaks and sends desktop notifications (and optionally emails) when new entries are published.
It’s designed for personal monitoring and educational use, integrating cleanly with local tools such as:
	•	notifier.py → macOS notifications
	•	mailer.py → email alerts via Gmail SMTP
	•	cron → scheduled background checks

Requirements
	•	Python 3.10+
	•	Dependencies:
	 	•	```pip install beautifulsoup4 requests```
	 	•```brew install terminal-notifier```

Basic syntax : 

```bash
python3 Sentry-Leak.py [--to EMAIL]
```

Cron example (for automation)
```bash
0 */6 * * * /usr/bin/python3 /path/to/Sentry-Leak.py --to "you@example.com"
```

How it works
1.	Fetches the latest leaks from bonjourlafuite.eu.org
2.	Parses each entry’s title ( `<h2>` ), date ( `<span>` ), and details ( `<div class='timeline-description'>` )
3.	Compares them with a local JSON file ( fuites.json )
4.	If a new leak is found:<br>
        •	Sends a macOS notification via  notifier.py <br>
        •	Optionally sends an email via  mailer.py <br>
        •	Updates the local JSON cache<br>

Integration notes
To enable secure email alerts, configure mailer.py once with your Gmail App Password in macOS Keychain  
