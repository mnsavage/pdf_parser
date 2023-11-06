import argparse


def main():
    arg_parser = argparse.ArgumentParser(description="Process some parameters.")
    arg_parser.add_argument("storage", help="where the encoded pdf is stored")
    arg_parser.add_argument("UUID", help="unique id")
    args = arg_parser.parse_args()

    print(f"storage: {args.storage}, UUID: {args.UUID}")


if __name__ == "__main__":
    main()
