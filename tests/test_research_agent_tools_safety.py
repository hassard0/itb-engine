from itb.research_agent.tools import compute_intersection, read_findings_doc


def test_read_findings_doc_rejects_path_traversal():
    result = read_findings_doc("../../pyproject.toml")
    assert "error" in result
    assert "docs/results" in result["error"]


def test_read_findings_doc_accepts_result_filename():
    result = read_findings_doc("README.md")
    assert result["filename"] == "README.md"
    assert "Results" in result["content"]


def test_compute_intersection_uses_current_eight_coefficient_basis():
    result = compute_intersection()
    assert "g_C" in result["coefficients"]
