# Grok Bot box: sound and speech

Open only when readiness names sound or speech. Box basics: `grok-bot-box.md`.

## Recording sound

The box may have a shared sound server with a virtual speaker `virtual_out` (socket path from house rules, `<sound-server socket>` below). Chrome plays into it; record from `virtual_out.monitor`.

1. Check it's there: `[ -S <sound-server socket> ] && PULSE_SERVER=unix:<sound-server socket> pactl list short sinks` lists `virtual_out`. If it's missing (after any house-rules recovery script), record a gap and tell your manager. Never claim sound was checked.
2. **It is shared, so say whose sound you recorded.** Other agents' sound can land in your recording. It's first-hand evidence only when the one stream playing was your own Chrome: log, with the time, each stream's `application.process.id` from `PULSE_SERVER=unix:<sound-server socket> pactl list sink-inputs`, and walk up its parents (`pstree -p <script pid>`, or repeated `ps -o pid,ppid,comm -p <pid>`) to the `process.pid` your script logged at launch; Chrome's audio process is a grandchild or deeper. A stream can be silent or corked, so proof is your stream plus a level (step 5) ("Where evidence came from" in `test-session/references/session-rules.md`). If another stream played, that stretch can't be attributed: say so and repeat. Use a dedicated speaker if you're given one.
3. Give Chrome the server in its own environment, unmuted:
   ```js
   const { chromium } = require('playwright-core');           // only playwright-core is installed
   chromium.launch({ executablePath: '/usr/bin/google-chrome',
     ignoreDefaultArgs: ['--mute-audio'],                      // Playwright mutes by default
     env: { ...process.env, PULSE_SERVER: 'unix:<sound-server socket>' } })
   ```
   `args: ['--autoplay-policy=no-user-gesture-required']` is only for proving capture; test the product's real autoplay without it, as a visitor's browser would.
4. Record: `PULSE_SERVER=unix:<sound-server socket> parecord --device=virtual_out.monitor --latency-msec=50 --file-format=wav audio/rec-01.wav &` then `echo $! > audio/rec-01.pid`, and log its start time. An idle speaker is SUSPENDED and gives no data, so WAV offsets aren't clock times: judge timing from your log. Stop with `kill -INT` on that pid after the sound ends and wait for exit; a 44-byte file means it stopped too early.
5. Check the capture: `ffmpeg -i audio/rec-01.wav -af volumedetect -f null - 2>&1 | grep -E 'mean_volume|max_volume'`. Silence reads about -91 dB, a loud tone near 0 dB. A level shows something played, not what: tie it to your stream (step 2) and compare with what the page should play.

## Speech (text-to-speech voices)

1. Check the tools exist: `command -v espeak-ng speech-dispatcher`.
2. Start Chrome with `--enable-speech-dispatcher`. Without it, `getVoices()` reports 0 voices: a tool setting, not a product finding.
3. Wait for `voiceschanged` before counting voices; log the default (`getVoices()[0]` and its `lang`), which a page that sets none gets.
4. Record speech with the sound recipe.
5. Note the pid of any `speech-dispatcher` your run starts, and stop it in cleanup.
