from fastapi import APIRouter, HTTPException, status, Query
from app.database import Database, scale_container
from app.schemas.affiliate import NewAffiliateInput, NewAffiliateOutput
import web3
import uuid
import random
import string

router = APIRouter(
    prefix="/affiliate",
    tags=["affiliate"],
    responses={404: {"description": "Not found"}},
)

database = Database()
rewardLevelContainer = database.getContrainer(containerId="REWARD_LEVEL")
affiliateContainer = database.getContrainer(containerId="AFFILIATES")
redeemContainer = database.getContrainer(containerId="REDEEM")


rewardLevels = [
    {"id": "0", "reward": 2.4},
    {"id": "1", "reward": 0.6},
    {"id": "2", "reward": 0.12},
]


def get_affiliate_item(address: str, parent_affiliate_id: str, affiliate_id: str):
    return {
        "affiliate_id": affiliate_id,
        "address": address,
        "parent_affiliate_id": parent_affiliate_id,
    }


def get_random_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "-".join("".join(random.choices(chars) for _ in range(4)) for __ in range(4))


if len(list(rewardLevelContainer.read_all_items())) == 0:
    for rewardLevel in rewardLevels:
        rewardLevelContainer.create_item(body=rewardLevel)

rewardLevels = list(rewardLevelContainer.read_all_items())


@router.post(
    "/",
    description="Create an affiliate ID along with an optional parent_affiliate_id parameter.",
    response_model=NewAffiliateOutput,
)
async def new_affiliate(data: NewAffiliateInput):
    if data.parent_affiliate_id != None:
        item = affiliateContainer.read_item(
            item=data.parent_affiliate_id, partition_key=data.parent_affiliate_id
        )

        if item == None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent affiliate doesn't exist",
            )

    new_affiliate_id = get_random_id()
    while (
        affiliateContainer.read_item(
            item=new_affiliate_id, partition_key=new_affiliate_id
        )
        != None
    ):
        new_affiliate_id = get_random_id()

    new_affiliate = {
        "affiliate_id": new_affiliate_id,
        "address": data.address,
        "parent_affiliate_id": data.parent_affiliate_id,
    }
    affiliateContainer.create_item(body=new_affiliate)


@router.post(
    "/{affiliate_id}", description="Submit a transaction hash to redeem as a purchase."
)
async def redeem_by_transaction(
    affiliate_id: str = Query(regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"),
    transaction_hash: str = Query(regex="0x[a-zA-Z0-9]{64}"),
):
    item = affiliateContainer.read_item(item=affiliate_id, partition_key=affiliate_id)
    if item == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Affiliate doesn't exist",
        )
    transaction = web3.eth.get_transzction(transaction_hash)
