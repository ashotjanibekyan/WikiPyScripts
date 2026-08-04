"""
Same output as scriptv4.py, but the per-article lookups (English page length,
ru/hy interlanguage targets, ru/hy page lengths) go through Toolforge's SQL
wiki replicas instead of the MediaWiki Action API. That's the only thing this
version changes - parsing, tree building, categorization, and table/wikitext
generation are untouched from v4.

Scope boundary (deliberate, not an oversight): the wiki replicas do not
contain page wikitext, so the source vital-articles list pages are still
fetched via pywikibot (page.text), and saving still goes through pywikibot
(page.save()) when DRY_RUN is off. SQL is used ONLY for page lengths and
langlinks.

Toolforge-only: this needs to run where replica.my.cnf and network access to
*.analytics.db.svc.wikimedia.cloud already exist (a Toolforge job/webservice).
It will not run from a plain workstation.

Known gap, deliberately deferred: like v4, this does not resolve redirects
for individual vital-article titles (a title that is itself a redirect will
be read as the empty/short redirect stub, not the real target). That's a
real bug shared with v3/v4, but fixing it changes output, which would break
the v4-vs-v5 parity diff this version needs to be verified against first.
Fix it as its own separate change once parity is confirmed.
"""

import os
import json
import time
from datetime import datetime
import mwparserfromhell
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

import pywikibot
import toolforge
import pymysql

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

site_en = pywikibot.Site('en', 'wikipedia')
site_hy = pywikibot.Site('hy', 'wikipedia')

# ---- Configuration ----
# While True, results are written to local files instead of being saved to
# Wikipedia, so the output can be reviewed before any real edit is made.
# v5 is unproven against live pages until it's been diffed against v4's
# output for the same category - keep this True until that check is done.
DRY_RUN = True
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output_v5')
CATEGORIES_PATH = os.path.join(SCRIPT_DIR, 'ցանկեր.json')
TRANSLATIONS_PATH = os.path.join(SCRIPT_DIR, 'վերնագրեր.json')

SQL_CHUNK_SIZE = 500


def log(msg: str) -> None:
    """Timestamped, flushed progress line - so a long run still shows
    visible heartbeat instead of going silent for minutes at a time."""
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


@dataclass
class VitalCategory:
    en: str
    hy_long: str
    hy_mid: str
    hy_short: str
    hy_missing: str


@dataclass
class Article:
    """Represents an article entry in a list"""
    en_title: str
    en_length: int
    hy_length: int
    ru_length: int
    hy_title: Optional[str]
    ru_title: Optional[str]
    icon: Optional[str] = None


