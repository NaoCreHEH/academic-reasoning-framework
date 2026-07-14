import json
import unittest

from benchmark.adapters.claude_code.stream import parse_claude_stream


class ClaudeAdapterStreamParserTests(unittest.TestCase):
    def test_system_init_identifies_loaded_arf_plugin(self):
        observation = parse_claude_stream(
            _ndjson({"type": "system/init", "plugins": [{"name": "arf-academic"}]})
        )
        self.assertTrue(observation.plugin_loaded)

    def test_system_init_explicit_plugin_error_identifies_failed_plugin(self):
        observation = parse_claude_stream(
            _ndjson(
                {
                    "type": "system/init",
                    "plugin_errors": [
                        {"name": "arf-academic", "error": "failed to load"}
                    ],
                }
            )
        )
        self.assertFalse(observation.plugin_loaded)
        self.assertEqual(observation.plugin_load_error, "failed to load")

    def test_unknown_stream_event_ignored(self):
        observation = parse_claude_stream(_ndjson({"type": "new/event", "value": 1}))
        self.assertIsNone(observation.parse_error)

    def test_malformed_json_line_is_parse_failure(self):
        observation = parse_claude_stream('{"type": "result"}\n{bad json}\n')
        self.assertIn("malformed JSON", observation.parse_error)

    def test_skill_tool_invocation_extracts_expected_namespaced_skill(self):
        observation = parse_claude_stream(
            _ndjson(_assistant_tool("arf-academic:exam-generation"))
        )
        self.assertEqual(observation.observed_skills, ("arf-academic:exam-generation",))

    def test_leading_slash_canonicalized(self):
        observation = parse_claude_stream(
            _ndjson(_assistant_tool("/arf-academic:exam-generation"))
        )
        self.assertEqual(observation.observed_skills, ("arf-academic:exam-generation",))

    def test_answer_prose_mentioning_skill_does_not_count_as_dispatch(self):
        observation = parse_claude_stream(
            _ndjson(
                {
                    "type": "assistant",
                    "content": "Use arf-academic:exam-generation for this.",
                }
            )
        )
        self.assertEqual(observation.observed_skills, ())

    def test_debug_like_text_mentioning_skill_does_not_count_as_dispatch(self):
        observation = parse_claude_stream(
            _ndjson(
                {
                    "type": "debug",
                    "message": "Skill tool arf-academic:exam-generation",
                }
            )
        )
        self.assertEqual(observation.observed_skills, ())

    def test_two_different_arf_skill_invocations_remain_observable(self):
        observation = parse_claude_stream(
            _ndjson(
                _assistant_tool("arf-academic:exam-generation"),
                _assistant_tool("arf-academic:python-teaching"),
            )
        )
        self.assertEqual(
            observation.observed_skills,
            ("arf-academic:exam-generation", "arf-academic:python-teaching"),
        )

    def test_non_arf_skills_do_not_become_arf_dispatch(self):
        observation = parse_claude_stream(_ndjson(_assistant_tool("other:skill")))
        self.assertEqual(observation.observed_skills, ())

    def test_final_public_response_reconstructed_from_result(self):
        observation = parse_claude_stream(_ndjson({"type": "result", "result": "Final"}))
        self.assertEqual(observation.response_text, "Final")
        self.assertTrue(observation.raw_response_available)

    def test_thinking_content_excluded(self):
        observation = parse_claude_stream(
            _ndjson(
                {
                    "type": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "hidden"},
                        {"type": "text", "text": "visible"},
                    ],
                }
            )
        )
        self.assertEqual(observation.response_text, "visible")
        self.assertNotIn("hidden", observation.response_text)

    def test_tool_inputs_excluded_from_response_text(self):
        observation = parse_claude_stream(
            _ndjson(
                _assistant_tool("arf-academic:exam-generation", marker="tool-only"),
                {"type": "result", "result": "final answer"},
            )
        )
        self.assertEqual(observation.response_text, "final answer")
        self.assertNotIn("tool-only", observation.response_text)

    def test_tool_results_excluded_from_final_model_response(self):
        observation = parse_claude_stream(
            _ndjson(
                {"type": "tool_result", "content": "tool result"},
                {"type": "result", "result": "final answer"},
            )
        )
        self.assertEqual(observation.response_text, "final answer")
        self.assertNotIn("tool result", observation.response_text)

    def test_stderr_is_irrelevant_to_response_parsing(self):
        observation = parse_claude_stream("")
        self.assertIsNone(observation.response_text)


def _assistant_tool(skill, marker=None):
    tool_input = {"skill": skill}
    if marker is not None:
        tool_input["marker"] = marker
    return {
        "type": "assistant",
        "content": [
            {
                "type": "tool_use",
                "name": "Skill",
                "input": tool_input,
            }
        ],
    }


def _ndjson(*events):
    return "\n".join(json.dumps(event) for event in events)


if __name__ == "__main__":
    unittest.main()
