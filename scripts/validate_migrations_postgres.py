from __future__ import annotations
import argparse
import ast
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "migrations" / "versions"

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def blocker(filename: str, line: int, message: str) -> None:
    BLOCKERS.append(f"[BLOCKER] {filename}:{line} - {message}")

def warning(filename: str, line: int, message: str) -> None:
    WARNINGS.append(f"[WARNING] {filename}:{line} - {message}")


# ---------------------------------------------------------------------------
# Revision metadata
# ---------------------------------------------------------------------------

def extract_revision_metadata(path: Path) -> tuple[str | None, str | None]:
    text = path.read_text(encoding="utf-8")

    revision_match = re.search(
        r"^\s*revision\s*=\s*['\"]([^'\"]+)['\"]",
        text,
        re.MULTILINE,
    )

    down_revision_match = re.search(
        r"^\s*down_revision\s*=\s*['\"]([^'\"]+)['\"]",
        text,
        re.MULTILINE,
    )

    revision = revision_match.group(1) if revision_match else None
    down_revision = (
        down_revision_match.group(1)
        if down_revision_match
        else None
    )

    return revision, down_revision


def build_chain(
    migrations: list[tuple[Path, str, str | None]],
) -> list[tuple[Path, str]]:
    by_revision = {
        revision: (path, down_revision)
        for path, revision, down_revision in migrations
    }

    children: dict[str | None, list[str]] = {}

    for revision, (_, down_revision) in by_revision.items():
        children.setdefault(down_revision, []).append(revision)

    roots = children.get(None, [])

    if len(roots) != 1:
        blocker(
            "<chain>",
            0,
            f"expected exactly one Alembic root, found {len(roots)}: {roots}",
        )
        return []

    chain: list[tuple[Path, str]] = []

    current = roots[0]
    visited: set[str] = set()

    while current:
        if current in visited:
            blocker(
                "<chain>",
                0,
                f"Alembic migration cycle detected at revision '{current}'.",
            )
            return chain

        visited.add(current)

        if current not in by_revision:
            blocker(
                "<chain>",
                0,
                f"migration revision '{current}' is referenced but no file exists.",
            )
            return chain

        path, _ = by_revision[current]
        chain.append((path, current))

        next_revisions = children.get(current, [])

        if len(next_revisions) > 1:
            blocker(
                "<chain>",
                0,
                f"migration revision '{current}' has multiple children: "
                f"{next_revisions}",
            )
            return chain

        if not next_revisions:
            break

        current = next_revisions[0]

    all_revisions = set(by_revision)
    chained_revisions = {revision for _, revision in chain}

    unreachable = sorted(all_revisions - chained_revisions)

    if unreachable:
        blocker(
            "<chain>",
            0,
            "unreachable migration revisions detected: "
            + ", ".join(unreachable),
        )

    return chain


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def get_call_name(node: ast.Call) -> str:
    func = node.func

    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            return f"{func.value.id}.{func.attr}"

        return func.attr

    if isinstance(func, ast.Name):
        return func.id

    return ""


def get_string_arg(node: ast.Call, index: int = 0) -> str | None:
    if len(node.args) <= index:
        return None

    value = node.args[index]

    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value

    return None


def walk_calls(tree: ast.AST) -> Iterable[ast.Call]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield node


# ---------------------------------------------------------------------------
# Static checks
# ---------------------------------------------------------------------------

