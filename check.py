"""Check saved AI responses against explicit text and JSON assertions."""

import argparse
import json
from pathlib import Path
import sys

RULES = {"contains", "forbids", "json_fields"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_cases(spec):
    if not isinstance(spec, dict) or not spec:
        raise ValueError("the spec must map case IDs to assertion objects")
    for case, rules in spec.items():
        if not case.strip() or not isinstance(rules, dict) or not rules or rules.keys() - RULES:
            raise ValueError(f"{case!r}: expected a nonempty object using {sorted(RULES)}")
        for rule in ("contains", "forbids"):
            if rule in rules:
                fragments = rules[rule]
                if not isinstance(fragments, list) or not fragments or any(
                    not isinstance(fragment, str) or not fragment for fragment in fragments
                ):
                    raise ValueError(f"{case!r}: {rule} must be a nonempty array of nonempty strings")
        if "json_fields" in rules and (
            not isinstance(rules["json_fields"], dict) or not rules["json_fields"]
        ):
            raise ValueError(f"{case!r}: json_fields must be a nonempty object")
    return spec


def compare_json(actual, expected):
    # Serialized comparison distinguishes Python's equal-but-different True and 1.
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def failures(answer, rules):
    for fragment in rules.get("contains", []):
        if fragment not in answer:
            yield f"missing required text {fragment!r}"
    for fragment in rules.get("forbids", []):
        if fragment in answer:
            yield f"found forbidden text {fragment!r}"
    if "json_fields" in rules:
        try:
            value = json.loads(answer)
        except ValueError:
            yield "response is not valid JSON"
            return
        if not isinstance(value, dict):
            yield "response JSON must be an object"
            return
        for key, expected in rules["json_fields"].items():
            if key not in value or not compare_json(value[key], expected):
                yield f"missing or mismatched JSON field {key!r}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON map of case IDs to assertion objects")
    parser.add_argument("responses", type=Path, help="JSON map of case IDs to response strings")
    args = parser.parse_args()
    try:
        cases = load_cases(read_json(args.spec))
        responses = read_json(args.responses)
        if not isinstance(responses, dict) or any(not isinstance(v, str) for v in responses.values()):
            raise ValueError("responses must map case IDs to strings")
    except (OSError, ValueError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    passed = 0
    for case, rules in cases.items():
        problems = list(failures(responses[case], rules)) if case in responses else ["missing response"]
        if problems:
            for problem in problems:
                print(f"FAIL {case!r}: {problem}")
        else:
            print(f"PASS {case!r}")
            passed += 1
    print(f"{passed}/{len(cases)} cases passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
