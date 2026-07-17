#!/usr/bin/env python3
"""Fetch read-only Naver Stock discussion payloads."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from typing import Any

from naverstock_api import (
    bounded_int,
    build_path,
    emit_output,
    normalize_item_code,
    render_json,
    request_json,
    validate_identifier,
)


MAX_COMMUNITY_ITEMS = 100
MAX_COMMUNITY_FIELDS = 200
MAX_COMMUNITY_DEPTH = 16
MAX_COMMUNITY_TEXT_LENGTH = 20_000
_PRIVATE_FIELD_NAMES = frozenset(
    {
        "accountid",
        "authorid",
        "authorimageurl",
        "avatarurl",
        "memberid",
        "memberno",
        "profileid",
        "profileimageurl",
        "profilelink",
        "profileno",
        "profiletype",
        "profileurl",
        "userid",
        "userno",
        "viewerprofileid",
        "writerid",
        "uno",
    }
)
_PRIVATE_VIEWER_FIELDS = frozenset(
    {
        "isblocked",
        "isfollowing",
        "ismuted",
        "viewerreaction",
    }
)
_URL_PATTERN = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
_EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?82[- .]?)?0?1[016789][- .]?\d{3,4}[- .]?\d{4}(?!\d)")


def sanitize_community_payload(payload: Any) -> Any:
    """Remove profile identifiers and redact contact links from community data."""

    return _sanitize_community_value(payload, depth=0, parent_key="")


def _sanitize_community_value(value: Any, *, depth: int, parent_key: str) -> Any:
    if depth >= MAX_COMMUNITY_DEPTH:
        return "[truncated]"
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, nested in list(value.items())[:MAX_COMMUNITY_FIELDS]:
            normalized_key = re.sub(r"[-_.\s]", "", str(key)).casefold()
            if _is_private_community_field(normalized_key, parent_key=parent_key):
                continue
            clean[key] = _sanitize_community_value(
                nested,
                depth=depth + 1,
                parent_key=normalized_key,
            )
        return clean
    if isinstance(value, (list, tuple)):
        return [
            _sanitize_community_value(item, depth=depth + 1, parent_key=parent_key)
            for item in value[:MAX_COMMUNITY_ITEMS]
        ]
    if isinstance(value, str):
        text = _URL_PATTERN.sub("[redacted-url]", value)
        text = _EMAIL_PATTERN.sub("[redacted-email]", text)
        text = _PHONE_PATTERN.sub("[redacted-phone]", text)
        if len(text) > MAX_COMMUNITY_TEXT_LENGTH:
            return text[:MAX_COMMUNITY_TEXT_LENGTH] + "…[truncated]"
        return text
    return value


def _is_private_community_field(normalized_key: str, *, parent_key: str) -> bool:
    if normalized_key in _PRIVATE_FIELD_NAMES or normalized_key in _PRIVATE_VIEWER_FIELDS:
        return True
    if normalized_key.startswith("viewer"):
        return True
    identity_subjects = ("account", "author", "avatar", "member", "profile", "user", "writer")
    generic_identity_fields = {
        "id",
        "image",
        "imageurl",
        "link",
        "no",
        "photo",
        "type",
        "uid",
        "uno",
        "uri",
        "url",
        "uuid",
    }
    if any(subject in parent_key for subject in identity_subjects) and normalized_key in generic_identity_fields:
        return True
    if not any(subject in normalized_key for subject in identity_subjects):
        return False
    return re.search(r"(?:id|image|link|no|photo|type|uid|uri|url|uuid)(?:hash|token)?$", normalized_key) is not None


def _page(value: str) -> int:
    try:
        return bounded_int(value, name="page", minimum=1, maximum=1_000)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _page_size(value: str) -> int:
    try:
        return bounded_int(value, name="page-size", minimum=1, maximum=MAX_COMMUNITY_ITEMS)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _post_id(value: str) -> str:
    try:
        return validate_identifier(value, name="post-id")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _cursor(value: str) -> str:
    clean = value.strip()
    if not clean or len(clean) > 512 or re.search(r"[^A-Za-z0-9._~+=:/-]", clean):
        raise argparse.ArgumentTypeError("offset must be a URL-safe cursor of at most 512 characters")
    return clean


def _iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("start-date must be a valid YYYY-MM-DD date") from exc


def fetch_hot_home(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/community/discussion/posts/hot/home", {"pageSize": args.page_size, "page": args.page})
    )


def fetch_post(args: argparse.Namespace) -> Any:
    return request_json(f"/api/community/discussion/posts/{args.post_id}")


def fetch_adjacent(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/community/discussion/posts/{args.post_id}/adjacent",
            {
                "itemCode": args.item_code,
                "pageSize": args.page_size,
                "discussionGroupType": args.discussion_group_type,
                "excludesItemNews": args.excludes_item_news,
                "isItemNewsOnly": args.is_item_news_only,
                "excludesBlockPost": args.excludes_block_post,
            },
        )
    )


def fetch_related_hot(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/related/hot",
            {"itemCode": args.item_code, "pageSize": args.page_size, "discussionType": args.discussion_type},
        )
    )


def fetch_popular_hot(args: argparse.Namespace) -> Any:
    return request_json("/api/community/discussion/posts/popular/hot")


def fetch_feed(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts",
            {
                "pageSize": args.page_size,
                "offset": args.offset,
                "discussionGroupType": args.discussion_group_type,
            },
        )
    )


def fetch_market_feed(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/market",
            {
                "filterType": args.filter_type,
                "pageSize": args.page_size,
                "offset": args.offset,
                "discussionGroupType": args.discussion_group_type,
            },
        )
    )


def fetch_item_posts(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/by-item",
            {
                "itemCode": normalize_item_code(args.item_code),
                "discussionType": args.discussion_type,
                "pageSize": args.page_size,
                "offset": args.offset,
                "isHolderOnly": args.is_holder_only,
                "excludesItemNews": args.excludes_item_news,
                "isItemNewsOnly": args.is_item_news_only,
            },
        )
    )


def fetch_stats_by_items(args: argparse.Namespace) -> Any:
    domestic_codes = ",".join(normalize_item_code(code) for code in args.domestic_codes) if args.domestic_codes else None
    foreign_codes = ",".join(args.foreign_codes) if args.foreign_codes else None
    return request_json(
        build_path(
            "/api/community/discussion/stats/by-items",
            {
                "startDate": args.start_date,
                "domesticCodes": domestic_codes,
                "foreignCodes": foreign_codes,
            },
        )
    )


def fetch_rankings(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/rankings",
            {
                "nationType": args.nation_type,
                "page": args.page,
                "size": args.size,
                "postType": args.post_type,
            },
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    hot = sub.add_parser("hot-home", help="Home hot discussion posts")
    hot.add_argument("--page", type=_page, default=1)
    hot.add_argument("--page-size", type=_page_size, default=20)
    hot.add_argument("--output")
    hot.set_defaults(func=fetch_hot_home)

    post = sub.add_parser("post", help="Discussion post detail")
    post.add_argument("--post-id", type=_post_id, required=True)
    post.add_argument("--output")
    post.set_defaults(func=fetch_post)

    adjacent = sub.add_parser("adjacent", help="Adjacent posts around a detail post")
    adjacent.add_argument("--post-id", type=_post_id, required=True)
    adjacent.add_argument("--item-code")
    adjacent.add_argument("--page-size", type=_page_size, default=20)
    adjacent.add_argument("--discussion-group-type")
    adjacent.add_argument("--excludes-item-news", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--is-item-news-only", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--excludes-block-post", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--output")
    adjacent.set_defaults(func=fetch_adjacent)

    related = sub.add_parser("related-hot", help="Related hot discussion posts for an item")
    related.add_argument("--item-code", required=True)
    related.add_argument("--page-size", type=_page_size, default=20)
    related.add_argument("--discussion-type", default="domesticStock")
    related.add_argument("--output")
    related.set_defaults(func=fetch_related_hot)

    popular = sub.add_parser("popular-hot", help="Popular hot discussion posts")
    popular.add_argument("--output")
    popular.set_defaults(func=fetch_popular_hot)

    feed = sub.add_parser("feed", help="General discussion feed")
    feed.add_argument("--page-size", type=_page_size, default=20)
    feed.add_argument("--offset", type=_cursor)
    feed.add_argument("--discussion-group-type")
    feed.add_argument("--output")
    feed.set_defaults(func=fetch_feed)

    market_feed = sub.add_parser("market-feed", help="Market discussion feed")
    market_feed.add_argument("--filter-type", default="marketIndex")
    market_feed.add_argument("--page-size", type=_page_size, default=20)
    market_feed.add_argument("--offset", type=_cursor)
    market_feed.add_argument("--discussion-group-type")
    market_feed.add_argument("--output")
    market_feed.set_defaults(func=fetch_market_feed)

    item_posts = sub.add_parser("item-posts", help="Discussion posts for an item")
    item_posts.add_argument("--item-code", required=True)
    item_posts.add_argument("--discussion-type", default="domesticStock")
    item_posts.add_argument("--page-size", type=_page_size, default=20)
    item_posts.add_argument("--offset", type=_cursor)
    item_posts.add_argument("--is-holder-only", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--excludes-item-news", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--is-item-news-only", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--output")
    item_posts.set_defaults(func=fetch_item_posts)

    stats = sub.add_parser("stats-by-items", help="Discussion statistics for domestic or foreign item codes")
    stats.add_argument("--start-date", type=_iso_date, required=True)
    stats.add_argument("--domestic-codes", action="append", help="Repeat for each domestic item code")
    stats.add_argument("--foreign-codes", action="append", help="Repeat for each foreign code")
    stats.add_argument("--output")
    stats.set_defaults(func=fetch_stats_by_items)

    rankings = sub.add_parser("rankings", help="Discussion item rankings")
    rankings.add_argument("--nation-type", choices=["KOR", "USA"], default="KOR")
    rankings.add_argument("--page", type=_page, default=1)
    rankings.add_argument("--page-size", type=_page_size, default=20, dest="size")
    rankings.add_argument("--post-type", choices=["HOT", "LATEST"], default="HOT")
    rankings.add_argument("--output")
    rankings.set_defaults(func=fetch_rankings)

    args = parser.parse_args()
    emit_output(render_json(sanitize_community_payload(args.func(args))), args.output)


if __name__ == "__main__":
    main()
