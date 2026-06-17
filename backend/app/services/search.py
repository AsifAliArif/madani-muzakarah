import meilisearch

from app.config import settings
from app.schemas import NoteOut

INDEX_NAME = "notes"


def get_client() -> meilisearch.Client | None:
    try:
        return meilisearch.Client(settings.meilisearch_url, settings.meilisearch_api_key)
    except Exception:
        return None


def ensure_index():
    client = get_client()
    if not client:
        return
    try:
        client.get_index(INDEX_NAME)
    except Exception:
        client.create_index(INDEX_NAME, {"primaryKey": "id"})
        index = client.index(INDEX_NAME)
        index.update_searchable_attributes(["title", "content_plain", "author_name", "categories"])
        index.update_filterable_attributes(["status", "categories"])


def index_note(note_out: NoteOut):
    client = get_client()
    if not client:
        return
    ensure_index()
    doc = {
        "id": str(note_out.id),
        "title": note_out.display_title,
        "content_plain": note_out.content_plain,
        "author_name": note_out.author_name,
        "categories": [c.name for c in note_out.categories],
        "status": note_out.status,
    }
    client.index(INDEX_NAME).add_documents([doc])


def remove_note(note_id: str):
    client = get_client()
    if not client:
        return
    try:
        client.index(INDEX_NAME).delete_document(note_id)
    except Exception:
        pass


def search_notes(
    query: str,
    mode: str = "broad",
    terms: list[str] | None = None,
    status: str = "active",
) -> tuple[list[str], int]:
    client = get_client()
    if not client:
        return [], 0
    ensure_index()
    index = client.index(INDEX_NAME)

    filters = [f'status = "{status}"']
    filter_str = " AND ".join(filters)

    search_query = query
    opts: dict = {"filter": filter_str, "limit": 50}

    if mode == "exact" and query:
        search_query = f'"{query}"'
    elif mode == "phrase" and query:
        search_query = f'"{query}"'
    elif mode == "word":
        opts["matchingStrategy"] = "all"

    if terms:
        for term in terms:
            if term.strip():
                search_query = f"{search_query} {term}".strip()

    try:
        result = index.search(search_query or "", opts)
        hits = result.get("hits", [])
        ids = [h["id"] for h in hits]
        return ids, result.get("estimatedTotalHits", len(ids))
    except Exception:
        return [], 0
