from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import logging

from .providers import ProviderManager
from .models import Offer, Category, ProviderAddRequest, ProviderAddResponse, RefreshResponse

# LOGGER SETUP
logger = logging.getLogger("offers_backend")
logging.basicConfig(level=logging.INFO)

# FastAPI app config with metadata for OpenAPI
app = FastAPI(
    title="Offer Tracker API",
    description="Backend for tracking, retrieving, and refreshing offers from different providers.",
    version="0.1.0",
    openapi_tags=[
        {"name": "offers", "description": "Operations related to offers"},
        {"name": "categories", "description": "Offer category listing"},
        {"name": "providers", "description": "Provider management and integration"},
        {"name": "admin", "description": "Admin or maintenance operations"},
    ],
)

# CORS SETUP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- JWT AUTHENTICATION HOOKS (NOT REQUIRED FOR MVP, BUT STRUCTURE PROVIDED) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Example dependency. For actual use, hook up JWT secret, algorithm, user fetch, etc.
def get_current_user(token: str = Depends(oauth2_scheme)):
    # --- placeholder for real validation ---
    # Raise HTTPException(status_code=401) on invalid
    return None

# --- DATABASE HOOKS (DEPENDENCY: offers_database) ---
# Placeholders for DB integration; expected to be implemented via offers_database container
def get_db():
    # This would return a DB session/connection (via e.g. SQLAlchemy or direct client)
    # For now, returns a dummy object
    class DummyDB:
        def query_offers(self, category: Optional[str] = None) -> List[Offer]:
            # Dummy example data
            base_offers = [
                Offer(id=1, title="10% off Books", description="Great deal on books", url="https://amazon.com/deal1", provider="Amazon", category="Books"),
                Offer(id=2, title="Laptop Sale", description="Best laptop discounts", url="https://amazon.com/deal2", provider="Amazon", category="Electronics"),
            ]
            if category:
                return [o for o in base_offers if o.category.lower() == category.lower()]
            return base_offers

        def get_categories(self) -> List[Category]:
            return [
                Category(name="Books"),
                Category(name="Electronics"),
                Category(name="Fashion"),
            ]

        def add_provider(self, provider_name: str, credentials: dict) -> bool:
            # Accepts everything in stub
            return True

        def save_offers(self, offers: List[Offer]) -> int:
            return len(offers)

        def purge_and_refresh(self):
            return 1

    return DummyDB()

# --- ROUTES ---

# PUBLIC_INTERFACE
@app.get("/offers", response_model=List[Offer], tags=["offers"], summary="Get offers", description="Retrieve all offers, optionally filtered by category.")
async def get_offers(category: Optional[str] = None, db=Depends(get_db)):
    """
    Returns a list of current offers from all providers, optionally filtered by category.

    - **category**: Optional filter for offers. If not provided, returns all.
    """
    offers = db.query_offers(category)
    logger.info(f"Fetched {len(offers)} offers for category: {category}")
    return offers

# PUBLIC_INTERFACE
@app.get("/categories", response_model=List[Category], tags=["categories"], summary="Get offer categories", description="List all available offer categories.")
async def get_categories(db=Depends(get_db)):
    """
    Returns all categories currently available for offers.
    """
    cat_list = db.get_categories()
    logger.info(f"Categories listed: {[c.name for c in cat_list]}")
    return cat_list

# PUBLIC_INTERFACE
@app.post("/providers/add", response_model=ProviderAddResponse, tags=["providers"], summary="Add provider integration", description="Add/integrate a new provider, such as Amazon. Extensible for more.")
async def add_provider(data: ProviderAddRequest, db=Depends(get_db)):
    """
    Registers/adds a new provider credentials, for later offer fetching.

    - **provider_name**: Provider name (Amazon supported, extensible for future providers)
    - **credentials**: Dict of connection or API credentials/configs.
    """
    logger.info(f"Adding provider: {data.provider_name}")
    # In a real system, credentials would be saved and verified
    res = db.add_provider(data.provider_name, data.credentials)
    if not res:
        raise HTTPException(status_code=400, detail="Provider integration failed")
    return ProviderAddResponse(success=True, message=f"Provider '{data.provider_name}' connected.")

# PUBLIC_INTERFACE
@app.post("/offers/refresh", response_model=RefreshResponse, tags=["admin"], summary="Refresh offers from all providers", description="Refresh/pull new offers from integrated providers.")
async def refresh_offers(db=Depends(get_db)):
    """
    Triggers a manual offers refresh by fetching the latest from all integrated providers (starting with Amazon).

    Returns:
      - Number of offers refreshed, and which providers updated.
    """
    provider_mgr = ProviderManager()
    # Fetch new offers from all providers (here: only Amazon)
    offers = []
    refreshed_providers = []
    for provider_cls in provider_mgr.get_all_providers():
        prov = provider_cls()
        logger.info(f"Refreshing offers from provider: {prov.name}")
        new_offers = prov.fetch_offers()
        offers.extend(new_offers)
        refreshed_providers.append(prov.name)
    # Save the new offers to database
    db.save_offers(offers)
    logger.info(f"Refreshed {len(offers)} offers from providers: {refreshed_providers}")
    return RefreshResponse(
        refreshed_providers=refreshed_providers,
        offer_count=len(offers)
    )

@app.get("/", tags=["misc"])
async def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

