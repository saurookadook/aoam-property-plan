from __future__ import annotations

from fastapi import status
from sqlalchemy.orm import Session

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.market.db import MarketDBFactory
from models.listing.entity import ListingEntity


class TestReadListingsListRoute:
    def test_returns_all_listings(self, test_app_client, test_db_session: Session):
        market = MarketDBFactory()
        test_db_session.commit()

        listing_second = ListingEntityFactory(
            airroi_id=2,
            market_id=market.id,
        )
        listing_first = ListingEntityFactory(airroi_id=1, market_id=market.id)
        ListingDBFactory(**listing_second.model_dump())
        ListingDBFactory(**listing_first.model_dump())
        test_db_session.commit()

        result = test_app_client.get("/api/listings")

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {
            "data": [
                ListingEntity.model_validate(listing_first).model_dump(mode="json"),
                ListingEntity.model_validate(listing_second).model_dump(mode="json"),
            ]
        }

    def test_returns_no_listings(self, test_app_client):
        result = test_app_client.get("/api/listings")

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {"data": []}


class TestReadListingRoute:
    def test_returns_listing(self, test_app_client, test_db_session: Session):
        market = MarketDBFactory()
        test_db_session.commit()

        listing = ListingEntityFactory(market_id=market.id)
        ListingDBFactory(**listing.model_dump())
        test_db_session.commit()

        result = test_app_client.get(f"/api/listings/{listing.id}")

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {
            "data": ListingEntity.model_validate(listing).model_dump(mode="json")
        }

    def test_raises_http_exception_for_nonexistent_listing(self, test_app_client):
        non_existent_listing_id = "01d336ff-c742-4682-80bb-5f7d5cdf8d26"

        result = test_app_client.get(f"/api/listings/{non_existent_listing_id}")

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Listing not found"}
