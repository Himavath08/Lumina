from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [ "verify", "update", "bank", "urgent"]

def analyze_url(url: str):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    score = 0
    reasons = []

    if any(word in url.lower() for word in SUSPICIOUS_KEYWORDS):
        score += 1
        reasons.append("Suspicious keyword found")

    if "-" in domain or len(domain) > 30:
        score += 1
        reasons.append("Suspicious domain pattern")

    if score >= 1:
        return {"status": "suspicious", "reasons": reasons}
    else:
        return {"status": "safe"}