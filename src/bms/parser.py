from pathlib import Path

from .exc import ParseBmsError


def scan_bms_file(scan_path:Path):
    """scan the bms file and return the bms info"""
    bms_file_info = []
    for file_path in scan_path.rglob("*.*"):
        if is_bms_file(file_path):
            bms_file_info.append(get_bms_info(file_path))

    return bms_file_info


def is_bms_file(file_path:Path):
    """determines whether the file is a bms file"""
    return all((
        file_path.is_file(),
        file_path.suffix in (".bms", ".bme"),
        file_path.name not in '.-~', 
    ))


def get_bms_info(file_path:Path):
    """obtain bms file meta info"""
    info = {
        "file_path": file_path,
        # below properties read from the file
        "PLAYER": "",
        "TITLE": "",
        "ARTIST": "",
        "GENRE": "",
        "PLAYLEVEL": "",
        "RANK": "",
        "TOTAL": "",
        "DIFFICULTY": "",
        "BPM": "",
        "PREVIEW": "",
        # below properties calculated from the file
        "MIN_BPM": 0,
        "MAX_BPM": 0,
    }

    with open(file_path, "rb") as fp:
        for line_no, line in enumerate(fp):
            # parse the meta info
            for key in (
                b"PLAYER", b"TITLE", b"ARTIST", b"GENRE", b"PLAYLEVEL",
                b"RANK", b"TOTAL", b"DIFFICULTY", b"BPM", b"PREVIEW",
            ):
                if line.startswith(b"#%s " % key):
                    tmp_str = line.partition(b" ")[2].strip()

                    decoded_tmp_str = _try_decode(tmp_str)
                    if not decoded_tmp_str:
                        raise ParseBmsError(f"parse error at line {line_no+1}: unknown char coding")
                    
                    info [key.decode()] = decoded_tmp_str
                    break

            # parse the min/max bpm info
            if line.startswith(b"#BPM"):
                tmp = line.partition(b" ")
                if len(tmp) == 6:
                    if info["MIN_BPM"]:
                        info["MIN_BPM"] = min(round(float(tmp[2])), info["MIN_BPM"])
                    else:
                        info["MIN_BPM"] = round(float(tmp[2]))
                    if info["MAX_BPM"]:
                        info["MAX_BPM"] = min(round(float(tmp[2])), info["MAX_BPM"])
                    else:
                        info["MAX_BPM"] = round(float(tmp[2]))

    if not info["MIN_BPM"] and info["BPM"]:
        info["MIN_BPM"] = round(float(info["BPM"]))
    if not info["MAX_BPM"] and info["BPM"]:
        info["MAX_BPM"] = round(float(info["BPM"]))

    return info


def _try_decode(tmp_str):
    """try to decode the string"""
    decoded_tmp_str = ""
    for i in (
        "utf8",
        "shiftjis",     # Japanese
        "gbk",          # Chinese
    ):
        try:
            decoded_tmp_str = tmp_str.decode(encoding=i)
            break
        except UnicodeDecodeError:
            continue
    return decoded_tmp_str
