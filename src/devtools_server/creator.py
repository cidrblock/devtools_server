"""The creator wrapper."""

from __future__ import annotations

import tarfile

from typing import TYPE_CHECKING

from ansible_creator._version import version as creator_version
from ansible_creator.config import Config
from ansible_creator.output import Output
from ansible_creator.subcommands.init import Init
from ansible_creator.utils import TermFeatures


if TYPE_CHECKING:
    from pathlib import Path


class CreatorOutput(Output):
    """The creator output."""

    def __init__(self: CreatorOutput, log_file: str) -> None:
        """Initialize the creator output.

        Args:
            log_file: The log file path
        """
        super().__init__(
            log_file=log_file,
            log_level="DEBUG",
            log_append="false",
            term_features=TermFeatures(color=False, links=False),
            verbosity=1,
        )


class Creator:
    """The creator wrapper."""

    def __init__(self: Creator, tmp_dir: Path) -> None:
        """Initialize the creator.

        Args:
            tmp_dir: The temporary directory
        """
        self.tmp_dir = tmp_dir

    def collection(self: Creator, collection: str) -> Path:
        """Scaffold a collection.

        Args:
            collection: The collection name
        Returns:
            Path: The tar file path
        """
        init_path = self.tmp_dir / collection
        config = Config(
            creator_version=creator_version,
            init_path=str(init_path),
            output=CreatorOutput(log_file=str(self.tmp_dir / "creator.log")),
            collection=collection,
            subcommand="init",
        )
        Init(config).run()
        tar_file = self.tmp_dir / f"{collection}.tar.gz"
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(str(init_path), arcname=".")
        return tar_file

    def playbook(self: Creator, project: str, scm_org: str, scm_project: str) -> Path:
        """Scaffold a playbook project.

        Args:
            project: The project type
            scm_org: The SCM organization
            scm_project: The SCM project
        Returns:
            Path: The tar file path
        """
        init_path = self.tmp_dir / f"{scm_org}-{scm_project}"
        config = Config(
            creator_version=creator_version,
            init_path=str(init_path),
            output=CreatorOutput(log_file=str(self.tmp_dir / "creator.log")),
            project=project,
            scm_org=scm_org,
            scm_project=scm_project,
            subcommand="init",
        )
        Init(config).run()
        tar_file = self.tmp_dir / f"{scm_org}-{scm_project}.tar.gz"
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(str(init_path), arcname=".")
        return tar_file
