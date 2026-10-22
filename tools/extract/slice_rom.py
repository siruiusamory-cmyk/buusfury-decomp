import sys


def main(argv):
    image, start_text, end_text = argv[0], argv[1], argv[2]
    start, end = int(start_text, 0), int(end_text, 0)
    if start < 0 or end < start:
        print("bad range %s..%s" % (start_text, end_text))
        return 1
    with open(image, "rb") as handle:
        handle.seek(start)
        data = handle.read(end - start)
    if len(data) != end - start:
        print("short read: %d of %d bytes" % (len(data), end - start))
        return 1
    name = "%s_%s_%s.extracted" % (image, start_text, end_text)
    with open(name, "wb") as handle:
        handle.write(data)
    print("extracted %s (%d bytes)" % (name, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
