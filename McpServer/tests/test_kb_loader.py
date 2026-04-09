from pathlib import Path

from systemix_mcp_server.kb_loader import SEED_SOURCE_FILES, load_seed_documents


def test_load_seed_documents_reads_expected_record_counts() -> None:
    seed_directory = Path(__file__).resolve().parents[1] / "kb"

    documents = load_seed_documents(seed_directory)

    counts_by_file = {filename: 0 for filename in SEED_SOURCE_FILES}
    for source_file, _document in documents:
        counts_by_file[source_file] += 1

    assert counts_by_file["account_and_login.txt"] >= 50
    assert counts_by_file["payments.txt"] >= 50
    assert counts_by_file["shipping_and_orders.txt"] >= 50
    assert counts_by_file["returns_and_refunds.txt"] >= 50
    assert counts_by_file["product_usage.txt"] >= 200
