import logging
import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
project_path = here
src_path = os.path.join(project_path, "src")
readme_path = os.path.join(project_path, "README.md")

sys.path.insert(0, src_path)

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def read_file(path):
    with open(path, "r") as fp:
        return fp.read()


def install_requires():
    requirements = read_file(os.path.join(project_path, "requirements.txt")).split("\n")
    requirements = list(filter(lambda s: not not s, map(lambda s: s.strip(), requirements)))

    return requirements


def main():
    import grapejuice.__about__ as __about__
    from grapejuice_packaging.local_install import InstallLocally

    setup(
        version=__about__.package_version,
        license=__about__.package_license,
        long_description=read_file(readme_path),
        long_description_content_type="text/markdown",
        readme=read_file(readme_path),
        url=__about__.package_repository,
        packages=find_packages("src", exclude=[
            "grapejuice_packaging",
            "grapejuice_packaging.*",
            "grapejuice_dev_tools",
            "grapejuice_dev_tools.*",
            "tests",
            "tests.*"
        ]),
        package_dir={"": "src"},
        include_package_data=True,
        install_requires=install_requires(),
        cmdclass={
            "install_locally": InstallLocally
        }
    )


if __name__ == '__main__':
    main()
