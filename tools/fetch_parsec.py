"""Fetch PARSEC isochrones from the CMD web service and convert them into the model's table.

    uv run python tools/fetch_parsec.py --raw <dir>     # download (skips files already there) and convert
    uv run python tools/fetch_parsec.py --raw <dir> --convert-only

One request per metallicity to the CMD 3.9 form (PARSEC v1.2S + COLIBRI TP-AGB, Kroupa IMF,
UBVRIJHK), every log age on the grid in each. The raw tables stay out of the repository;
what is committed is ``model/galaxy/data/parsec_isochrones.npz``: per isochrone, initial mass,
log L, log T_eff and the evolutionary-phase label, as float32 — the four columns photometry needs.

Attribution: see the README's Attributions section. The CMD service's certificate does not
verify (an incomplete chain), so this client does not verify it either; it only reads data.
"""

from __future__ import annotations

import argparse
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "galaxy" / "data" / "parsec_isochrones.npz"
CMD = "https://stev.oapd.inaf.it/cgi-bin/cmd_3.9"
SERVER = "https://stev.oapd.inaf.it"

LOG_AGES = np.round(np.arange(6.6, 10.1001, 0.1), 2)  # asked for 6.6-10.1; CMD returns 6.6-10.0, 35 ages
METALLICITIES = np.round(np.arange(-2.2, 0.3001, 0.25), 2)  # [M/H] -2.2 to +0.3: 11 values (CMD clamps -2.2 to -2.19)

FORM = {
    "cmd_version": "3.9", "track_parsec": "parsec_CAF09_v1.2S", "track_colibri": "parsec_CAF09_v1.2S_S_LMC_08_web",
    "track_omegai": "0.00", "track_postagb": "no", "n_inTPC": "10", "eta_reimers": "0.2", "kind_interp": "1",
    "kind_postagb": "-1", "photsys_file": "YBC_tab_mag_odfnew/tab_mag_ubvrijhk.dat", "photsys_version": "YBCnewVega",
    "dust_sourceM": "dpmod60alox40", "dust_sourceC": "AMCSIC15", "kind_mag": "2", "kind_dust": "0",
    "extinction_av": "0.0", "extinction_coeff": "constant", "extinction_curve": "cardelli", "kind_LPV": "4",
    "imf_file": "tab_imf/imf_kroupa_orig.dat", "isoc_isagelog": "1", "isoc_agelow": "1.0e9", "isoc_ageupp": "1.0e10",
    "isoc_dage": "0.0", "isoc_ismetlog": "1", "isoc_zlow": "0.0152", "isoc_zupp": "0.03", "isoc_dz": "0.0",
    "output_kind": "0", "output_evstage": "1", "lf_maginf": "-15", "lf_magsup": "20", "lf_deltamag": "0.5",
    "sim_mtot": "1.0e4", "submit_form": "Submit",
}

INSECURE = ssl.create_default_context()
INSECURE.check_hostname = False
INSECURE.verify_mode = ssl.CERT_NONE


def fetch(mh: float, dest: Path) -> None:
    form = {**FORM, "isoc_lagelow": f"{LOG_AGES[0]}", "isoc_lageupp": f"{LOG_AGES[-1]}", "isoc_dlage": "0.1",
            "isoc_metlow": f"{mh}", "isoc_metupp": f"{mh}", "isoc_dmet": "0.0"}
    body = urllib.parse.urlencode(form).encode()
    with urllib.request.urlopen(urllib.request.Request(CMD, data=body), context=INSECURE, timeout=900) as r:
        page = r.read().decode("utf-8", "replace")
    found = re.search(r"\.\./tmp/(output\d+\.dat)", page)
    if not found:
        raise RuntimeError(f"[M/H] = {mh}: no output file in the CMD response")
    with urllib.request.urlopen(f"{SERVER}/tmp/{found.group(1)}", context=INSECURE, timeout=900) as r:
        dest.write_bytes(r.read())


def read(path: Path) -> list[dict[str, np.ndarray]]:
    """Split one CMD file into isochrones, keeping the four columns photometry needs."""
    header: list[str] | None = None
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# Zini"):
            header = line[1:].split()
        elif line and not line.startswith("#"):
            rows.append([float(x) for x in line.split()])
    if header is None or not rows:
        raise RuntimeError(f"{path}: no isochrone table")
    table = np.array(rows)
    col = {name: header.index(name) for name in ("MH", "logAge", "Mini", "logL", "logTe", "label")}
    out = []
    for age in np.unique(np.round(table[:, col["logAge"]], 2)):
        sel = np.round(table[:, col["logAge"]], 2) == age
        out.append({
            "mh": float(np.round(table[sel, col["MH"]][0], 2)), "log_age": float(age),
            **{k: table[sel, col[c]] for k, c in (("mass", "Mini"), ("log_l", "logL"), ("log_teff", "logTe"), ("label", "label"))},
        })
    return out


def convert(raw: Path) -> None:
    isochrones = [iso for mh in METALLICITIES for iso in read(raw / f"parsec_mh{mh:+.2f}.dat")]
    lengths = np.array([len(i["mass"]) for i in isochrones])
    offsets = np.concatenate([[0], np.cumsum(lengths)[:-1]])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT,
        mh=np.array([i["mh"] for i in isochrones], np.float32),
        log_age=np.array([i["log_age"] for i in isochrones], np.float32),
        offset=offsets.astype(np.int32), length=lengths.astype(np.int32),
        mass=np.concatenate([i["mass"] for i in isochrones]).astype(np.float32),
        log_l=np.concatenate([i["log_l"] for i in isochrones]).astype(np.float32),
        log_teff=np.concatenate([i["log_teff"] for i in isochrones]).astype(np.float32),
        label=np.concatenate([i["label"] for i in isochrones]).astype(np.int8),
        source=np.array("PARSEC v1.2S + COLIBRI via CMD 3.9 (stev.oapd.inaf.it); see README Attributions"),
    )
    print(f"{len(isochrones)} isochrones, {lengths.sum()} rows -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.2f} MB)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", type=Path, required=True, help="directory for the raw CMD tables (not committed)")
    ap.add_argument("--convert-only", action="store_true")
    args = ap.parse_args()
    args.raw.mkdir(parents=True, exist_ok=True)
    if not args.convert_only:
        for mh in METALLICITIES:
            dest = args.raw / f"parsec_mh{mh:+.2f}.dat"
            if dest.exists():
                continue
            start = time.time()
            fetch(float(mh), dest)
            print(f"[M/H] = {mh:+.2f}: {dest.stat().st_size / 1e6:.2f} MB in {time.time() - start:.0f} s", flush=True)
            time.sleep(5)  # one job at a time, and a pause between them: it is someone else's server
    convert(args.raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
