import hashlib
from dataclasses import dataclass
from pathlib import Path


class MigrationChecksumMismatch(RuntimeError):
    def __init__(self, version: str, expected: str, actual: str) -> None:
        super().__init__(f"migration {version} checksum changed: database={expected} file={actual}")
        self.version = version
        self.expected = expected
        self.actual = actual


@dataclass(frozen=True)
class MigrationFile:
    version: str
    path: Path
    checksum: str


@dataclass(frozen=True)
class MigrationPlan:
    to_apply: list[MigrationFile]
    skipped: list[MigrationFile]


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_migration_files(directory: Path) -> list[MigrationFile]:
    return [
        MigrationFile(version=path.name, path=path, checksum=calculate_sha256(path))
        for path in sorted(directory.glob("*.sql"), key=lambda item: item.name)
    ]


def plan_migrations(files: list[MigrationFile], applied: dict[str, str]) -> MigrationPlan:
    to_apply: list[MigrationFile] = []
    skipped: list[MigrationFile] = []
    for file in files:
        applied_checksum = applied.get(file.version)
        if applied_checksum is None:
            to_apply.append(file)
        elif applied_checksum != file.checksum:
            raise MigrationChecksumMismatch(file.version, applied_checksum, file.checksum)
        else:
            skipped.append(file)
    return MigrationPlan(to_apply=to_apply, skipped=skipped)

