from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    print(f"Hello from migr! {PROJECT_ROOT=}")
