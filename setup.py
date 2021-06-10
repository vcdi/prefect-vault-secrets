from setuptools import setup, find_packages

package_name = "prefect-vault-secrets"
description = "Prefect secrets from Hashicorp Vault"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=package_name,
    use_scm_version=True,
    author="VCDI Platform Tech",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vcdi/prefect-vault-secrets",
    license="BSD 3 license",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "hvac>=0.10",
        "prefect>=0.13"
    ]
)
