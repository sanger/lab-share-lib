from setuptools import find_packages, setup  # type: ignore

setup(
    name="lab_share_lib",
    packages=find_packages(include=["lab_share_lib"]),
    version="0.1.0",
    description="Library to allow creating consumers to interact with lab-share framework",
    author="Stuart McHattie",
    license="MIT",
    install_requires=["pika", "fastavro~=1.5", "requests"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
)
