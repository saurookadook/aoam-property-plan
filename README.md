# AOAM Property Plan

## TL;DR

```sh
docker compose up all -d
```

---

## Installation/Setup

### First Time Setup

#### Set up NGINX Reverse Proxy

See [Setup instructions](/nginx-reverse-proxy/README.md#setup) for `nginx-reverse-proxy` service.

```sh
chmod +x scripts/admin.sh
./scripts/admin.sh db create
./scripts/admin.sh db create-test
```

#### Backend

See [Setup instructions](/backend/README.md#setup) for `backend` sevice.

#### Frontend

See [Setup instructions](/frontend/README.md#setup) for `frontend` sevice.

---

## Data Sources

- [airroi][airroi]
  + [airroi: Developer Dashboard][airroi--dev-dash]

## AirROI Endpoints

- [Search Listings by Market - `POST /listings/search/market][airroi--search-listings-by-market]

## AirBnB URL Examples

- [Salento, weekend, 2 adults][airbnb--salento-wknd-2-adlt]

<!-- LINKS -->

[airroi]: https://www.airroi.com/api/pricing
[airroi--dev-dash]: https://www.airroi.com/api/developer/activate
[airroi--search-listings-by-market]: https://www.airroi.com/api/documentation#tag/Listings/operation/searchListingsByMarket
[airbnb--salento-wknd-2-adlt]: https://www.airbnb.com/s/Salento--Quind%C3%ADo--Colombia/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJ5SDE7bySOI4RupnWre7tgY8&location_bb=QJbqasKWxDRAjxuNwpdJCw%3D%3D&acp_id=67370121-2a39-4dd2-8d33-8c8a55504b5a&date_picker_type=flexible_dates&flexible_trip_lengths%5B%5D=weekend_trip&adults=2&search_type=autocomplete_click

## Storybook

Run this later to install Playwright

```sh
pnpm exec playwright install chromium --with-deps
```

### Final output

```log
◇  Storybook setup completed, but some non-blocking errors occurred. Please check
│  the log file below for details.
│
│  To run Storybook, run pnpm run storybook. CTRL+C to stop.
│
│  Official documentation reference: https://storybook.js.org/llms.txt
│
◇  To finalize setting up with AI, paste this prompt to your AI agent:

│  Run `npx storybook ai setup` and follow its instructions precisely.
```
