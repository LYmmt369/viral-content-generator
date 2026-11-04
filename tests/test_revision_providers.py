"""Real SDK round trips to localhost, plus the Gemini SDK method contract. No cloud calls."""

import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from viral_content_drafting import _generate_text, revise_from_instruction
from viral_content_revision import RevisionError


class ProviderHTTPContracts(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.status = 200
        self.reply = '{"edits": [{"before": "唯一长句。", "after": "短句。"}]}'
        self.finish = "stop"
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                owner.requests.append((self.path, body))
                if owner.status != 200:
                    response = {"error": {"message": "fixture failure", "type": "server_error"}}
                elif self.path.endswith("/messages"):
                    response = {
                        "id": "msg_fixture",
                        "type": "message",
                        "role": "assistant",
                        "model": "fixture",
                        "content": [{"type": "text", "text": owner.reply}],
                        "stop_reason": "max_tokens" if owner.finish == "length" else "end_turn",
                        "stop_sequence": None,
                        "usage": {"input_tokens": 10, "output_tokens": 10},
                    }
                else:
                    response = {
                        "id": "chatcmpl_fixture",
                        "object": "chat.completion",
                        "created": 0,
                        "model": "fixture",
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": owner.reply},
                                "finish_reason": owner.finish,
                            }
                        ],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
                    }
                data = json.dumps(response).encode("utf-8")
                self.send_response(owner.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        address = f"http://127.0.0.1:{self.server.server_port}"
        self.environment = {
            "OPENAI_API_KEY": "test-only",
            "ANTHROPIC_API_KEY": "test-only",
            "VIRAL_API_KEY": "",
            "OPENAI_BASE_URL": address + "/v1",
            "ANTHROPIC_BASE_URL": address,
            "NO_PROXY": "127.0.0.1,localhost",
        }

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_openai_and_claude_real_sdks_send_only_the_direct_editing_task(self):
        for provider in ["openai", "claude"]:
            self.requests.clear()
            with (
                self.subTest(provider=provider),
                patch.dict(os.environ, self.environment),
                patch(
                    "viral_content.generators.base.load_skill",
                    side_effect=AssertionError("legacy Skill must not be loaded"),
                ),
            ):
                result = revise_from_instruction(
                    "标题\n唯一长句。\n结尾。",
                    "只压缩长句",
                    protected=["结尾。"],
                    provider=provider,
                    model="fixture",
                    max_tokens=512,
                    timeout=5.0,
                )
                self.assertEqual(result.content, "标题\n短句。\n结尾。")
                self.assertEqual(len(self.requests), 1)
                path, body = self.requests[0]
                if provider == "openai":
                    self.assertEqual(path, "/v1/chat/completions")
                    self.assertIn("只返回一个 JSON", body["messages"][0]["content"])
                    self.assertEqual(body["max_completion_tokens"], 512)
                    self.assertNotIn("max_tokens", body)
                else:
                    self.assertEqual(path, "/v1/messages")
                    self.assertIn("只返回一个 JSON", body["system"])
                payload = json.loads(body["messages"][-1]["content"])
                self.assertEqual(payload["instruction"], "只压缩长句")
                self.assertEqual(payload["protected"], ["结尾。"])

    def test_http_failures_make_one_request_and_never_leak_the_response(self):
        self.status = 500
        for provider in ["openai", "claude"]:
            self.requests.clear()
            with (
                self.subTest(provider=provider),
                patch.dict(os.environ, self.environment),
                self.assertRaises(RevisionError) as raised,
            ):
                _generate_text(
                    "system",
                    "user",
                    provider=provider,
                    model="fixture",
                    max_tokens=512,
                    timeout=5.0,
                )
            self.assertEqual(len(self.requests), 1)
            self.assertNotIn("fixture failure", str(raised.exception))

    def test_truncation_from_both_sdks_is_not_accepted_as_a_complete_result(self):
        self.finish = "length"
        for provider in ["openai", "claude"]:
            with (
                self.subTest(provider=provider),
                patch.dict(os.environ, self.environment),
                self.assertRaisesRegex(RevisionError, "truncated"),
            ):
                _generate_text(
                    "system",
                    "user",
                    provider=provider,
                    model="fixture",
                    max_tokens=512,
                    timeout=5.0,
                )


class GeminiSDKContract(unittest.TestCase):
    def test_direct_prompts_timeout_and_no_retry_match_the_installed_sdk(self):
        from google import genai
        from google.genai import types

        client = MagicMock()
        client.models.generate_content.return_value = SimpleNamespace(
            text="# 完整稿件",
            candidates=[SimpleNamespace(finish_reason=types.FinishReason.STOP)],
            usage_metadata=SimpleNamespace(total_token_count=9),
        )
        with (
            patch.dict(os.environ, {"GOOGLE_API_KEY": "test-only", "VIRAL_API_KEY": ""}),
            patch.object(genai, "Client", return_value=client) as client_factory,
            patch(
                "viral_content.generators.base.load_skill",
                side_effect=AssertionError("legacy Skill must not be loaded"),
            ),
        ):
            text = _generate_text(
                "direct system",
                "direct user",
                provider="gemini",
                model="fixture",
                max_tokens=512,
                timeout=5.0,
            )
        self.assertEqual(text, "# 完整稿件")
        options = client_factory.call_args.kwargs["http_options"]
        self.assertEqual(options.timeout, 5000)
        self.assertEqual(options.retry_options.attempts, 1)
        call = client.models.generate_content.call_args.kwargs
        self.assertEqual(call["model"], "fixture")
        self.assertEqual(call["contents"], "direct user")
        self.assertEqual(call["config"].system_instruction, "direct system")
        self.assertEqual(call["config"].max_output_tokens, 512)
        client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
