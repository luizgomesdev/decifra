"""The settings file must work in a checkout and inside the container."""

from pathlib import Path

from decifra.config import repo_root


def test_checkout_layout_points_at_the_repository():
    config_file = Path("/home/dev/decifra/apps/api/src/decifra/config.py")

    assert repo_root(config_file) == Path("/home/dev/decifra")


def test_container_layout_points_at_the_app_folder():
    config_file = Path("/app/src/decifra/config.py")

    assert repo_root(config_file) == Path("/app")
