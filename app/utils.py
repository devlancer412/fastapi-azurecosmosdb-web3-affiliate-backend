def isValidWalletAddress(address: str) -> bool:
    return address.fullmatch(r"0x[0-9a-zA-Z]{32}")


def isValidAffiliateId(id: str) -> bool:
    return id.fullmatch(r"[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}")
