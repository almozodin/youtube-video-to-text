# youtube-link-transcriber

A Python CLI project that downloads audio from a YouTube link, runs local transcription with `faster-whisper`, and exports readable transcripts to TXT, Markdown, DOCX, and SRT.

## Features

- Accepts a YouTube URL as input.
- Uses `yt-dlp` to extract best-available audio.
- Uses `faster-whisper` for local speech-to-text.
- Exports transcript formats: `.txt`, `.md`, `.docx`, `.srt`.
- Outputs timestamped transcript segments.
- Optional Obsidian vault sync (`YouTube Transcripts` folder).
- Optional Notion page creation via Notion API.
- Friendly terminal output with `rich`.

## Installation

```bash
git clone https://github.com/almozodin/youtube-video-to-text.git
cd youtube-video-to-text
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## ffmpeg system dependency

`ffmpeg` must be installed and available on your PATH.

- **macOS**
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu**
  ```bash
  sudo apt install ffmpeg
  ```
- **Windows**
  Install ffmpeg, then add the ffmpeg `bin` folder to your PATH.

## Usage

```bash
python -m transcriber.cli "https://www.youtube.com/watch?v=VIDEO_ID"
python -m transcriber.cli "https://www.youtube.com/watch?v=VIDEO_ID" --model base --formats txt md srt docx
python -m transcriber.cli "https://www.youtube.com/watch?v=VIDEO_ID" --model medium --obsidian-vault "/Users/me/Obsidian/Vault/YouTube Notes"
python -m transcriber.cli "https://www.youtube.com/watch?v=VIDEO_ID" --notion
```

### CLI arguments

- `url` (required positional)
- `--model` (`tiny`, `base`, `small`, `medium`, `large-v3`; default `base`)
- `--language` (optional language code; default auto-detect)
- `--output-dir` (default `output`)
- `--formats` (one or more of `txt md docx srt`; default `txt md`)
- `--keep-audio` (keep `audio.mp3` in output)
- `--obsidian-vault` (optional path)
- `--notion` (enable Notion sync)
- `--notion-parent-page-id` (optional; overrides `.env`)
- `--cookies` (optional cookies.txt for yt-dlp)

## Output layout

For `Example Video`:

```text
output/example-video/
├── audio.mp3        (only with --keep-audio)
├── transcript.txt
├── transcript.md
├── transcript.docx
└── transcript.srt
```

## Obsidian sync

If you pass `--obsidian-vault`, the tool creates `<vault>/YouTube Transcripts/` and copies `transcript.md` there. Existing files are never silently overwritten; a suffix (`-1`, `-2`, ...) is added.

## Notion sync

Enable with `--notion`.

1. Create `.env` from `.env.example`.
2. Set token and parent page id.
3. Optionally pass `--notion-parent-page-id` at runtime.

If credentials are missing or Notion API fails, local transcript generation still completes.

## .env example

```env
NOTION_TOKEN=
NOTION_PARENT_PAGE_ID=
```

## Whisper model sizes

- `tiny`: fastest, lowest accuracy
- `base`: good for testing
- `small`: better
- `medium`: strong balance
- `large-v3`: best quality, slowest

## Error handling

The CLI surfaces readable errors/warnings for:
- invalid URL / private / age or region restricted content
- missing ffmpeg
- failed download/transcription
- invalid Obsidian path
- missing Notion credentials

## Legal note

This tool is for personal transcription, study, and accessibility use. Users are responsible for respecting YouTube Terms of Service and applicable copyright laws.
