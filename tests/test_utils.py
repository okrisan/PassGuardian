from ENGINE.utils import calcola_distanza_levenshtein


def test_levenshtein_returns_zero_for_equal_strings() -> None:
    assert calcola_distanza_levenshtein("passguardian", "passguardian") == 0


def test_levenshtein_handles_empty_strings() -> None:
    assert calcola_distanza_levenshtein("", "vault") == 5
    assert calcola_distanza_levenshtein("vault", "") == 5


def test_levenshtein_known_examples() -> None:
    assert calcola_distanza_levenshtein("kitten", "sitting") == 3
    assert calcola_distanza_levenshtein("gumbo", "gambol") == 2