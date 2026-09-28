"""Package identity: id and creation time. Deterministic when SOURCE_DATE_EPOCH is set (reproducible builds convention),
so that regenerating an example or a benchmark package from the same source yields byte-identical manifests."""
from __future__ import annotations
import datetime as _dt, os, uuid

_NS = uuid.UUID("6f1c2a4e-9b3d-4c7a-8e5f-0d2b1a9c7e31")   # OIP namespace for uuid5 package ids


def package_identity(source_hash: str) -> tuple[str, str]:
    """Return (package_id, created). With SOURCE_DATE_EPOCH: uuid5 of the source hash and that timestamp;
    otherwise a random uuid4 and the current UTC time."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        created = _dt.datetime.fromtimestamp(int(epoch), _dt.timezone.utc).isoformat(timespec="seconds")
        return str(uuid.uuid5(_NS, f"urn:oip:source:{source_hash}")), created
    return str(uuid.uuid4()), _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
