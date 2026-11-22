# Prompt Regression Check

Catch broken output contracts when changing an AI prompt or model. Check response text and JSON fields against a versioned set of assertions. The checker runs locally against saved responses, with no dependencies beyond Python 3.8+.

## Run the example

```sh
python check.py cases.json responses.json
```

Both sample cases pass. Change `needs_review` to `false` inside the saved refund response and rerun. The checker names the mismatched field and exits with code 1.

## Check your own responses

1. Define stable case IDs in a JSON spec. Give each case one or more of these assertions.

   | Assertion | Expected value | What it checks |
   | --- | --- | --- |
   | `contains` | Array of strings | Each string appears verbatim, with case sensitivity. |
   | `forbids` | Array of strings | None of the strings appears verbatim, with case sensitivity. |
   | `json_fields` | Object | The entire response parses as a JSON object and each listed top-level field has the specified value. Extra fields are allowed. |

2. Run your prompts using your own app or model client. Save the raw response strings into a JSON object keyed by case ID, as shown in [responses.json](responses.json). A JSON response goes inside a string. Missing cases fail and extra response IDs are ignored.
3. Run `python check.py cases.json responses.json` in your terminal or CI. Exit codes are 0 for all checks passed, 1 for failing checks, and 2 for invalid input.

Use manually reviewed examples to decide what behavior belongs in the contract. Passing assertions cover the declared output properties.

MIT license.
