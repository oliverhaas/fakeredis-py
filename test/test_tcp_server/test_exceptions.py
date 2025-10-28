import time
from threading import Thread

import pytest
import redis

from fakeredis import TcpFakeServer
from test import testtools


@testtools.run_test_if_lupa_installed()
def test_noscript_error():
    """Test that EVALSHA with a non-existent script returns NOSCRIPT error."""
    server_address = ("127.0.0.1", 19000)
    server = TcpFakeServer(server_address)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)

    with redis.Redis(host=server_address[0], port=server_address[1]) as r:
        fake_sha = "0" * 40
        with pytest.raises(redis.exceptions.NoScriptError):
            r.evalsha(fake_sha, 0)

    server.server_close()
    server.shutdown()
    t.join()


def test_wrongpass_error():
    """Test that wrong password returns WRONGPASS error."""
    server_address = ("127.0.0.1", 19001)
    server = TcpFakeServer(server_address)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)

    with redis.Redis(host=server_address[0], port=server_address[1]) as r:
        # Set a password
        r.execute_command("ACL", "SETUSER", "testuser", "on", ">wrongpass", "~*", "+@all")

        # Try to authenticate with wrong password
        with pytest.raises(redis.exceptions.AuthenticationError):
            r.execute_command("AUTH", "testuser", "badpassword")

    server.server_close()
    server.shutdown()
    t.join()
