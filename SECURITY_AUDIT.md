ANSHU Phase 25 — Security Hardening Notes
========================================

Purpose
-------
This update adds defense-in-depth for local personal use. It is not a guarantee
that ANSHU is completely secure, and it is not a professional penetration test.
Keep using it only on a trusted personal computer with supervision.

Implemented safeguards
---------------------
- Server binds to 127.0.0.1:8000, not all network interfaces.
- Requests with non-loopback Host values are rejected; browser POSTs with a
  foreign Origin are rejected.
- POST APIs require application/json and enforce endpoint-specific request limits.
- Sensitive files such as server.py, README, and the SQLite database are no
  longer served as static web files. Only the UI entry page is served.
- Browser response headers reduce MIME sniffing, framing, referrer leakage,
  and unnecessary camera/microphone/geolocation permissions.
- Computer-control tasks remain deterministic, allowlisted, and confirmation-based.
  Plans are server-created, expire, and are single-use.
- Known executable, installer, shortcut, and command-script file types are
  blocked from the file-opening action. Source-code/text files open in VS Code
  or Notepad as text, rather than through their file association.
- Basic per-endpoint request rate limits reduce accidental request floods.
- Request bodies/prompts are not deliberately logged; standard HTTP access
  metadata remains in the terminal.
- Static file handling is restricted for GET and HEAD requests; private project
  and database files are not available through the built-in HTTP file server.

Important limitations
---------------------
- No desktop app can be declared “fully safe” based only on static checks.
- There is no login/password because this is intended to bind to loopback on a
  single-user computer. Other local processes running as the same user may be
  able to contact localhost. Do not run untrusted software alongside ANSHU.
- Do not port-forward 8000, expose it to a LAN, or use a public tunnel.
- The current UI still loads Google Fonts and computer-vision/hand-tracking
  libraries from Google Fonts and jsDelivr CDN URLs. Those third-party resources
  can receive network requests and their JavaScript runs in the page context.
  Vision/hand tracking and the custom fonts may not work offline. Self-hosting
  audited/pinned copies would reduce this supply-chain and network dependency.
- Ollama and browser speech recognition may have their own settings and data
  handling. Voice recognition may use a browser/vendor service; offline voice
  operation is not guaranteed.
- Opening non-executable document/media formats still invokes the system's
  default application, which has its own risks. Do not open untrusted files.
- AI output can be wrong or manipulated by malicious content in files. Treat
  file contents and AI advice as untrusted; do not approve actions you do not
  understand.
- This build does not implement automatic backups, antivirus, Windows account
  isolation, signed updates, or a formal dependency vulnerability audit.

Recommended daily-use settings
------------------------------
1. Keep Windows, browser, Python, Ollama, and packages updated.
2. Keep ANSHU on localhost and close the server when finished.
3. Keep confirmation enabled for all computer actions.
4. Back up projects and ANSHU data regularly.
5. Do not provide passwords, API keys, banking details, or sensitive documents.
6. Never approve an unexpected action plan; cancel it and investigate.

Phase 28 — Streaming chat security notes
----------------------------------------
- Local chat can request token streaming, but the upstream Ollama URL remains
  fixed to 127.0.0.1:11434; the browser cannot supply a target URL or model URL.
- Streaming requests pass through the same Host, Origin, JSON content-type,
  body-size and rate-limit checks as ordinary chat requests.
- The streaming response uses newline-delimited JSON, no-store, nosniff, and
  no permissive CORS policy. No user prompt is deliberately written to logs.
- Streamed model text is display-only. It cannot invoke desktop tools or issue
  robot actions. Explicit robot commands still use the deterministic router.
- Token streaming improves perceived latency but does not itself add voice
  activity detection, partial speech recognition, or interruptible streaming
  TTS. Those remain future work and must retain explicit microphone controls.
- Third-party CDN references remain in the UI. Therefore this build is local
  for AI inference, but is not yet fully air-gapped at the web-asset layer.


Phase 29 — response handling regression fix
--------------------------------------------
- The browser now handles both application/json responses from deterministic
  local routes and application/x-ndjson streaming responses from Ollama.
- The stream reader flushes TextDecoder at EOF and processes a final line even
  if the server did not terminate it with a newline.
- This is a UI protocol-compatibility fix; it does not relax Host/Origin checks,
  request validation, rate limits, action allowlists, or local-only binding.

