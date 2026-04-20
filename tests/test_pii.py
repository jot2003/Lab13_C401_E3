from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_phone_vn() -> None:
    out = scrub_text("Call me at 0987654321 or +84 987 654 321")
    assert "0987654321" not in out
    assert "+84 987 654 321" not in out
    assert out.count("REDACTED_PHONE_VN") == 2


def test_scrub_cccd() -> None:
    out = scrub_text("My CCCD is 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Card: 4111 1111 1111 1111")
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("Passport code is B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out
