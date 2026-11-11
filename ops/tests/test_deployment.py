import base64
import asyncio
import configparser
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import types
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contracts = load_module("check_contracts", "ops/check-contracts.py")
certificate = load_module("download_certificate", "ops/download-tencent-certificate.py")


class ContractPreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.abi_root = Path(self.directory.name)
        chain_dir = self.abi_root / "1"
        chain_dir.mkdir()
        for name in ("Player",):
            (chain_dir / f"{name}.json").write_text(json.dumps({
                "abi": [{"type": "function", "name": "test", "inputs": [], "outputs": []}],
                "address": "0x" + "12" * 20,
            }))
        self.environment = patch.dict(os.environ, {"ENDPOINT": "https://rpc.invalid"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_valid_chain_and_player_without_loot(self):
        with patch.object(contracts, "rpc", side_effect=["0x1", "0x6000"]) as rpc:
            self.assertEqual(contracts.check_contracts(self.abi_root), "1")
            self.assertEqual([call.args[1] for call in rpc.call_args_list],
                             ["eth_chainId", "eth_getCode"])

    def test_rejects_development_chains_and_invalid_chain_ids(self):
        for value in ("0x539", "0x7a69", None, [], "1"):
            with self.subTest(value=value), patch.object(contracts, "rpc", return_value=value):
                with self.assertRaises(ValueError):
                    contracts.check_contracts(self.abi_root)

    def test_rejects_missing_invalid_and_empty_abi(self):
        path = self.abi_root / "1" / "Player.json"
        for value in ("invalid", "[]", '{"abi":[],"address":"0x12"}'):
            path.write_text(value)
            with self.subTest(value=value), patch.object(contracts, "rpc", return_value="0x1"):
                with self.assertRaises(ValueError):
                    contracts.check_contracts(self.abi_root)
        path.unlink()
        with patch.object(contracts, "rpc", return_value="0x1"):
            with self.assertRaisesRegex(ValueError, "Missing or invalid ABI"):
                contracts.check_contracts(self.abi_root)

    def test_rejects_missing_or_invalid_bytecode(self):
        for code in ("0x", "0x0", "0x00", "0x0000", "garbage", None):
            with self.subTest(code=code), patch.object(contracts, "rpc", side_effect=["0x1", code]):
                with self.assertRaisesRegex(ValueError, "no deployed bytecode"):
                    contracts.check_contracts(self.abi_root)

    def test_rpc_serialization_and_error_redaction(self):
        with patch.object(contracts, "urlopen", return_value=BytesIO(b'{"result":"0x1"}')) as urlopen:
            self.assertEqual(contracts.rpc("https://rpc.invalid", "eth_chainId", []), "0x1")
            payload = json.loads(urlopen.call_args.args[0].data)
            self.assertEqual(payload["method"], "eth_chainId")
            self.assertEqual(urlopen.call_args.args[0].get_header("User-agent"), "EthOS/1.0")
        for response in (b'[]', b'{"error":{"message":"private-token"}}', b'invalid'):
            with self.subTest(response=response), patch.object(
                contracts, "urlopen", return_value=BytesIO(response),
            ):
                with self.assertRaises(RuntimeError) as error:
                    contracts.rpc("https://rpc.invalid/private-token", "eth_chainId", [])
                self.assertNotIn("private-token", str(error.exception))

    def test_endpoint_requires_http(self):
        with patch.dict(os.environ, {"ENDPOINT": "file:///private"}):
            with self.assertRaises(ValueError):
                contracts.check_contracts(self.abi_root)


class CertificateTests(unittest.TestCase):
    def test_cli_uses_supported_arguments_and_redacts_failure(self):
        with patch.object(certificate, "run", return_value=Mock(
            returncode=0, stdout='{"CertificateId":"test"}',
        )) as run:
            self.assertEqual(certificate.run_tccli("ssl", "DescribeCertificate"),
                             {"CertificateId": "test"})
            self.assertEqual(run.call_args.args[0], ["tccli", "ssl", "DescribeCertificate"])
        with patch.object(certificate, "run", return_value=Mock(
            returncode=1, stderr="private-token",
        )):
            with self.assertRaises(RuntimeError) as error:
                certificate.run_tccli("ssl", "DescribeCertificate")
            self.assertNotIn("private-token", str(error.exception))

    def test_download_extracts_pem_only_into_private_directory(self):
        archive = BytesIO()
        pem = b"-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----\n"
        key = b"-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("../../nginx/server_bundle.crt", pem * 2)
            output.writestr("nginx/server.key", key)
            output.writestr("other/server.crt", pem)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "certificate"
            with patch.object(sys, "argv", ["download", "test", str(destination)]), patch.object(
                certificate, "run_tccli", side_effect=[
                    {"CertificateId": "test", "Status": 1},
                    {"Content": base64.b64encode(archive.getvalue()).decode()},
                ],
            ):
                certificate.main()
            self.assertEqual({path.name for path in destination.iterdir()},
                             {"server.crt", "server.key"})
            self.assertEqual((destination / "server.crt").read_bytes(), pem * 2)
            self.assertEqual((destination / "server.key").read_bytes(), key)
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((destination / "server.key").stat().st_mode), 0o600)

    def test_pending_or_wrong_certificate_is_not_downloaded(self):
        for metadata in ({"CertificateId": "test", "Status": 0},
                         {"CertificateId": "wrong", "Status": 1}):
            with patch.object(sys, "argv", ["download", "test", "/unused"]), patch.object(
                certificate, "run_tccli", return_value=metadata,
            ) as tccli:
                with self.assertRaisesRegex(RuntimeError, "not issued"):
                    certificate.main()
                self.assertEqual(tccli.call_count, 1)


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # BaseHandler eagerly connects to Ethereum; origin checks do not use it.
        base = types.ModuleType("handlers.base")
        base.BaseHandler = type("BaseHandler", (), {})
        base.MYTOKEN = "mytoken"
        with patch.dict(sys.modules, {"handlers.base": base}):
            cls.mud = load_module("mud_deployment_test", "src/ethos/handlers/mud.py")
        cls.slack = load_module("slack_deployment_test", "src/ethos/slack.py")

    def test_same_host_websocket_origins_only(self):
        handler = types.SimpleNamespace(settings={"ethos_origin": "https://meta.twinsant.com"})
        self.assertTrue(self.mud.MudWebSocket.check_origin(handler, "https://meta.twinsant.com"))
        for origin in ("http://meta.twinsant.com", "https://attacker.invalid", "null", "https://[",
                       "https://meta.twinsant.com.evil", "https://meta.twinsant.com/path",
                       "https://user@meta.twinsant.com", "file://meta.twinsant.com"):
            with self.subTest(origin=origin):
                self.assertFalse(self.mud.MudWebSocket.check_origin(handler, origin))
        handler.settings["ethos_origin"] = "http://127.0.0.1:4003"
        self.assertTrue(self.mud.MudWebSocket.check_origin(handler, "http://127.0.0.1:4003"))

    def test_mud_rejects_input_before_identity_handshake(self):
        handler = types.SimpleNamespace(did_ready=False, close=Mock())
        asyncio.run(self.mud.MudWebSocket.on_message(handler, '{"input":"victim"}\r'))
        handler.close.assert_called_once()

        mud = types.SimpleNamespace(write_message=Mock())
        handler = types.SimpleNamespace(did_ready=True, command='', mud=mud, mud_token='mud',
            settings={'ethos_mud_tokens': {'mud': 'session'},
                      'ethos_sessions': {'session': {'expires': float('inf')}}}, close=Mock())
        asyncio.run(self.mud.MudWebSocket.on_message(handler, 'look\r'))
        mud.write_message.assert_called_once_with('look\r')
        handler.settings['ethos_sessions'].clear()
        asyncio.run(self.mud.MudWebSocket.on_message(handler, 'look\r'))
        handler.close.assert_called_once()
        mud.write_message.assert_called_once()

    def test_optional_slack_and_failure_reporting(self):
        with patch.object(self.slack.requests, "post") as post:
            self.slack.slack_message("", "channel", "message")
            post.assert_not_called()
            post.return_value.json.return_value = {"ok": True}
            self.slack.slack_message("test-token", "channel", "message")
            self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-token")
            self.assertEqual(post.call_args.kwargs["timeout"], 10)
            post.return_value.json.return_value = {"ok": False, "error": "channel_not_found"}
            with self.assertRaisesRegex(RuntimeError, "channel_not_found"):
                self.slack.slack_message("test-token", "channel", "message")

    def test_web3_handlers_load_without_loot_contract(self):
        base = types.ModuleType("handlers.base")
        base.BaseHandler = type("BaseHandler", (), {})
        eth = types.ModuleType("w3.eth")
        eth.Eth = object
        unavailable_loot = types.ModuleType("w3.loot")
        with patch.dict(sys.modules, {"handlers.base": base, "w3.eth": eth,
                                      "w3.loot": unavailable_loot}):
            module = load_module("w3_player_only_test", "src/ethos/handlers/w3.py")
        self.assertTrue(hasattr(module, "BalanceHandler"))
        self.assertTrue(hasattr(module, "CryptoHandler"))

    def test_main_reads_production_defaults_from_environment(self):
        from tornado.web import RequestHandler
        modules = {}
        for module_name, names in {
            "handlers.base": ("BaseHandler",),
            "handlers.auth": ("SigninHandler", "SignoutHandler", "MeHandler"),
            "handlers.w3": ("CryptoHandler", "BalanceHandler"),
            "handlers.mud": ("MudWebSocket", "EchoWebSocket"),
        }.items():
            module = types.ModuleType(module_name)
            for name in names:
                setattr(module, name, RequestHandler)
            modules[module_name] = module
        modules["handlers.base"].NONCE_COOKIE = "ethos_nonce"
        modules["handlers.base"].NONCE_TTL = 300
        modules["slack"] = self.slack
        with patch.dict(sys.modules, modules), patch.dict(os.environ, {
            "ETHOS_COOKIE_SECRET": "production-test-secret",
            "ENDPOINT": "https://rpc.invalid",
            "ETHOS_ADDRESS": "127.0.0.1",
            "SLACK_SECRET": "",
        }), patch("tornado.options.define") as define, patch("tornado.options.parse_command_line"):
            load_module("main_deployment_test", "src/ethos/main.py")
        defaults = {call.args[0]: call.kwargs["default"] for call in define.call_args_list}
        self.assertEqual(defaults["secret"], "production-test-secret")
        self.assertEqual(defaults["endpoint"], "https://rpc.invalid")
        self.assertEqual(defaults["address"], "127.0.0.1")
        self.assertEqual(defaults["slack_secret"], "")

    def test_template_renders_same_host_websocket_csp(self):
        from tornado.template import Loader
        loader = Loader(str(ROOT / "src/ethos/templates"))
        for host, socket_origin in (("meta.twinsant.com", "wss://meta.twinsant.com"),
                                    ("127.0.0.1:4003", "ws://127.0.0.1:4003")):
            html = loader.load("index.html").generate(
                static_url=lambda path: "/static/" + path,
                request=types.SimpleNamespace(host=host),
                csp_nonce="test-nonce",
                socket_origin=socket_origin,
            ).decode()
            self.assertIn(socket_origin, html)
            self.assertIn("script-src 'self' 'nonce-test-nonce'", html)
            self.assertIn('<script nonce="test-nonce">', html)
            self.assertNotIn("connect-src 'self' ws: wss:", html)

    def test_deploy_help_does_not_require_credentials(self):
        result = subprocess.run(["bash", str(ROOT / "ops/deploy.sh"), "--help"],
                                capture_output=True, text=True, check=True)
        self.assertIn("ETHOS_ABI_DIR", result.stdout)

    def test_supervisor_uses_bundled_x86_64_linux_driver(self):
        configuration = configparser.ConfigParser()
        configuration.read(ROOT / "ops/supervisor/ethos.ini")
        command = configuration["program:ethos-driver"]["command"]
        self.assertEqual(command.split()[0], "/opt/ethos/bin/driver.linux.x86_64")
        with (ROOT / "bin/driver.linux.x86_64").open("rb") as binary:
            header = binary.read(20)
        self.assertEqual(header[:6], b"\x7fELF\x02\x01")
        self.assertEqual(header[18:20], b"\x3e\x00")


if __name__ == "__main__":
    unittest.main()
