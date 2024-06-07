from setuptools import find_packages, setup  # type: ignore

setup(
    name="lab_share_lib",
    packages=find_packages(include=["lab_share_lib"]),
    version="1.0.1",
    description="Library to allow creating consumers to interact with lab-share framework",
    author="Stuart McHattie",
    license="MIT",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
)
