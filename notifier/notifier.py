#!/usr/bin/env python3
import subprocess
import argparse
import re

def notify(title: str, subtitle: str, message: str) -> bool:
    """Notification macOS"""
    
    # Nettoyage français sécurisé
    title_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"\']', '', title)[:50]
    subtitle_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"\']', '', subtitle)[:50]
    message_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"\']', '', message)[:100]

    cmd = [
        '/opt/homebrew/bin/terminal-notifier',
        '-title', title_clean,
        '-subtitle', subtitle_clean,
        '-message', message_clean, 
        '-sound', 'Glass' 
    ]
    
    try:
        result = subprocess.run(cmd, check=True, timeout=10, capture_output=True, text=True)
        print(f"Notification: {title_clean}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur terminal-notifier: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("Timeout")
        return False

def main() -> int:
    parser = argparse.ArgumentParser(description='Notifications macOS')
    parser.add_argument('title', help='Titre')
    parser.add_argument('-s', '--subtitle', default='', help='Sous-titre')
    parser.add_argument('-m', '--message', required=True, help='Message')
    
    args = parser.parse_args()
    return 0 if notify(args.title, args.subtitle, args.message) else 1

if __name__ == '__main__':
    exit(main())
