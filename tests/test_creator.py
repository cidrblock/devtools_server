import requests
import tarfile
from pathlib import Path


def test_error(server: str) -> None:
    """Test the error response."""
    response = requests.post(f"{server}/v1/creator/playbook")
    assert response.status_code == 400
    assert response.text == "Missing required request body"


def test_playbook_v1(server: str, tmp_path: Path) -> None:
    """Test the playbook creation."""
    response = requests.post(
        f"{server}/v1/creator/playbook",
        json={
            "project": "ansible-project",
            "scm_org": "ansible",
            "scm_project": "devops",
        },
    )
    assert response.status_code == 201
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="ansible-devops.tar.gz"'
    )
    assert response.headers["Content-Type"] == "application/tar+gzip"
    dest_file = tmp_path / "ansible-devops.tar.gz"
    with open(dest_file, "wb") as tar_file:
        tar_file.write(response.content)
    file = tarfile.open(dest_file)
    assert (
        "./collections/ansible_collections/ansible/devops/roles/run/README.md"
        in file.getnames()
    )


def test_collection_v1(server: str, tmp_path: Path) -> None:
    """Test the collection creation."""
    response = requests.post(
        f"{server}/v1/creator/collection",
        json={
            "collection": "namespace.name",
            "project": "collection",
        },
    )
    assert response.status_code == 201
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="namespace.name.tar.gz"'
    )
    assert response.headers["Content-Type"] == "application/tar+gzip"
    dest_file = tmp_path / "namespace.name.tar.gz"
    with open(dest_file, "wb") as tar_file:
        tar_file.write(response.content)
    file = tarfile.open(dest_file)
    assert "./roles/run/tasks/main.yml" in file.getnames()