PHASE 30 VOICE PRIVACY NOTES
----------------------------
The main microphone/orb path now uses browser MediaRecorder + Web Audio VAD and submits completed utterance audio only to the local ANSHU server endpoint. It no longer starts Web Speech / browser SpeechRecognition for the main microphone path. Offline wake detection uses the same local Whisper endpoint. The microphone is requested only after an explicit user action and can be stopped from the voice control. Audio is not intentionally sent to a cloud speech provider by this path. Browser/OS-level microphone permissions and local loopback protections still apply.

Residual limitations: this is utterance segmentation, not streaming partial ASR; TTS remains browser speechSynthesis and barge-in is not implemented. External UI CDN references elsewhere in the app remain and mean the whole app is not air-gapped.


## Phase 31 - Live conversational voice
- No external speech or AI provider was introduced. TTS uses the browser/system speechSynthesis engine.
- Microphone-based barge-in monitoring runs only while Offline Wake is explicitly enabled and ANSHU is speaking.
- The monitor computes local audio RMS only; it does not upload audio. Transcription uses the existing local `/api/voice/transcribe` endpoint.
- Existing loopback binding, request validation, rate limits, allowlisted robot actions, and SQLite persistence are unchanged.
- Barge-in energy detection is heuristic and may miss quiet speech or react to loud environmental sounds.


## Phase 32 - Voice false-trigger and duplicate suppression
- Local voice activity threshold and minimum sustained speech duration were increased to reduce ambient-noise clips.
- The wake loop observes a post-TTS quiet period and ignores stale/duplicate transcripts.
- In wake-required mode, recognized text without a wake phrase or active wake window is not forwarded to chat.
- All filtering is local in the browser; no cloud service or additional data transfer was introduced.


## Phase 33 - English-only language policy
- The UI no longer exposes automatic language detection or alternate-language options.
- Voice transcription is pinned to the English Whisper language code; requests specifying another language are rejected.
- Speech synthesis selects only installed English voices and falls back to en-US.
- The local assistant system prompt instructs the model to respond in English only.
- No cloud provider or new external dependency was introduced.


## Phase 34 voice controls
Voice sensitivity, silence timeout, and TTS speed are user-adjustable. Preferences are stored in browser-local storage only; no new network endpoint or external provider is introduced.


## Phase 35 diagnostics
The diagnostics panel runs only after the user clicks its button. It queries the existing same-origin `/api/health` endpoint and browser capability/permission metadata. It does not call `getUserMedia`, capture audio, transmit microphone data, or contact remote hosts. Browser microphone permission reporting may be unavailable in some browsers; in that case the panel reports API availability without prompting. This is not a full network isolation or penetration test.


## Phase 35.1 UI layout correction
The diagnostics panel layout was corrected for usability. The right sidebar is independently scrollable, sidebar cards do not shrink into clipped content, and diagnostic result rows use a bounded scroll region. This is a presentation-only change; it does not add permissions, network calls, microphone capture, or backend actions.


## Phase 36 — Local memory controls
Saved memories remain user-approved and local. The memory API validates non-empty updates, limits text to 400 characters, checks IDs for updates, and requires explicit UI confirmation before clear-all. Retrieval treats saved memories as contextual data, not instructions. No automatic personal-data extraction or cloud sync is added.


## Phase 36.1 memory-context correction
Typed "Remember that ..." requests use the existing localhost memory endpoint. Streaming chat retains selected user-approved memory context. Memory text remains untrusted context, not instructions. No new network destination or permission was added.


## Phase 37 — Intelligent local context
- Conversation history sent to Ollama is bounded to the latest 12 stored messages, with a 700-character cap per message. The current user message remains separately bounded by the existing request validation.
- Older history is reduced to a bounded extractive digest stored in the existing local SQLite database. No remote summarization or new network destination is used.
- Saved memory retrieval is opt-in via a local setting and uses keyword overlap only; unrelated memories are not automatically injected as a fallback.
- Memory and summary text are labeled untrusted context. They do not alter the deterministic robot-action allowlist or authorize shell/filesystem operations.
- Intent hints are deterministic labels used only to shape response style; they do not dispatch tools or actions.
- Existing SQLite content is preserved; startup creates the new summary table if absent. The summary is derived from existing chat history and can be regenerated as new turns accumulate.
- The new context settings endpoint remains same-origin, loopback-only, JSON-only, and protected by the existing request-size and origin checks.
- This phase does not provide semantic embeddings or model-generated abstractive summaries. Keyword relevance can miss paraphrases. Existing external UI CDN references remain, so the full UI is not air-gapped.
