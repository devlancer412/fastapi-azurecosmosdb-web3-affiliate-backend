import re
import os
import json
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

load_dotenv(".env")

RPC_URL = os.getenv("RPC_URL")
PURCHASE_EVENT_FILTER = os.getenv("AFFILIATE_CALL_ID").lower()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

web3 = Web3(provider=Web3.HTTPProvider(RPC_URL))

affiliate_data = json.load(open("app/contracts/affiliate.json"))
affiliate_contract = web3.eth.contract(
    address=affiliate_data["address"], abi=affiliate_data["abi"]
)


def is_valid_wallet_address(address: str) -> bool:
    pattern = re.compile("0x[0-9a-zA-Z]{32}")
    return pattern.match(address)


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
