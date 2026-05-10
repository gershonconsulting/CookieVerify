"""
profile_sanitizer.py  —  v1.2.0
--------------------
Cleans LinkedIn profile data before serializing the /api/validate response.

Fixes:
    1. Trailing punctuation on lastName, e.g. "Puard,"
    2. Vanity slug leaking into firstName/fullName when the user has no
       LinkedIn display name set, e.g. "Brunoseguin9178874", "Zaksirlin",
       "Ouryc", "Jeffreyglick", "Krisvanransbeek"
    3. isValid: true firing even when no usable name was extracted

v1.2.0 changes vs v1.1.0:
    - Always populate `username` field from vanityName (LinkedIn URL slug)
      so the UI can display it as its own column.
    - Stricter vanity-slug detection: any single-token name (no spaces, no
      real-name signal) that matches the vanity slug is flagged as
      vanity_only — catches Zaksirlin / Ouryc / Jeffreyglick that v1.1.0
      missed because they had no digits.
"""
import re
import unicodedata

LOWERCASE_PARTICLES = {
    "de", "del", "della", "di", "da", "das", "do", "dos",
    "van", "von", "der", "den", "ter",
    "la", "le", "les", "el", "al",
    "bin", "ibn", "bint",
}

_TRAILING_PUNCT = re.compile(r"[\s,;.\-_]+$")
_LEADING_PUNCT  = re.compile(r"^[\s,;.\-_]+")
_ZERO_WIDTH     = re.compile(r"[​-‏﻿]")
_CONTROL_CHARS  = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_MULTI_SPACE    = re.compile(r"\s+")
_HAS_DIGIT      = re.compile(r"\d")


def _clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = _ZERO_WIDTH.sub("", s)
    s = _CONTROL_CHARS.sub("", s)
    s = _MULTI_SPACE.sub(" ", s)
    s = _LEADING_PUNCT.sub("", s)
    s = _TRAILING_PUNCT.sub("", s)
    s = s.strip()
    return s if s else None


def _normalize(s):
    """Lowercase + alphanumeric only, accent-stripped — for slug comparison."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", no_accents.lower())


_NULL_LITERALS = {"none", "null", "undefined", "nil", "n/a", "na", "none none", "null null"}


def _is_vanity_garbage(name, vanity):
    """
    Returns True when `name` is clearly the vanity URL slug or a literal
    "None"/"null" string from a serialization bug rather than a real
    human display name.

    Signals:
      - Literal "None"/"null"/"undefined" strings (caused by upstream
        f-string formatting None values into strings — v1.2.1).
      - Digits in the name (LinkedIn display names never have them).
      - Single-token name (no space) whose normalized form matches the
        vanity slug — e.g. firstName="Zaksirlin" with vanity="zaksirlin",
        or firstName="Brunoseguin" with vanity="brunoseguin9178874".
        Real LinkedIn display names from the API arrive split into
        firstName + lastName, so a single-token name == vanity slug means
        the API returned nothing usable and the code fell back to the URL.
    """
    if not name:
        return False
    if name.strip().lower() in _NULL_LITERALS:
        return True
    if _HAS_DIGIT.search(name):
        return True
    if vanity and " " not in name:
        n = _normalize(name)
        v = _normalize(vanity)
        if not n:
            return False
        # Exact match: firstName=="zaksirlin" and vanity=="zaksirlin"
        if n == v:
            return True
        # Prefix match where the rest of the slug is digits
        # (firstName=="brunoseguin", vanity=="brunoseguin9178874")
        if v.startswith(n) and len(v) > len(n):
            tail = v[len(n):]
            if _HAS_DIGIT.search(tail):
                return True
    return False


def _title_case_token(token):
    """Title-case a single token, handling hyphens and apostrophes."""
    out = []
    capitalize_next = True
    for ch in token:
        if ch in ("-", "'", "’"):
            out.append(ch)
            capitalize_next = True
        elif capitalize_next:
            out.append(ch.upper())
            capitalize_next = False
        else:
            out.append(ch.lower())
    return "".join(out)


def _title_case(s):
    """Title-case a name, preserving lowercase particles in the middle."""
    if not s:
        return s
    words = s.split(" ")
    parts = []
    for i, w in enumerate(words):
        if not w:
            continue
        if i > 0 and w.lower() in LOWERCASE_PARTICLES:
            parts.append(w.lower())
        else:
            parts.append(_title_case_token(w))
    return " ".join(parts)


def sanitize_profile(profile):
    """
    Mutates and returns the profile dict from validate_linkedin_cookie().

    Always populates:
        - username (str | None): LinkedIn URL slug, mirrors vanityName
                                 for clean UI display.

    Adds derived fields:
        - profileComplete (bool): isValid AND a usable name was extracted.
        - nameSource (str): 'linkedin' | 'vanity_only' | 'none'.
    """
    if not isinstance(profile, dict):
        return profile

    # 1. Clean every string field.
    for key in ("firstName", "lastName", "fullName", "vanityName",
                "company", "headline", "title", "profileUrl", "error"):
        if key in profile:
            profile[key] = _clean(profile.get(key))

    vanity = profile.get("vanityName")

    # 2. Always expose username (the LinkedIn URL slug).
    profile["username"] = vanity

    # 3. Detect vanity-slug-as-name and null out garbage.
    # If we have BOTH a firstName AND a lastName populated (and neither is a
    # null literal), trust them as a real name structure. This avoids false
    # positives like firstName="Bruno", lastName="Séguin", vanity="brunoseguin9178874"
    # — where the vanity slug happens to start with "bruno" + digits.
    has_first = profile.get("firstName") and profile.get("firstName").strip().lower() not in _NULL_LITERALS
    has_last = profile.get("lastName") and profile.get("lastName").strip().lower() not in _NULL_LITERALS
    if has_first and has_last:
        name_is_garbage = False
    else:
        name_is_garbage = (
            _is_vanity_garbage(profile.get("firstName"), vanity)
            or _is_vanity_garbage(profile.get("fullName"), vanity)
            or _is_vanity_garbage(profile.get("lastName"), vanity)
        )
    if name_is_garbage:
        profile["firstName"] = None
        profile["lastName"]  = None
        profile["fullName"]  = None
        profile["nameSource"] = "vanity_only"
    elif not any([profile.get("firstName"), profile.get("lastName"), profile.get("fullName")]):
        profile["nameSource"] = "none"
    else:
        profile["nameSource"] = "linkedin"

    # 4. Title-case surviving name fields.
    profile["firstName"] = _title_case(profile.get("firstName"))
    profile["lastName"]  = _title_case(profile.get("lastName"))
    profile["fullName"]  = _title_case(profile.get("fullName"))

    # 5. Reconstruct fullName from parts when possible.
    fn, ln = profile.get("firstName"), profile.get("lastName")
    if fn and ln:
        profile["fullName"] = f"{fn} {ln}".strip()
    elif fn and not profile.get("fullName"):
        profile["fullName"] = fn
    elif ln and not profile.get("fullName"):
        profile["fullName"] = ln

    # 6. profileComplete: cookie auth worked AND we have a usable name.
    profile["profileComplete"] = bool(
        profile.get("isValid") and profile.get("fullName")
    )

    return profile
