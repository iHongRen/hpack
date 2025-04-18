import argparse

def packBefore():
    print("packBefore")


def packAfter():
    print("packAfter")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PackFile script")
    parser.add_argument('--desc', type=str, help="Description parameter")
    parser.add_argument('--before', action='store_true', help="Execute packBefore")
    parser.add_argument('--after', action='store_true', help="Execute packAfter")
    args = parser.parse_args()

    if args.before:
        packBefore()
    elif args.after:
        packAfter()
    else:
        print("No valid action specified.")
