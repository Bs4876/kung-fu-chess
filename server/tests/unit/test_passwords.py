from persistence.passwords import hash_password, verify_password


def test_verify_password_accepts_the_correct_password():
    password_hash, salt = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", password_hash, salt)


def test_verify_password_rejects_the_wrong_password():
    password_hash, salt = hash_password("correct horse battery staple")
    assert not verify_password("wrong password", password_hash, salt)


def test_hashing_the_same_password_twice_uses_different_random_salts():
    hash_a, salt_a = hash_password("hunter2")
    hash_b, salt_b = hash_password("hunter2")
    assert salt_a != salt_b
    assert hash_a != hash_b


def test_hash_is_reproducible_given_the_same_salt():
    _, salt = hash_password("hunter2")
    hash_a, _ = hash_password("hunter2", salt)
    hash_b, _ = hash_password("hunter2", salt)
    assert hash_a == hash_b
