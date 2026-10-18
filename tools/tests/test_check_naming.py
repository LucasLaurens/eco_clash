"""The naming rule itself: verbs pass, nouns fail, and the whole repo is clean."""

import check_naming


def test_verbs_pass_and_nouns_fail() -> None:
    # Act & Assert
    assert check_naming.check_function_name("compute_hit_rect") is None
    assert check_naming.check_function_name("_update_free_state") is None
    assert check_naming.check_function_name("is_in_play") is None
    assert check_naming.check_function_name("total_duration") is not None
    assert check_naming.check_function_name("_screen_size") is not None


def test_engine_callbacks_and_handlers_are_exempt() -> None:
    # Act & Assert
    assert check_naming.check_function_name("_physics_process") is None
    assert check_naming.check_function_name("_on_hit_landed") is None
    assert check_naming.check_function_name("__init__") is None


def test_one_letter_names_fail_except_coordinates() -> None:
    # Act & Assert
    assert check_naming.check_short_name("p") is not None
    assert check_naming.check_short_name("x") is None
    assert check_naming.check_short_name("perception") is None


def test_repository_follows_the_naming_rule() -> None:
    # Act
    offences = check_naming.collect_offences()
    # Assert
    assert offences == []


def test_main_reports_zero_offences(capsys) -> None:
    # Act
    exit_code = check_naming.main()
    # Assert
    assert exit_code == 0
    assert "0 offence(s)" in capsys.readouterr().out
