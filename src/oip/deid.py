"""De-identification helpers: PHI tag removal, UID hashing, age banding."""
from __future__ import annotations
import hashlib
from pydicom.dataset import Dataset

# Attributes removed outright (DICOM PS3.15 basic profile, abbreviated).
PHI_KEYWORDS = {
    "PatientName", "PatientID", "PatientBirthDate", "PatientBirthTime", "OtherPatientIDs",
    "OtherPatientNames", "PatientAddress", "PatientTelephoneNumbers", "EthnicGroup",
    "PatientComments", "IssuerOfPatientID", "AccessionNumber", "InstitutionName",
    "InstitutionAddress", "ReferringPhysicianName", "PerformingPhysicianName",
    "OperatorsName", "PhysiciansOfRecord", "NameOfPhysiciansReadingStudy",
    "StationName", "StudyDescription", "SeriesDescription", "StudyID", "RequestingPhysician",
    "StudyDate", "SeriesDate", "AcquisitionDate", "ContentDate", "StudyTime", "SeriesTime",
    "AcquisitionTime", "ContentTime", "AcquisitionDateTime", "InstanceCreationDate",
    "InstanceCreationTime", "DeviceSerialNumber", "ImageComments", "RequestAttributesSequence",
    "ReferencedPatientSequence", "PatientInsurancePlanCodeSequence", "MilitaryRank",
    "PatientReligiousPreference", "AdditionalPatientHistory", "Occupation",
}
UID_KEYWORDS = {"StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "FrameOfReferenceUID",
                "MediaStorageSOPInstanceUID"}


def hash_uid(uid: str | None) -> str | None:
    if not uid:
        return None
    return hashlib.sha256(str(uid).encode()).hexdigest()[:16]


def age_band(patient_age: str | None) -> str | None:
    """'045Y' -> '45-49'; returns None if unknown/unparseable. Ages >= 90 -> '90+'."""
    if not patient_age:
        return None
    s = str(patient_age).strip().upper()
    try:
        n = int(s[:-1]) if s[-1] in "YMWD" else int(s)
        unit = s[-1] if s[-1] in "YMWD" else "Y"
    except ValueError:
        return None
    if unit != "Y":
        return "0-4"
    if n >= 90:
        return "90+"
    lo = (n // 5) * 5
    return f"{lo}-{lo + 4}"


def deidentify(ds: Dataset) -> tuple[Dataset, int]:
    """Return a copy with PHI removed, UIDs hashed, private tags dropped. Also returns count removed."""
    out = Dataset()
    out.file_meta = getattr(ds, "file_meta", None)
    removed = 0
    for elem in ds:
        kw = elem.keyword
        if elem.tag.is_private:
            removed += 1
            continue
        if kw in PHI_KEYWORDS:
            removed += 1
            continue
        if kw in UID_KEYWORDS:
            out.add_new(elem.tag, elem.VR, "2.25." + str(int(hash_uid(elem.value), 16)))
            continue
        if kw == "PatientAge":
            band = age_band(elem.value)
            if band:
                out.add_new(elem.tag, elem.VR, band.replace("-", "").rjust(3, "0")[:3] + "Y" if band != "90+" else "090Y")
            continue
        out.add(elem)
    return out, removed
