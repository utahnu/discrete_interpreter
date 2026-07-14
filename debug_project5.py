import sys  # noqa

sys.argv = ["project", "arg1"]

from project.project import projectcli  # noqa

if __name__ == "__main__":
    projectcli()
