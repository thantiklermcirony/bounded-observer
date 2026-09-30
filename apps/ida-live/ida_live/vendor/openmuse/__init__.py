"""Vendored from OpenMuse (https://github.com/DominiqueMakowski/OpenMuse), commit a9be252,
MIT licence (declared in OpenMuse's pyproject.toml), (c) Dominique Makowski and contributors.

Only the Muse S Athena protocol decoder, clock models and device commands are included.
Changes: pandas is optional (only the offline decode_rawdata helper needs it) and the
clock fallback uses time.perf_counter instead of mne_lsl's local_clock, so the installed
app needs neither pandas nor LSL. Nothing else is modified.
"""
