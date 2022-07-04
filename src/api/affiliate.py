from __future__ import annotations
from typing import Callable
from fastapi import FastAPI
from app.__internal import Function

from src.utils import (
    format_price,
    get_eggsale_amount,
    get_transaction_purchase_log,
    get_valid_wallet_address,
    is_valid_affiliate_id,
    sign_for_redeem,
)
from fastapi import APIRouter, HTTPException, status, Query
from src.database import Database
from src.schemas.affiliate import (
    NewAffiliateInput,
    NewAffiliateOutput,
    RequestRedeemInput,
)
from azure.cosmos import exceptions as cosmos_exceptions
from random import choices
import string


def generate_random_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "-".join(("".join(choices(chars)[0] for _ in range(4))) for __ in range(4))


def get_affiliate_item(address: str, parent_id: str, id: str):
    return {
        "id": id,
        "address": address,
        "parent_id": parent_id,
    }


class Affiliate(Function):
    def __init__(self, error: Callable):
        self.log.info("This is where the initialization code go")
        self.database = Database()
        self.reward_level_container = self.database.getContrainer(
            container_id="REWARD_LEVELS"
        )
        self.affiliate_container = self.database.getContrainer(
            container_id="AFFILIATES"
        )
        self.redeem_container = self.database.getContrainer(container_id="REDEEMS")

        self.reward_levels = list(self.reward_level_container.read_all_items())

    def Bootstrap(self, app: FastAPI):
        router = APIRouter(
            prefix="/affiliate",
            tags=["affiliate"],
            responses={404: {"description": "Not found"}},
        )

        @router.post(
            "/",
            description="Create an affiliate ID along with an optional parent_id parameter.",
            response_model=NewAffiliateOutput,
        )
        async def new_affiliate(data: NewAffiliateInput):
            if data.parent_id.__len__() == 0:
                data.parent_id = None

            if data.parent_id != None:
                if not is_valid_affiliate_id(data.parent_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid parent affiliate id",
                    )

                try:
                    item = self.affiliate_container.read_item(
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

                if item["address"] == data.address:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You can't add another affiliate to your affiliate",
                    )

            new_id = generate_random_id()
            try:
                while (
                    self.affiliate_container.read_item(
                        item=new_id, partition_key=new_id
                    )
                    is None
                ):
                    new_id = generate_random_id()
            except:
                print("Generated random id", new_id)

            valid_address = get_valid_wallet_address(data.address)

            if valid_address is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Wallet address is invalid",
                )

            new_affiliate = {
                "id": new_id,
                "address": data.address,
                "parent_id": data.parent_id,
            }
            try:
                item = self.affiliate_container.create_item(body=new_affiliate)
            except Exception as ex:
                print(ex)
            return item

        @router.post(
            "/{affiliate_id}",
            description="Submit a transaction hash to redeem as a purchase.",
        )
        async def redeem_by_transaction(
            affiliate_id: str = Query(
                regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"
            ),
            transaction_hash: str = Query(regex="0x[a-zA-Z0-9]{64}"),
        ):
            log = get_transaction_purchase_log(transaction_hash)

            if len(log) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No such log",
                )

            if log == None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong in server side",
                )

            try:
                affiliate = self.affiliate_container.read_item(
                    item=affiliate_id, partition_key=affiliate_id
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

            if (
                is_valid_affiliate_id(affiliate["address"], log.topics[1].hex())
                == False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Doesn't runner of this transaction",
                )

            try:
                last_redeems = list(
                    self.redeem_container.query_items(
                        query="SELECT * FROM r WHERE r.transaction_hash=@hash",
                        parameters=[{"name": "@hash", "value": transaction_hash}],
                        enable_cross_partition_query=True,
                    )
                )

            except Exception as ex:
                print(ex)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong in server side",
                )

            if len(last_redeems) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already redeemed",
                )

            count_str = self.redeem_container.query_items(
                query="SELECT VALUE MAX(c.id) FROM c",
                enable_cross_partition_query=True,
            )

            try:
                count = int(list(count_str)[0]) + 1
            except Exception as ex:
                print(ex)
                count = 0

            amount = get_eggsale_amount(log.data)

            print(count)
            redeems = []
            for affiliate_level in range(len(self.reward_levels)):
                redeem = {
                    "id": str(count + affiliate_level),
                    "transaction_hash": transaction_hash,
                    "address": affiliate["address"],
                    "affiliate_id": affiliate["id"],
                    "amount": str(amount),
                    "affiliate_level": str(affiliate_level),
                }

                redeems.append(redeem)

                self.redeem_container.create_item(body=redeem)

                if affiliate["parent_id"] == None:
                    break

                try:
                    affiliate = self.affiliate_container.read_item(
                        item=affiliate["parent_id"],
                        partition_key=affiliate["parent_id"],
                    )

                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Something went wrong in server side",
                    )

            return redeems

        @router.get("/{affiliate_id}", description="Get the rewards for an affiliate.")
        async def get_redeem(
            affiliate_id: str = Query(
                regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"
            ),
        ):
            return list(
                self.redeem_container.query_items(
                    query="SELECT r.id as redeem_code, r.transaction_hash, r.address, r.affiliate_id, r.amount, r.affiliate_level FROM r WHERE r.affiliate_id=@hash",
                    parameters=[{"name": "@hash", "value": affiliate_id}],
                    enable_cross_partition_query=True,
                )
            )

        @router.post(
            "/{affiliate_id}/redeem",
            description="Submit a transaction hash to redeem as a purchase.",
        )
        async def redeem_by_transaction(
            affiliate_id: str = Query(
                regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"
            ),
            data: RequestRedeemInput = RequestRedeemInput(),
        ):
            total_value = 0
            for redeem_code in data.redeem_codes:
                try:
                    redeem = self.redeem_container.read_item(
                        item=str(redeem_code), partition_key=str(redeem_code)
                    )

                except cosmos_exceptions.CosmosResourceNotFoundError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Redeem doesn't exist",
                    )

                except Exception as ex:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Something went wrong in server side",
                    )

                if redeem["affiliate_id"] != affiliate_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Redeem code and affiliate id doesn't match",
                    )

                total_value += int(redeem["amount"]) * int(
                    str(self.reward_levels[int(redeem["affiliate_level"])]["reward"])
                )

                print(total_value)

            affiliate = self.affiliate_container.read_item(
                item=affiliate_id, partition_key=affiliate_id
            )

            signature = sign_for_redeem(
                address=affiliate["address"],
                redeem_codes=data.redeem_codes,
                total_value=total_value,
            )

            return {
                "redeemer": affiliate["address"],
                "redeem_codes": data.redeem_codes,
                "total_value": format_price(total_value),
                "signature": {
                    "r": hex(signature.r),
                    "s": hex(signature.s),
                    "v": signature.v,
                },
            }

        app.include_router(router)
