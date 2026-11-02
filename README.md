# ANSHU — Local-First AI Desktop Assistant

ANSHU is a JARVIS-inspired desktop assistant that runs locally on your computer. It combines a browser-based command-center interface with a Python backend and locally hosted AI models.

> **Project status:** Personal/experimental project. The included security controls reduce risk for local use, but this is not a production-hardened desktop application and has not undergone a professional penetration test.

## Highlights

- **Local AI chat:** Connects to Ollama for conversational responses using `qwen2.5:3b`.
- **Image understanding:** Uses `qwen2.5vl:3b` through Ollama.
- **Voice interaction:** Local audio transcription through `faster-whisper` (optional); browser/system speech synthesis for spoken responses.
- **Computer vision:** Browser-side object detection with TensorFlow.js / COCO-SSD and hand tracking with MediaPipe.
- **Controlled desktop actions:** Fixed allowlist, server-created short-lived plans, and explicit confirmation before supported actions.
- **Persistent local context:** SQLite conversation history plus local JSON memory/reminder stores.
- **3D robotics lab:** Three.js rover simulation with manual/autonomous movement, obstacle sensing, and simulated telemetry. It does **not** control a physical robot.

## Architecture

```text
Browser UI (HTML / CSS / JavaScript)
        |
        | same-origin HTTP + NDJSON streaming
        v
Python server (http.server, loopback only)
        |
        +---- Ollama on 127.0.0.1:11434
        |       +-- qwen2.5:3b
        |       +-- qwen2.5vl:3b
        |
        +---- SQLite + JSON local data
        |
        +---- Allowlisted desktop actions
```

## Requirements

- Windows 10/11 recommended (some diagnostics and desktop actions are Windows-specific).
- Python 3.10+ recommended.
- [Ollama](https://ollama.com/) installed and running.
- Models downloaded locally:
  ```bash
  ollama pull qwen2.5:3b
  ollama pull qwen2.5vl:3b
  ```
- A modern browser (Chrome or Edge recommended).
- Optional voice transcription:
  ```bash
  py -m pip install faster-whisper
  ```

The first Whisper model download requires internet access. Browser-side vision/hand-tracking libraries and fonts are loaded from pinned third-party CDN URLs, so the UI is not fully air-gapped.

## Run locally

1. Download or clone this repository.
2. Open a terminal in the project directory (the directory containing `server.py`).
3. Start the server:
   ```bash
   py server.py
   ```
4. Open [http://localhost:8000](http://localhost:8000).
5. Keep Ollama running in the background.

The server intentionally binds to `127.0.0.1:8000`. Do not change this to `0.0.0.0`, port-forward it, expose it to a LAN, or place it behind a public tunnel.

## Security design

The current implementation includes several defense-in-depth controls:

- Loopback-only HTTP server binding and validation of request Host/Origin.
- JSON-only POST requests, request-size limits, and basic endpoint rate limits.
- Static-file restrictions so backend source, local databases, and private files are not served by the UI server.
- Fixed allowlists for supported desktop applications/actions; subprocess calls use argument arrays and `shell=False`.
- Confirmation-based action plans with expiry/single-use execution tokens.
- Blocked executable/script file extensions for supported file-opening flows.
- Local storage of conversations and user-approved memories.

### Security limitations — read before running

- There is no login or authentication. The server is designed for one trusted local user only. Other local processes under the same account may be able to contact localhost.
- Do not expose the server to the network or approve actions you do not understand.
- Treat model responses, file contents, and generated plans as untrusted. Review every action before confirming it.
- Browser UI dependencies are fetched from third-party CDNs. Pinning versions does not eliminate supply-chain risk.
- Browser/system speech synthesis and browser permissions are controlled by the browser/OS. Voice features may have platform-specific behavior.
- This repository does not include a formal dependency vulnerability audit, penetration test, code signing, sandboxing, or production authentication.

See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for the detailed security notes.

## Local data and privacy

On first run, ANSHU creates `jarvis_local_data/` beside `server.py`. It stores conversation history and local memory/reminder data. **This directory is intentionally excluded from Git.** Do not commit your personal database, memory JSON files, logs, or screenshots containing private information.

## Tests

Run the individual test scripts from the project directory:

```bash
for %f in (tests\*_test.py) do py "%f"
```

The test suite includes API security smoke tests, command allowlist checks, streaming framing, memory/context, and project-status behavior. Some tests may emit SQLite `ResourceWarning` messages; these are cleanup warnings, not test failures.

## Known limitations

- Robotics is a browser simulation only; no ESP32 firmware or physical hardware connection is included.
- Voice transcription is segmented utterance processing, not guaranteed word-by-word streaming.
- Some browser capabilities and third-party assets require a compatible browser and internet access.
- Runtime behavior must be verified on the target Windows machine; passing automated tests does not prove every hardware/browser integration works.

## Repository layout

```text
server.py                 Python HTTP server and local AI bridge
index.html                ANSHU command-center UI
tests/                    Regression and security smoke tests
SECURITY_AUDIT.md         Security controls and limitations
DEVELOPMENT_HISTORY.txt   Historical phase/change notes
INSTALL_OFFLINE_VOICE.bat Optional faster-whisper installer
```

## License

No license is currently specified. All rights remain with the respective authors until a license is added.
