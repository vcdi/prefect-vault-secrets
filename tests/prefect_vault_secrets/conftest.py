import pytest
import tempfile
import os

from prefect.utilities import configuration


@pytest.fixture()
def server_api():
    """
    backend settings don't seem to be getting respected.  As a work-around
    set export PREFECT__BACKEND=server where running the tests to enforce
    use of the server endpoint
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = os.path.join(tmp, ".prefect")
        os.makedirs(tmp)
        with configuration.set_temporary_config({
                "home_dir": tmp,
                "backend": "server",
                "cloud.api": "https:/localhost:4200",
                "cloud.auth_token": "secret_token",
                "cloud.use_local_secrets": False}):
            yield
