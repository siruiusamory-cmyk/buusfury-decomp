from __future__ import annotations

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _flat(relative_path: str) -> str:
    return re.sub(r"\s+", " ", _read(relative_path)).lower()


def test_permanent_rules_require_independent_review_before_closure():
    agents = _flat("<local-state-name>")
    detail = _flat("docs/DEVELOPMENT.md")

    assert "every nontrivial code-bearing ticket" in agents
    assert "report closed without an independent verdict" in agents
    assert "independent code review gate" in detail
    assert "actual diff" in detail
    assert "relevant surrounding code" in detail
    assert "implementer's closure report is orientation, not authoritative evidence" in detail
    assert "initial review pass produces findings and does not edit code" in detail


def test_review_gate_covers_risk_areas_and_has_actionable_verdicts():
    detail = _flat("docs/DEVELOPMENT.md")

    for area in (
        "correctness",
        "architecture",
        "rom/data safety",
        "determinism",
        "tests/evidence",
        "compatibility",
        "maintainability",
        "public-release hygiene",
    ):
        assert area in detail

    for verdict in ("approve", "approve with non-blocking notes", "block"):
        assert verdict in detail
    for finding_field in (
        "severity",
        "file/location",
        "observed problem",
        "impact",
        "concrete evidence",
        "smallest recommended correction",
    ):
        assert finding_field in detail
    for severity in ("critical", "high", "medium", "low"):
        assert f"`{severity}`" in detail


def test_review_fix_loop_and_closure_order_are_explicit():
    detail = _flat("docs/DEVELOPMENT.md")

    assert "smallest sufficient focused validation" in detail
    assert "blast-radius policy" in detail
    assert "explicitly changes the verdict or lists remaining blockers" in detail

    closure_flow = detail[
        detail.index("the effective closure sequence is:") :
        detail.index("use the established authenticated `glab` workflow")
    ]
    ordered_steps = (
        "implementation/research + public-progress changes when expected updated",
        "focused validation",
        "implementation frozen",
        "independent review",
        "reviewer sign-off",
        "final integration gate when warranted",
        "public_progress_impact confirmation (reviewed diff only)",
        "explicit staging",
        "commit / mr / push",
        "live-site verification when updated",
        "closure",
    )
    cursor = 0
    for step in ordered_steps:
        cursor = closure_flow.index(step, cursor) + len(step)


def test_review_workflow_records_cross_model_and_gitlab_preferences():
    detail = _flat("docs/DEVELOPMENT.md")

    assert "prefer a fresh-context reviewer" in detail
    assert "different strong model" in detail
    assert "not a vendor lock" in detail
    assert "resolved by evidence, never model authority" in detail
    assert "authenticated `glab` workflow" in detail
    assert "never assume ssh keys" in detail
    assert "feature branch" in detail
    assert "gitlab merge request" in detail
    assert "pipeline and independent review" in detail
    assert "do not force an mr for trivial documentation-only changes" in detail
    assert "enable force-push" in detail


def test_ticket_template_and_closure_checklist_require_review_records():
    template = _flat("docs/REVIEW.md")
    review_template = _flat("docs/REVIEW.md")
    checklist = _flat("docs/README.md")

    assert "required review" in template
    assert "independent reviewer/model" in template
    assert "explicit re-review" in template
    assert "reviewer identity/model, verdict, findings and resolution" in template
    assert "code review" in review_template
    assert "scope reviewed" in review_template
    assert "blocking findings" in review_template
    assert "correctness" in review_template
    assert "maintainability" in review_template
    assert "reviewer validation performed" in review_template
    assert "remaining uncertainty" in review_template
    assert "cannot report closed" in checklist
    assert "independent `approve` or `approve with non-blocking notes`" in checklist
    assert checklist.index("update `src/data/project.ts`") < checklist.index(
        "freeze the implementation"
    )
    assert checklist.index("freeze the implementation") < checklist.index(
        "independent code-review verdict"
    )
    assert checklist.index("reviewer sign-off") < checklist.index(
        "final integration gate"
    )
    assert checklist.index("confirm `public_progress_impact") < checklist.index(
        "stage explicit paths"
    )
    assert checklist.index("commit/mr/push sequence") < checklist.index(
        "verify the live site after publishing"
    )


def test_pre_public_audit_includes_repository_relevance_inventory():
    detail = _flat("docs/DEVELOPMENT.md")

    assert "one-time pre-public audit" in detail
    assert "public repository relevance" in detail
    assert (
        "would a legacy of goku modder, rom hacker, contributor, or sdk "
        "maintainer reasonably benefit from this being in the public repository?"
        in detail
    )
    for column in (
        "path",
        "current purpose",
        "community relevance",
        "keep / move / trim / remove / ignore",
        "reason",
        "blocking before public sharing? yes/no",
    ):
        assert column in detail
    assert "first produce an inventory and recommendation" in detail
    assert "high-priority release blocker" in detail
    assert "private development-process residue" in detail


def test_removed_godot_prototype_stays_out_of_the_product_repository():
    assert not (PROJECT_ROOT / "remake").exists()

    agents = _flat("<local-state-name>")
    detail = _flat("docs/DEVELOPMENT.md")
    assert "former godot prototype" in agents
    assert "do not recreate it" in agents
    assert "owner selected `remove`" in detail
    assert "must not ship or be reintroduced" in detail


def test_instruction_continuations_remain_within_established_bounds():
    assert len(_read("<local-state-name>").splitlines()) <= 300
    assert len(_read("docs/DEVELOPMENT.md").splitlines()) <= 240
    assert len(_read("docs/REVIEW.md").splitlines()) <= 100
