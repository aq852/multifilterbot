import re


def extract_metadata(name: str) -> dict[str, str | None]:
    value = name or ""
    resolution = re.search(r"(?i)(2160p|1440p|1080p|720p|480p|360p)", value)
    season = re.search(r"(?i)\bS(\d{1,2})(?:-?E\d{1,3})?\b", value)
    quality = re.search(r"(?i)\b(WEB[- .]?DL|WEB[- .]?Rip|Blu[- .]?Ray|HDTV|CAMRip|DVDRip)\b", value)
    language = re.search(r"(?i)\b(English|Hindi|Tamil|Telugu|Japanese|Korean|Spanish|French)\b", value)
    return {
        "resolution": resolution.group(1).lower() if resolution else None,
        "season": f"S{int(season.group(1)):02d}" if season else None,
        "quality": quality.group(1).replace(" ", "-").upper() if quality else None,
        "language": language.group(1).title() if language else None,
    }

