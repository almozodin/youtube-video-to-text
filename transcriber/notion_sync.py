from __future__ import annotations

import os
from typing import Any

import requests

NOTION_VERSION = "2022-06-28"
BLOCK_TEXT_LIMIT = 1900


def _chunk_text(text: str, size: int = BLOCK_TEXT_LIMIT) -> list[str]:
    chunks: list[str] = []
    current = ""
    for line in text.splitlines():
        if len(current) + len(line) + 1 > size:
            if current:
                chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def create_notion_page(
    title: str,
    source_url: str,
    model: str,
    language: str | None,
    transcript_text: str,
    parent_page_id: str | None = None,
) -> str:
    notion_token = os.getenv("NOTION_TOKEN")
    parent_id = parent_page_id or os.getenv("NOTION_PARENT_PAGE_ID")
    if not notion_token or not parent_id:
        raise ValueError("Missing Notion credentials. Set NOTION_TOKEN and NOTION_PARENT_PAGE_ID.")

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    blocks: list[dict[str, Any]] = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Source: {source_url}"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Model: {model}"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"Language: {language or 'auto'}"}}]
            },
        },
    ]

    for chunk in _chunk_text(transcript_text):
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]},
            }
        )

    payload: dict[str, Any] = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}},
        "children": blocks,
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=30)
    if response.status_code >= 400:
        raise RuntimeError(f"Notion API error ({response.status_code}): {response.text}")
    data = response.json()
    return data.get("url", "")