def check_revision_file(path: Path) -> None:
    filename = path.name
    text = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        blocker(
            filename,
            exc.lineno or 0,
            f"Python syntax error: {exc.msg}",
        )
        return

    lines = text.splitlines()

    # ---------------------------------------------------------------
    # 1. Explicit SQLite-only migrations
    # ---------------------------------------------------------------

    sqlite_only_markers = (
        "supports SQLite only",
        "designed specifically for SQLite",
        "SQLite only",
    )

    has_sqlite_only_message = any(
        marker in text
        for marker in sqlite_only_markers
    )

    has_non_sqlite_raise = bool(
        re.search(
            r'if\s+[^:\n]*dialect\.name\s*!=\s*["\']sqlite["\'][^:]*:\s*'
            r'(?:\n[ \t]+.*){0,8}raise\s+RuntimeError',
            text,
        )
    )

    # A migration which explicitly rejects PostgreSQL is a real blocker
    # unless the upgrade path returns before that code executes.
    has_postgres_return = bool(
        re.search(
            r'if\s+[^:\n]*dialect\.name\s*!=\s*["\']sqlite["\'][^:]*:\s*'
            r'(?:\n[ \t]+.*){0,5}return\b',
            text,
        )
    )

    if has_sqlite_only_message and has_non_sqlite_raise:
        if not has_postgres_return:
            line = next(
                (
                    i
                    for i, value in enumerate(lines, start=1)
                    if "SQLite only" in value
                    or "specifically for SQLite" in value
                ),
                1,
            )

            blocker(
                filename,
                line,
                "migration explicitly rejects non-SQLite databases; "
                "PostgreSQL deployment will fail unless upgrade() returns "
                "before the SQLite-only code.",
            )

    # ---------------------------------------------------------------
    # 2. SQLite PRAGMA usage
    # ---------------------------------------------------------------

    for i, line in enumerate(lines, start=1):
        if re.search(r"\bPRAGMA\s+", line, re.IGNORECASE):
            warning(
                filename,
                i,
                "SQLite PRAGMA detected; verify this code is unreachable "
                "on PostgreSQL.",
            )

    # ---------------------------------------------------------------
    # 3. SQLite catalog usage
    # ---------------------------------------------------------------

    for i, line in enumerate(lines, start=1):
        if "sqlite_master" in line:
            warning(
                filename,
                i,
                "SQLite sqlite_master catalog query detected; verify "
                "this code is unreachable on PostgreSQL.",
            )

    # ---------------------------------------------------------------
    # 4. SQLite-specific SQL functions
    # ---------------------------------------------------------------

    sqlite_functions = (
        "randomblob(",
        "hex(",
        "datetime(",
        "strftime(",
        "julianday(",
    )

    for i, line in enumerate(lines, start=1):
        lower = line.lower()

        for function in sqlite_functions:
            if function in lower:
                warning(
                    filename,
                    i,
                    f"SQLite-specific SQL function detected: {function}",
                )

    # ---------------------------------------------------------------
    # 5. Boolean defaults
    #
    # PostgreSQL requires boolean expressions such as TRUE/FALSE
    # rather than integer defaults such as 0/1.
    #
    # IMPORTANT:
    # Only flag 0/1 defaults when the column is actually declared
    # as sa.Boolean(). Integer columns legitimately use 0/1 defaults.
    # ---------------------------------------------------------------

    boolean_column_pattern = re.compile(
        r"""
        sa\.Column\(
            .*?
            sa\.Boolean
        """,
        re.IGNORECASE | re.VERBOSE | re.DOTALL,
    )

    boolean_default_pattern = re.compile(
        r"""
        server_default\s*=\s*
        (?:
            sa\.text\(\s*['"](?:0|1)['"]\s*\)
            |
            ['"](?:0|1)['"]
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # Inspect each Column(...) block rather than individual lines so
    # the validator can distinguish Boolean defaults from Integer
    # defaults.
    column_start_pattern = re.compile(
        r"\bsa\.Column\s*\(",
        re.IGNORECASE,
    )

    for start_index, line in enumerate(lines):
        if not column_start_pattern.search(line):
            continue

        # Collect the complete Column(...) expression, accounting for
        # nested parentheses.
        block = []
        depth = 0
        started = False
        end_index = start_index

        for j in range(start_index, len(lines)):
            current_line = lines[j]
            block.append(current_line)

            depth += current_line.count("(")
            depth -= current_line.count(")")

            if "sa.Column" in current_line:
                started = True

            if started and depth <= 0:
                end_index = j
                break

        column_text = "".join(block)

        if (
            boolean_column_pattern.search(column_text)
            and boolean_default_pattern.search(column_text)
        ):
            blocker(
                filename,
                start_index + 1,
                "PostgreSQL boolean column uses integer default 0/1; "
                "use TRUE/FALSE or sa.text('true'/'false').",
            )

    # ---------------------------------------------------------------
    # 6. Hard-coded constraint names
    #
    # These are warnings, not automatic blockers.
    # ---------------------------------------------------------------

    for i, line in enumerate(lines, start=1):
        if "batch_op.drop_constraint(" in line:
            if not "batch_op.f(" in line:
                warning(
                    filename,
                    i,
                    "hard-coded batch_op.drop_constraint() name; "
                    "PostgreSQL may use a different generated constraint name.",
                )

    # ---------------------------------------------------------------
    # 7. Raw SQL
    # ---------------------------------------------------------------

    for i, line in enumerate(lines, start=1):
        if "op.execute(" in line or "connection.exec_driver_sql(" in line:
            warning(
                filename,
                i,
                "raw SQL execution detected; verify PostgreSQL compatibility.",
            )

    # ---------------------------------------------------------------
    # 8. Explicit SQLite connection checks
    # ---------------------------------------------------------------

    for i, line in enumerate(lines, start=1):
        if "dialect.name" in line and "sqlite" in line.lower():
            warning(
                filename,
                i,
                "explicit SQLite dialect guard detected; verify the "
                "PostgreSQL execution path.",
            )

    # ---------------------------------------------------------------
    # 9. Obvious PostgreSQL-invalid SQLite SQL
    # ---------------------------------------------------------------

    sqlite_sql_patterns = (
        r"\bPRAGMA\b",
        r"\bsqlite_master\b",
        r"\brandomblob\s*\(",
    )

    for pattern in sqlite_sql_patterns:
        compiled = re.compile(pattern, re.IGNORECASE)

        for i, line in enumerate(lines, start=1):
            if compiled.search(line):
                # Already reported above; don't duplicate.
                pass

    # ---------------------------------------------------------------
    # 10. AST sanity checks for create/alter operations.
    #
    # We intentionally DO NOT attempt to reconstruct complete schema
    # ordering here. SQLAlchemy/Alembic constructs are multiline and can
    # contain nested calls which make regex-based FK/table reconstruction
    # unreliable.
    # ---------------------------------------------------------------

    for call in walk_calls(tree):
        name = get_call_name(call)

        if name == "op.create_table":
            table_name = get_string_arg(call)

            if not table_name:
                warning(
                    filename,
                    getattr(call, "lineno", 0),
                    "op.create_table() call could not be statically "
                    "identified; manual review required.",
                )

        elif name == "op.batch_alter_table":
            table_name = get_string_arg(call)

            if not table_name:
                warning(
                    filename,
                    getattr(call, "lineno", 0),
                    "batch_alter_table() table name could not be "
                    "statically identified.",
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate TUR Alembic migrations for PostgreSQL hazards."
    )

    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="show warnings in addition to blockers",
    )

    args = parser.parse_args()

    print("=" * 78)
    print("THE UNCHARTED ROUTE — PostgreSQL Migration Preflight")
    print("=" * 78)
    print()

    files = sorted(MIGRATIONS_DIR.glob("*.py"))

    migrations: list[tuple[Path, str, str | None]] = []

    for path in files:
        revision, down_revision = extract_revision_metadata(path)

        if not revision:
            blocker(
                path.name,
                1,
                "migration file has no revision identifier.",
            )
            continue

        migrations.append(
            (path, revision, down_revision)
        )

    print(f"Migration files discovered: {len(files)}")
    print(f"Migration chain candidates : {len(migrations)}")

    chain = build_chain(migrations)

    if chain:
        print(
            "Actual Alembic chain       : "
            f"{chain[0][1]} -> ... -> {chain[-1][1]}"
        )
    else:
        print("Actual Alembic chain       : unavailable")

    print()

    for path, _revision in chain:
        check_revision_file(path)

    # Files not reachable from the root still need basic syntax/content
    # checks, but are not treated as part of the active chain.
    chained_paths = {path.resolve() for path, _ in chain}

    for path, _revision, _down_revision in migrations:
        if path.resolve() not in chained_paths:
            check_revision_file(path)

    print("=" * 78)
    print("RESULTS")
    print("=" * 78)
    print()

    print("BLOCKERS")
    print("-" * 78)

    if BLOCKERS:
        for item in BLOCKERS:
            print(item)
    else:
        print("None")

    if args.show_warnings:
        print()
        print("WARNINGS")
        print("-" * 78)

        if WARNINGS:
            for item in WARNINGS:
                print(item)
        else:
            print("None")

    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"Migrations scanned : {len(files)}")
    print(f"Blockers           : {len(BLOCKERS)}")
    print(f"Warnings           : {len(WARNINGS)}")

    if BLOCKERS:
        print()
        print("RESULT: FAIL — confirmed PostgreSQL migration blockers found.")
        return 1

    print()
    print("RESULT: PASS — no confirmed PostgreSQL migration blockers found.")
    return 0


BLOCKERS: list[str] = []
WARNINGS: list[str] = []


if __name__ == "__main__":
    raise SystemExit(main())
