import argparse
from prepare_dataset import prepare_dataset


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("class_name", type=str, help="Classname for product training")

    args = parser.parse_args()

    prepare_dataset(args.class_name)


if __name__ == "__main__":
    main()
