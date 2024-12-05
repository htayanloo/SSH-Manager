from autossh.parser import Parser


def main():
    parser = Parser()
    parser.process_and_save()

if __name__ == "__main__":
    main()
