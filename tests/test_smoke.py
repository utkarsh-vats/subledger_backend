def test_smoke(client, auth_header):
    assert auth_header["Authorization"].startswith("Bearer ")