@dataclass
class Section:
    """Represents a section in the wiki page"""
    title: str
    level: int
    content: str = ""
    articles: List[Article] = field(default_factory=list)
    children: List['Section'] = field(default_factory=list)

    def add_child(self, child: 'Section'):
        self.children.append(child)

    def print_tree(self, indent=0):
        """Print the section tree"""
        print("  " * indent + f"{'=' * self.level} {self.title}")
        for child in self.children:
            child.print_tree(indent + 1)

    def get_all_articles(self) -> List[Article]:
        """Get all articles in this section and all subsections"""
        all_articles = list(self.articles)
        for child in self.children:
            all_articles.extend(child.get_all_articles())
        return all_articles

    def get_all_titles(self) -> List[str]:
        """Get all article titles in this section and all subsections"""
        return list(set([article.en_title for article in self.get_all_articles()]))

    def to_wikitext(self, translations_children: Optional[dict] = None) -> str:
        """Convert section tree back to wikitext.

        `translations_children` is the sibling-lookup dict for THIS section
        at this position in the tree - i.e. the parent's translation node's
        "children" dict, keyed by English heading text. It comes from
        վերնագրեր.json's per-page nested tree (see load_translations), and
        is threaded down through the recursion one level at a time so that
        the same English heading text can resolve to a different Armenian
        translation depending on where in the tree it appears (the whole
        reason the old flat English->Armenian dict was replaced - see
        conversation/design notes, a flat dict can only hold one Armenian
        value per English string, which silently collided whenever the same
        heading text meant something different in a different page/branch).

        Lookup order for this section's own heading: the page-specific node
        for this exact path, if present and non-null; otherwise the global
        `defaults` flat dict (old CSV behavior); otherwise leave untranslated.
        """
        translations_children = translations_children or {}
        my_translation_node = translations_children.get(self.title)

        result = []

        # Check if this section has any content (articles in this section or any subsection)
        has_content = len(self.articles) > 0 or any(child.get_all_articles() for child in self.children)

        # Skip empty sections (except root)
        if not has_content and self.level > 0:
            return ''

        # Add section heading (skip root and lead)
        if self.level > 0 and self.title != "Lead":
            hy_title = None
            if my_translation_node and my_translation_node.get('hy'):
                hy_title = my_translation_node['hy']
            elif self.title in defaults:
                hy_title = defaults[self.title]
            heading = "=" * self.level + " " + str(hy_title if hy_title else self.title) + " " + "=" * self.level
            result.append(heading)

        # Add wikitable if there are articles in THIS section
        if self.articles:
            result.append('{| class="wikitable sortable"')
            result.append(
                '! # !! {{Tooltip|Ա․ կ․|Անգլերեն կարգավիճակ}} !! Անգլերեն (չափ) !! Ռուսերեն (չափ) !! Հայերեն (չափ) !! Ստորագրություն')

            for i, article in enumerate(self.articles, 1):
                row = ['|-']

                # Build table row
                cells = []
                cells.append(f"| {i}")

                # Icon
                if article.icon:
                    cells.append(f"{{{{Icon|{article.icon}}}}}")
                else:
                    cells.append("")

                # English article and length
                cells.append(f"[[:en:{article.en_title}]] ({str(article.en_length)})")

                # Russian article and length
                if article.ru_title:
                    cells.append(f"[[:ru:{article.ru_title}]] ({str(article.ru_length)})")
                else:
                    cells.append("")

                # Armenian article
                if article.hy_title:
                    cells.append(f"[[{article.hy_title}]] ({str(article.hy_length)})")
                else:
                    cells.append("")

                # Signature (empty)
                cells.append("")

                row.append(" || ".join(cells))
                result.extend(row)

            result.append('|}')
            result.append('')  # Empty line after table

        # Add child sections recursively
        child_translations = my_translation_node['children'] if my_translation_node else {}
        for child in self.children:
            child_wikitext = child.to_wikitext(child_translations)
            if child_wikitext:
                result.append(child_wikitext)

        return '\n'.join(result)


def parse_article_list(content: str) -> List[Article]:
    """Parse article list from section content"""
    articles = []

    # Find all list items
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line.startswith('#'):
            continue

        # Parse the line with mwparserfromhell
        line_code = mwparserfromhell.parse(line)

        # Extract icon template
        icon = None
        for template in line_code.filter_templates():
            if str(template.name).strip().lower() == 'icon':
                if template.params:
                    icon = str(template.params[0]).strip()
                break

        # Extract article link
        links = list(line_code.filter_wikilinks())
        if not links:
            continue

        # Find the main article link (usually the longest non-Wikipedia: link)
        article_link = None
        for link in links:
            link_title = str(link.title)
            if not link_title.startswith('Wikipedia:'):
                article_link = link
                break

        if not article_link:
            continue

        title = str(article_link.title).strip()

        articles.append(Article(
            en_title=title,
            en_length=0,
            hy_length=0,
            ru_length=0,
            hy_title=None,
            ru_title=None,
            icon=icon
        ))

    return articles


def parse_wikitext(wikitext: str) -> Section:
    """Parse wikitext and return root section with tree structure"""
    wikicode = mwparserfromhell.parse(wikitext)
    sections = wikicode.get_sections(include_lead=True, include_headings=True, flat=True)

    root = Section(title="Root", level=0)
    stack = [root]

    for i, section in enumerate(sections):
        section_text = str(section).strip()
        if not section_text:
            continue

        headings = section.filter_headings()

        if headings:
            heading = headings[0]
            level = heading.level
            title = heading.title.strip_code().strip()

            # Get only immediate content (exclude subsections)
            content = section_text.replace(str(heading), '', 1).strip()

            node = Section(title=title, level=level, content=content)
            node.articles = parse_article_list(content)
            # Find parent at appropriate level
            while len(stack) > 1 and stack[-1].level >= level:
                stack.pop()

            stack[-1].add_child(node)
            stack.append(node)

        elif i == 0:
            # Lead section
            lead = Section(title="Lead", level=1, content=section_text)
            root.add_child(lead)
            stack.append(lead)

    return root


