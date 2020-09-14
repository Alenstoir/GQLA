import setuptools

with open('VERSION', 'r') as verfile:
    version = verfile.read()

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="gqla",
    version=version,
    author="Alexey Kuzin",
    author_email="alenstoir@yandex.ru",
    description="A module used to generate querry statements and perform data fetching via GraphQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alenstoir/GQLA",
    license='MIT License',
    requires='aiohttp',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
