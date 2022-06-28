from pydantic import BaseModel, Field


class NewAffiliateInput(BaseModel):
    address: str = Field(
        nullable=False, description="User wallet address", regex="0x[0-9a-zA-Z]{32}"
    )
    parent_affiliate_id: str | None = Field(
        default=None,
        nullable=True,
        description="Parent id",
        regex="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}",
    )


class NewAffiliateOutput(NewAffiliateInput):
    affiliate_id: str