def load_vital_categories(json_path: str) -> list[VitalCategory]:
    with open(json_path, encoding='utf-8') as f:
        rows = json.load(f)

    return [
        VitalCategory(
            en=row['en'],
            hy_long=row['hy_long'],
            hy_mid=row['hy_mid'],
            hy_short=row['hy_short'],
            hy_missing=row['hy_missing'],
        )
        for row in rows
    ]


vital_categories: list[VitalCategory] = load_vital_categories(CATEGORIES_PATH)


def load_translations(json_path: str) -> dict:
    """{"defaults": {English: Armenian}, "pages": {category.en: {"children": {...nested tree...}}}}
    See the per-page nested tree design: same English heading text can carry
    a different Armenian translation depending on its exact position in a
    given page's tree; "defaults" is the flat fallback used when no
    page-specific override exists for that path."""
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


translations: dict = load_translations(TRANSLATIONS_PATH)
defaults: dict = translations.get('defaults', {})
pages_translations: dict = translations.get('pages', {})


# ---- SQL access (Toolforge wiki replicas) ----
#
# One connection per wiki, opened lazily and reused for the whole run.
# `cluster='analytics'` is the documented choice for batch/bulk queries like
# this one; the 'web' cluster (the default) is meant for short, per-request
# lookups from live tools and shouldn't be hammered with bulk IN-list scans.
# https://wikitech.wikimedia.org/wiki/Help:Toolforge/Database

_connections: Dict[str, "pymysql.connections.Connection"] = {}


def get_conn(dbname: str):
    if dbname not in _connections:
        log(f"  Connecting to {dbname}_p (analytics cluster)...")
        _connections[dbname] = toolforge.connect(dbname, cluster='analytics')
    return _connections[dbname]


def run_query(dbname: str, sql: str, params: tuple) -> tuple:
    """Execute a query, reconnecting once if the replica connection dropped
    (Toolforge replica connections can be closed server-side after periods
    of inactivity or long-running batch jobs)."""
    try:
        conn = get_conn(dbname)
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
        log(f"  SQL connection to {dbname}_p dropped ({e}); reconnecting...")
        _connections.pop(dbname, None)
        conn = get_conn(dbname)
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def close_connections() -> None:
    for conn in _connections.values():
        try:
            conn.close()
        except Exception:
            pass
    _connections.clear()


def decode(value) -> str:
    """page_title/ll_title/ll_lang are varbinary columns - PyMySQL returns
    those as bytes rather than str since they're binary-collated, not
    text-charset."""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return value


def to_db_title(title: str) -> str:
    """page.page_title is stored with spaces replaced by underscores."""
    return title.strip().replace(' ', '_')


def from_db_title(title) -> str:
    return decode(title).replace('_', ' ')


