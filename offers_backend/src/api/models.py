from pydantic import BaseModel, Field
from typing import List, Dict

# PUBLIC_INTERFACE
class Offer(BaseModel):
    """Offer model representing a deal or coupon from a provider."""
    id: int = Field(..., description="Unique offer ID")
    title: str = Field(..., description="Short display title for the offer")
    description: str = Field(..., description="Detailed description of offer terms")
    url: str = Field(..., description="Direct URL to the offer")
    provider: str = Field(..., description="Name of the source/provider (e.g. Amazon)")
    category: str = Field(..., description="Offer's category")

# PUBLIC_INTERFACE
class Category(BaseModel):
    """Category model representing an offer category."""
    name: str = Field(..., description="Category name")

# PUBLIC_INTERFACE
class ProviderAddRequest(BaseModel):
    """Request schema for adding a provider."""
    provider_name: str = Field(..., description="Name of provider to add")
    credentials: Dict[str, str] = Field(..., description="API/connection credentials/config as key-value pairs")

# PUBLIC_INTERFACE
class ProviderAddResponse(BaseModel):
    """Response schema after adding a provider."""
    success: bool
    message: str

# PUBLIC_INTERFACE
class RefreshResponse(BaseModel):
    """Response returned after a refresh of offers from providers."""
    refreshed_providers: List[str]
    offer_count: int

