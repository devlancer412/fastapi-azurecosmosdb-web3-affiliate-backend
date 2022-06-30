import re

def isValidWalletAddress(address: str) -> bool:
    pattern = re.compile("0x[0-9a-zA-Z]{32}")
    return pattern.match(address)


def isValidAffiliateId(id: str) -> bool:
    pattern = re.compile(r"[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}")
    print(id, re.search(pattern, id))
    return pattern.match(id)