def chunked(items: List, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def fetch_en_data(titles: List[str]) -> Tuple[Dict[str, int], Dict[str, str], Dict[str, str]]:
    """For each English title: its page length, plus its ru/hy langlink
    targets - one SELECT per chunk against `page`, one against `langlinks`
    joined to `page`. Confirmed empirically (Quarry) that enwiki's local
    langlinks table does carry the Wikidata-derived ru/hy targets, so no
    separate hop through wikidatawiki_p/wb_items_per_site is needed."""
    lengths: Dict[str, int] = {}
    ru_targets: Dict[str, str] = {}
    hy_targets: Dict[str, str] = {}

    total_chunks = (len(titles) + SQL_CHUNK_SIZE - 1) // SQL_CHUNK_SIZE
    for idx, chunk in enumerate(chunked(titles, SQL_CHUNK_SIZE), 1):
        db_titles = [to_db_title(t) for t in chunk]
        log(f"    [enwiki] chunk {idx}/{total_chunks} ({len(chunk)} titles)...")
        start = time.monotonic()

        rows = run_query(
            'enwiki',
            "SELECT page_title, page_len FROM page "
            "WHERE page_namespace = 0 AND page_title IN %s",
            (tuple(db_titles),),
        )
        for db_title, length in rows:
            lengths[from_db_title(db_title)] = length

        rows = run_query(
            'enwiki',
            "SELECT page.page_title, langlinks.ll_lang, langlinks.ll_title "
            "FROM langlinks "
            "JOIN page ON langlinks.ll_from = page.page_id "
            "WHERE page.page_namespace = 0 "
            "AND page.page_title IN %s "
            "AND langlinks.ll_lang IN ('ru', 'hy')",
            (tuple(db_titles),),
        )
        for db_title, lang, ll_title in rows:
            title = from_db_title(db_title)
            lang = decode(lang)
            if lang == 'ru':
                ru_targets[title] = decode(ll_title)
            elif lang == 'hy':
                hy_targets[title] = decode(ll_title)

        log(f"    [enwiki] chunk {idx}/{total_chunks} done in {time.monotonic() - start:.1f}s")

    return lengths, ru_targets, hy_targets


def fetch_lengths(dbname: str, titles: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    if not titles:
        return result

    total_chunks = (len(titles) + SQL_CHUNK_SIZE - 1) // SQL_CHUNK_SIZE
    for idx, chunk in enumerate(chunked(titles, SQL_CHUNK_SIZE), 1):
        db_titles = [to_db_title(t) for t in chunk]
        log(f"    [{dbname}] lengths chunk {idx}/{total_chunks} ({len(chunk)} titles)...")
        start = time.monotonic()

        rows = run_query(
            dbname,
            "SELECT page_title, page_len FROM page "
            "WHERE page_namespace = 0 AND page_title IN %s",
            (tuple(db_titles),),
        )
        for db_title, length in rows:
            result[from_db_title(db_title)] = length

        log(f"    [{dbname}] chunk {idx}/{total_chunks} done in {time.monotonic() - start:.1f}s")

    return result


def resolve_articles(titles: List[str], cache: Dict[str, Article]) -> None:
    """Populate `cache` with a fully-resolved Article for every title not
    already present. Shared across categories within a run, so an English
    article that appears in more than one vital-articles list is only ever
    fetched once."""
    to_fetch = [t for t in titles if t not in cache]
    cached_hits = len(titles) - len(to_fetch)
    log(f"  {len(titles)} articles total, {cached_hits} already cached, {len(to_fetch)} to fetch")
    if not to_fetch:
        return

    log(f"  Step 1/3: en length + ru/hy langlinks for {len(to_fetch)} titles (SQL)")
    en_lengths, ru_targets, hy_targets = fetch_en_data(to_fetch)

    missed = [t for t in to_fetch if t not in en_lengths]
    if missed:
        sample = missed[:10]
        log(f"  WARNING: {len(missed)} of {len(to_fetch)} titles got no enwiki page-length row "
            f"(title-normalization mismatch, or the page genuinely doesn't exist / is a redirect "
            f"we didn't resolve). Sample: {sample}")

    ru_titles = list(set(ru_targets.values()))
    hy_titles = list(set(hy_targets.values()))

    log(f"  Step 2/3: ru lengths for {len(ru_titles)} titles (SQL)")
    ru_sizes = fetch_lengths('ruwiki', ru_titles)
    log(f"  Step 3/3: hy lengths for {len(hy_titles)} titles (SQL)")
    hy_sizes = fetch_lengths('hywiki', hy_titles)

    for title in to_fetch:
        ru_title = ru_targets.get(title)
        hy_title = hy_targets.get(title)
        cache[title] = Article(
            en_title=title,
            en_length=en_lengths.get(title, 0),
            ru_title=ru_title,
            ru_length=ru_sizes.get(ru_title, 0) if ru_title else 0,
            hy_title=hy_title,
            hy_length=hy_sizes.get(hy_title, 0) if hy_title else 0,
        )


def categorize_article_by_hy_length(article: Article) -> str:
    """Categorize article based on Armenian version length"""
    if article.hy_title is None:
        return "missing"
    elif article.hy_length < 8000:
        return "short"
    elif article.hy_length < 16000:
        return "mid"
    else:
        return "long"


def split_tree_by_hy_status(root: Section, category: VitalCategory) -> Dict[str, Section]:
    """Split the section tree into four categories based on Armenian article status"""
    # Create four new root sections
    categories = {
        "long": Section(title=category.hy_long, level=-1),
        "mid": Section(title=category.hy_mid, level=-1),
        "short": Section(title=category.hy_short, level=-1),
        "missing": Section(title=category.hy_missing, level=-1)
    }

    def clone_section_structure(section: Section, parent_category: str) -> Optional[Section]:
        """Recursively clone section structure, filtering articles by category"""
        # Filter articles for this section that belong to the target category
        filtered_articles = [
            article for article in section.articles
            if categorize_article_by_hy_length(article) == parent_category
        ]

        # Clone children recursively
        cloned_children = []
        for child in section.children:
            cloned_child = clone_section_structure(child, parent_category)
            if cloned_child:
                cloned_children.append(cloned_child)

        # Only create section if it has articles or non-empty children
        if filtered_articles or cloned_children:
            cloned = Section(
                title=section.title,
                level=section.level,
                content=section.content,
                articles=filtered_articles,
                children=cloned_children
            )
            return cloned
        return None

    # Process each child of root into the four categories
    for child in root.children:
        for cat_name in ["long", "mid", "short", "missing"]:
            cloned = clone_section_structure(child, cat_name)
            if cloned:
                categories[cat_name].add_child(cloned)

    return categories


def update_tree(category: VitalCategory, cache: Dict[str, Article]) -> Dict[str, Section]:
    log(f"  Fetching source list page: {category.en}")
    page = pywikibot.Page(site_en, category.en)
    result = parse_wikitext(page.text)
    titles = result.get_all_titles()
    log(f"  Parsed {len(titles)} unique article titles")

    resolve_articles(titles, cache)

    # Apply the (possibly cached) resolved data onto this tree's articles.
    # Icon comes from the parse step above and must be kept as-is.
    for article in result.get_all_articles():
        resolved = cache[article.en_title]
        article.en_length = resolved.en_length
        article.ru_title = resolved.ru_title
        article.ru_length = resolved.ru_length
        article.hy_title = resolved.hy_title
        article.hy_length = resolved.hy_length

    # Split the tree into four categories
    return split_tree_by_hy_status(result, category)


def save_or_write(hy_page: pywikibot.Page, wikitext: str) -> None:
    """Persist `wikitext` for `hy_page`. In DRY_RUN mode this writes a local
    file named after the target page instead of touching the live wiki, so
    results can be reviewed/tested before any real edit is made. Also skips
    writing/saving when there is nothing to write, instead of blanking a
    live page that simply has no articles in this category this run."""
    if not wikitext:
        return

    if DRY_RUN:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        safe_name = hy_page.title().replace('/', '__') + '.txt'
        path = os.path.join(OUTPUT_DIR, safe_name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(wikitext)
        print(f"[DRY RUN] Wrote {path}")
    else:
        hy_page.text = wikitext
        hy_page.save(summary="Թարմացում")


def main():
    cache: Dict[str, Article] = {}
    total = len(vital_categories)

    try:
        for idx, category in enumerate(vital_categories, 1):
            log(f"Category {idx}/{total}: {category.en}")
            start = time.monotonic()
            categories = update_tree(category, cache)

            # Same starting translation node for all four long/mid/short/missing
            # splits of this category, since they're all derived from the same
            # source page's heading tree (see split_tree_by_hy_status - titles
            # are preserved as-is from the original parse, so the paths still
            # match the page's entry in վերնագրեր.json).
            page_translations_root = pages_translations.get(category.en, {}).get('children', {})

            for cat_name in ["long", "mid", "short", "missing"]:
                section = categories[cat_name]
                wikitext = section.to_wikitext(page_translations_root)
                hy_page = pywikibot.Page(site_hy, section.title)
                save_or_write(hy_page, wikitext)
                if wikitext:
                    print(wikitext)
                    print()

            log(f"Category {idx}/{total} done in {time.monotonic() - start:.1f}s")
            print("=" * 80)
            print()

        log(f"All {total} categories done. Cache holds {len(cache)} resolved articles.")
    finally:
        close_connections()


main()
