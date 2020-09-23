from setuptools import setup, find_namespace_packages # type: ignore


def main():
    pkgs = find_namespace_packages('src')
    pkg = min(pkgs)
    return setup(
        name=pkg,
        zip_safe=False,
        packages=pkgs,
        package_dir={'': 'src'},
        package_data={pkg: ['py.typed']},

        install_requires=[
            'requests', # dependency of Hypothesis API
            # todo sadly, the API itself is not a python package, so checked it out as a submodule.. would be nice to convert?
        ],
        extras_require={
            'testing': ['pytest'],
            'linting': ['pytest', 'mypy'],
        },
    )


if __name__ == '__main__':
    main()
