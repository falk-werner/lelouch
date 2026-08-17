[![Build](https://github.com/falk-werner/lelouch/actions/workflows/build.yml/badge.svg)](https://github.com/falk-werner/lelouch/actions/workflows/build.yml)
[![PyPI Version](https://img.shields.io/pypi/v/lelouch)](https://pypi.org/project/lelouch/)

# lelouch

Library and execution environment for AI agents and loops.

## Usage

```
lelouch [options] <script> [args...]
```

### Options

| Option | Type | Defaut | Description |
| ------ | ---- | ------ | ----------- |
| -u, --base-url | str | env(BASE_URL) | URL to OpenAI compatible API |
| -k, --api-key | str | env(API_KEY) | API_KEY of OpenAI compatible API |
| -m, --model | str | env(MODEL) | ID of the model to use |
| -U, --user | int | uid | ID of the sandbox user |
| -G, --group | int | gid | ID of the sandox group |
| -w, --workspace | path | . | Path of the workspace |
| --rebuild | - | - | Force to rebuild the sandbox |

## Environment Variables

| Variable | Description |
| -------- | ----------- |
| BASE_URL | URL to OpenAI compatible API |
| API_KEY  | API_KEY of OpenAI compatible API |
| MODEL    | ID of the default model |

## Requirements

- docker: required to build sandbox (strongly recommended)

## References

- [Open AI Responses API](https://developers.openai.com/api/reference/resources/responses)
- [Open AI list models API](https://developers.openai.com/api/reference/resources/models/methods/list)
