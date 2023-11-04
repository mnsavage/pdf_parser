import argparse


def main():
    arg_parser = argparse.ArgumentParser(description="Process some parameters.")
    arg_parser.add_argument("dynamoDB", help="database")
    arg_parser.add_argument("UUID", help="unique id")
    arg_parser.add_argument("pdf", help="pdf file to parse")
    args = arg_parser.parse_args()

    print(f"dynamoDB: {args.dynamoDB}, UUID: {args.UUID}, pdf: {args.pdf}")


if __name__ == "__main__":
    main()
