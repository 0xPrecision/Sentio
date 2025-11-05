import argparse
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--bot", default="your_bot")
    args = p.parse_args()
    print(f"https://t.me/{args.bot}?start=tn-{args.slug}")
if __name__ == "__main__":
    main()
