from app.utils import isValidAffiliateId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import Database, scale_container
from app.schemas.affiliate import NewAffiliateInput, NewAffiliateOutput
from azure.cosmos import exceptions as cosmos_exceptions
import web3
import uuid
from random import choices
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


def get_affiliate_item(address: str, parent_id: str, id: str):
    return {
        "id": id,
        "address": address,
        "parent_id": parent_id,
    }


def generate_random_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "-".join(("".join(choices(chars)[0] for _ in range(4))) for __ in range(4))

if len(list(rewardLevelContainer.read_all_items())) == 0:
    for rewardLevel in rewardLevels:
        rewardLevelContainer.create_item(body=rewardLevel)

rewardLevels = list(rewardLevelContainer.read_all_items())


@router.post(
    "/",
    description="Create an affiliate ID along with an optional parent_id parameter.",
    response_model=NewAffiliateOutput,
)
async def new_affiliate(data: NewAffiliateInput):
    if data.parent_id.__len__() == 0:
        data.parent_id = None

    if data.parent_id != None :
        if not isValidAffiliateId(data.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent affiliate id",
            )
            
        try:
            item = affiliateContainer.read_item(
                item=data.parent_id, partition_key=data.parent_id
            )
        except cosmos_exceptions.CosmosResourceNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent affiliate doesn't exist",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong in server side",
            )

        print(item, data)
        if item.address == data.address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent affiliate is invalid",
            )

    new_id = generate_random_id()
    try:
        while (
            affiliateContainer.read_item(
                item=new_id, partition_key=new_id
            )
            != None
        ):
            new_id = generate_random_id()
    except:
        print("Generated random id", new_id)

    new_affiliate = {
        "id": new_id,
        "address": data.address,
        "parent_id": data.parent_id,
    }
    try:
        affiliateContainer.create_item(body=new_affiliate)
    except Exception as ex:
        print(ex)

@router.post(
    "/{id}", description="Submit a transaction hash to redeem as a purchase."
)
async def redeem_by_transaction(
    id: str = Query(regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"),
    transaction_hash: str = Query(regex="0x[a-zA-Z0-9]{64}"),
):
    item = affiliateContainer.read_item(item=id, partition_key=id)
    if item == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Affiliate doesn't exist",
        )
    transaction = web3.eth.get_transzction(transaction_hash)
