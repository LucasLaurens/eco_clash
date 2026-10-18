"""GDScript coverage instrumenter: probes land at the top of every body, never anywhere else."""

import gd_coverage

SOURCE = """class_name Sample
extends RefCounted

@abstract func read_frame() -> InputFrame


static func create(
	first: int,
	second: int,
) -> Sample:
	# a comment line stays first
	var sample := Sample.new()
	return sample


func compute_total() -> int:

	if true:
		return 1
	return 0
"""


def test_probes_sit_at_the_top_of_each_body_and_skip_abstract_functions() -> None:
    # Act
    instrumented, function_ids = gd_coverage.instrument_source(SOURCE, "src/sample.gd")
    # Assert
    assert function_ids == ["src/sample.gd:create", "src/sample.gd:compute_total"]
    lines = instrumented.split("\n")
    create_probe = lines.index('\tCoverageProbe.hit("src/sample.gd:create")')
    assert lines[create_probe - 1] == ") -> Sample:"
    total_probe = lines.index('\tCoverageProbe.hit("src/sample.gd:compute_total")')
    assert lines[total_probe + 1] == "\tif true:"
    assert "read_frame" not in "".join(line for line in lines if "CoverageProbe" in line)


def test_instrumentation_only_adds_probe_lines() -> None:
    # Act
    instrumented, function_ids = gd_coverage.instrument_source(SOURCE, "src/sample.gd")
    # Assert
    without_probes = [line for line in instrumented.split("\n") if "CoverageProbe.hit" not in line]
    assert without_probes == SOURCE.split("\n")
    assert len(instrumented.split("\n")) == len(SOURCE.split("\n")) + len(function_ids)


def test_report_totals_and_lists_missed_functions() -> None:
    # Arrange
    covered = gd_coverage.FileCoverage("src/a.gd", ["src/a.gd:f_one", "src/a.gd:f_two"], {"src/a.gd:f_one"})
    empty = gd_coverage.FileCoverage("src/b.gd", [], set())
    # Act
    report, percent = gd_coverage.format_report([covered, empty])
    # Assert
    assert percent == 50.0
    assert "src/a.gd:f_two" in report
    assert "| `src/b.gd` | 0 | 0 | 100 |" in report


def test_instrument_project_writes_probe_and_hooks_the_runner(tmp_path) -> None:
    # Arrange
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "sample.gd").write_text(SOURCE, encoding="utf-8")
    runner_source = f"extends Node\n\n\nfunc _ready() -> void:\n{gd_coverage.RUNNER_QUIT}\n"
    (tmp_path / gd_coverage.RUNNER_PATH).write_text(runner_source, encoding="utf-8")
    # Act
    files = gd_coverage.instrument_project(tmp_path)
    # Assert
    assert [file.path for file in files] == ["src/sample.gd"]
    assert (tmp_path / gd_coverage.PROBE_PATH).exists()
    assert "CoverageProbe.write_report" in (tmp_path / gd_coverage.RUNNER_PATH).read_text(encoding="utf-8")
