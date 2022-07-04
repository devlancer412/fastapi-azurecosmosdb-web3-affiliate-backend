from logging import exception
import re
import os
import json
from urllib.request import HTTPPasswordMgrWithDefaultRealm
from web3 import Web3
from web3.auto import w3
from eth_abi import decode_abi
from eth_account.messages import encode_defunct
from random import choices
import string

from config import cfg

RPC_URL = cfg.RPC_URL
PURCHASE_EVENT_FILTER = cfg.AFFILIATE_CALL_ID.lower()
PRIVATE_KEY = cfg.PRIVATE_KEY

web3 = Web3(provider=Web3.HTTPProvider(RPC_URL))

affiliate_data = json.load(open(os.path.join("src", "contracts", "affiliate.json")))
affiliate_contract = web3.eth.contract(
    address=affiliate_data["address"], abi=affiliate_data["abi"]
)


def generate_random_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "-".join(("".join(choices(chars)[0] for _ in range(4))) for __ in range(4))


def get_valid_wallet_address(address: str) -> str:
    try:
        return Web3.toChecksumAddress(address)
    except Exception as ex:
        print(ex)
        return None


def is_valid_affiliate_id(id: str) -> bool:
    pattern = re.compile(r"[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}")
    print(id, re.search(pattern, id))
    return pattern.match(id)


def get_transaction_purchase_log(tx_hash: str) -> object:
    try:
        receipt = web3.eth.get_transaction_receipt(tx_hash)

        return list(
            filter(
                lambda log: log.topics[0].hex() == PURCHASE_EVENT_FILTER, receipt.logs
            )
        )[0]
    except Exception as ex:
        print(ex)
        return None


def uint256_to_address(address: str):
    return Web3.toChecksumAddress("0x" + address[-40:])


def compare_address(address1: str, address2: str):
    return Web3.toChecksumAddress(address1) == Web3.toChecksumAddress(address2)


def is_valid_affiliate_id(address: str, affiliate_id: str):
    hashed_address = Web3.solidityKeccak(
        ["address"],
        [Web3.toChecksumAddress(address)],
    )
    return hashed_address.hex() == affiliate_id


def sign_for_redeem(address: str, redeem_codes: list[int], total_value):
    hashed = Web3.solidityKeccak(
        ["address", "uint256[]", "uint256"],
        [Web3.toChecksumAddress(address), redeem_codes, total_value],
    )
    eth_signed_message_hash = Web3.solidityKeccak(
        ["string", "bytes32"], ["\x19Ethereum Signed Message:\n32", hashed]
    )

    message = encode_defunct(eth_signed_message_hash)
    return w3.eth.account.sign_message(message, private_key=PRIVATE_KEY)


def format_price(price: int) -> str:
    return "{:_}".format(price)


def get_eggsale_amount(data: bytes) -> int:
    decoded = decode_abi(["address", "uint256"], bytes(data))
    return int(decoded[len(decoded) - 1])
