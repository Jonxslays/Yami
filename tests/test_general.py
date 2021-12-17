import yami


def test_version() -> None:
    with open("pyproject.toml") as f:
        for line in f:
            if "=" in line:
                k, v = line.split(" = ")

                if k == "version":
                    assert yami.__version__ == v.strip("\"\n")
                    return None

    raise RuntimeError("Wheres the version?")
