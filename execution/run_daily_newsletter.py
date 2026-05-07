import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS = [
    BASE_DIR / 'execution' / 'fetch_news.py',
    BASE_DIR / 'execution' / 'generate_newsletter.py',
    BASE_DIR / 'execution' / 'send_newsletter.py',
]


def run(script):
    print(f"\n[{script.name}]")
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(f"FEJL:\n{result.stderr.strip()}")
        raise RuntimeError(f"{script.name} fejlede med kode {result.returncode}")


def main():
    print("Starter dagligt nyhedsbrev...")
    for script in SCRIPTS:
        run(script)
    print("\nNyhedsbrev sendt!")


if __name__ == '__main__':
    main()
