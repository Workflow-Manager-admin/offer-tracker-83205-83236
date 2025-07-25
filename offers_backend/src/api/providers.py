from typing import List, Type
from .models import Offer
import random

# You can extend this as more providers are added
ProviderName = str

# Base class for all providers
class OfferProviderBase:
    """Abstract provider integration base for all offer sources."""
    name: ProviderName = "BASE"

    # PUBLIC_INTERFACE
    def fetch_offers(self) -> List[Offer]:
        """Fetches latest offers from this provider. Must be implemented by subclass."""
        raise NotImplementedError("Provider must implement fetch_offers.")

    # Additional methods for other API actions can be added here

# Amazon provider implementation stub (API scraping or SDK integration to be added)
class AmazonOfferProvider(OfferProviderBase):
    name = "Amazon"

    # PUBLIC_INTERFACE
    def fetch_offers(self) -> List[Offer]:
        """Simulated fetch of latest offers from Amazon."""
        # TODO: Replace with real crawl/API logic.
        offer_list = [
            Offer(
                id=random.randint(100, 10000),
                title="Amazon Sample Deal",
                description="Save on select Amazon products.",
                url="https://amazon.com/sample-offer",
                provider="Amazon",
                category="Electronics"
            )
        ]
        return offer_list

# Extensible ProviderManager
class ProviderManager:
    """Handles registration and listing of all active offer providers."""

    _providers: List[Type[OfferProviderBase]] = [AmazonOfferProvider]  # Extend as more providers are implemented

    # PUBLIC_INTERFACE
    def get_all_providers(self) -> List[Type[OfferProviderBase]]:
        """Returns list of all integrated provider classes."""
        return self._providers[:]

    # In future: implement dynamic registration, removal, introspection, etc.

