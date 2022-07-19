from pydantic import BaseModel, Field
from typing import List, Union


class NewAffiliateInput(BaseModel):
    address: str = Field(
        nullable=False, description="User wallet address", regex="0x[0-9a-zA-Z]{32}"
    )
    parent_id: Union[str, None] = Field(
        default=None,
        nullable=True,
        description="Parent id",
        # regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}",
    )


class NewAffiliateOutput(NewAffiliateInput):
    id: str


class RequestRedeemInput(BaseModel):
    redeem_codes: List[int] = []
