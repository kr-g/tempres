import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


def load_requirements():
    with open("requirements.txt") as f:
        lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = filter(lambda x: len(x) > 0, lines)
        lines = filter(lambda x: x[0] != "#", lines)
        return list(lines)


pyver = platform.python_version_tuple()[:2]
pyversion = ".".join(pyver)

file = os.path.join("tempres", "__init__.py")
version = find_version(file)
projectname = find_projectname()

setuptools.setup(
    name=projectname,
    version=version,
    author="k. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(),
    install_requires=load_requirements(),
    python_requires=f">={pyversion}",
)

# python3 -m setup sdist build bdist_wheel
# twine upload dist/*
