# Capture Workflow

Use this when a requested Naver Stock page or subpage is not already covered in [api-catalog.md](api-catalog.md).

1. Open the public page in a fresh, non-authenticated browser context.
2. Filter network requests to `stock.naver.com/api/` and ignore static chunks, CSS, telemetry, ads, images, and legacy `finance.naver.com` pages.
3. Keep only GET endpoints or public-looking read POST endpoints that directly answer stock, market, news, research, crypto, or discussion questions.
4. Exclude `auth`, `personal`, `favorite`, `holding`, `notification`, profile mutation, comment write, reaction mutation, and any endpoint that needs cookies or authorization.
5. For Next.js chunk inspection, search downloaded chunks for strings such as `/api/domestic`, `/api/securityService`, `/api/securityFe`, `/api/coin`, `/api/community/discussion`, `/api/domestic/news`, and `/api/domestic/research`.
6. Verify one small direct request with `Accept: application/json` and `Referer: https://stock.naver.com/`.
7. Add the endpoint to the catalog with an observation date and one of these labels: `script-backed`, `observed`, `needs-recheck`, or `excluded`.

Do not save raw HARs, cookies, tokens, or browser storage. Summarize sanitized endpoint patterns instead.
