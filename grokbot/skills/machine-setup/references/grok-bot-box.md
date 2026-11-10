# Grok Bot platform reference: recipes for the Grok Bot box

Only if you run as a Grok Bot, on its shared Linux box with Chrome and ffmpeg. House rules add paths, leases and limits. Elsewhere, prove your own tools ("Prove your tools" in [machine-setup](../../machine-setup/SKILL.md)).

- Each recipe starts with a check. If one fails, tell your manager rather than concluding the capability is missing; an equally good safe equivalent is fine if you prove it and say so.
- The box is shared: follow `test-session/references/resource-cleanup.md` (memory floor, leases, stop only your own pids).
- Values are examples (sizes come from your charter); re-prove a recipe after changing it.

Run commands from your session folder. First: `mkdir -p shots video audio`.

## Driving Chrome with Playwright

Check: `ls /usr/bin/google-chrome && ls "$(npm root -g)/playwright-core"`.

Use the system Chrome and box-wide `playwright-core`; don't install your own. Run with `NODE_PATH=$(npm root -g) node script.js`. Headed (so a screen recording sees it), phone size with touch:
```js
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: false });
  try {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    console.log(new Date().toTimeString().slice(0, 8), 'open'); await page.goto('about:blank');
    await page.screenshot({ path: 'shots/01-start.png' });
  } finally { await browser.close(); }   // always close, even on failure
})();
```
Desktop: the charter's size (for example `{ width: 1280, height: 800 }`) without `isMobile`/`hasTouch`. At phone size, a page with no `<meta name="viewport">` lays out 980 px wide, as on real phones: a finding, not a tool fault. Playwright's `recordVideo` doesn't work here (no bundled ffmpeg); for headless runs see "Recording a headless browser".

## Recording the screen with a clock (headed browser)

Check: `echo "$DISPLAY"` is set (your desktop's own display), `which xdpyinfo` and `ls /usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`.

Start ffmpeg in the background and save its pid. It grabs the whole display at its real size, so the window you test is always inside the frame:
```
SIZE=$(xdpyinfo | awk '/dimensions:/{print $2}')
ffmpeg -loglevel error -f x11grab -video_size "$SIZE" -framerate 10 -i "$DISPLAY" -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:text='%{localtime\:%H\\\\\:%M\\\\\:%S}':x=w-tw-10:y=10:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -y video/rec-01.mp4 > video/rec-01.log 2>&1 &
echo $! > video/rec-01.pid
```
Stop it by that pid only (other agents record too), wait for it to finish, then check:
```
PID=$(cat video/rec-01.pid); kill -INT "$PID"; while kill -0 "$PID" 2>/dev/null; do sleep 0.5; done
ffmpeg -v error -i video/rec-01.mp4 -f null -                    # no output = the whole clip decodes
ffprobe -v error -show_entries format=duration -of csv=p=0 video/rec-01.mp4
ffmpeg -loglevel error -i video/rec-01.mp4 -frames:v 1 -y shots/clock-check.png   # then look at the clock
```
## Recording a headless browser

No display to grab: use Chrome's screencast and burn in the clock (Check: `ffmpeg -hide_banner -filters | grep drawtext`). After `newPage()`:
```js
const fs = require('fs'); fs.mkdirSync('video/frames-01', { recursive: true });
const cdp = await ctx.newCDPSession(page); let n = 0, stopped = false;
cdp.on('Page.screencastFrame', f => {
  if (stopped) return;   // frames still in flight after stop must not be written
  fs.writeFileSync(`video/frames-01/${String(n++).padStart(6, '0')}-${Math.round(f.metadata.timestamp * 1000)}.jpg`, Buffer.from(f.data, 'base64'));
  cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
});
await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 80 });
try {
  // … probes …
} finally {
  stopped = true; await cdp.send('Page.stopScreencast').catch(() => {});   // before browser.close()
}
```
Frames arrive only on repaint, each named with its wall-clock ms. Build the clip with each frame held until the next:
```
cd video && python3 - frames-01 <<'PY'
import os, sys; d = sys.argv[1]; fs = sorted(os.listdir(d)); t = [int(f.split('-')[1][:-4]) for f in fs]
with open(d + '.txt', 'w') as o:
    for i, f in enumerate(fs): o.write(f"file '{d}/{f}'\nduration {((t[i+1] - t[i]) / 1000 if i + 1 < len(fs) else 0.5):.3f}\n")
    o.write(f"file '{d}/{fs[-1]}'\n")
open(d + '.start', 'w').write(f"{t[0] / 1000:.3f}")
PY
START=$(cat frames-01.start)
ffmpeg -loglevel error -f concat -safe 0 -i frames-01.txt -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:text='%{pts\:localtime\:$START\:%H\\\\\:%M\\\\\:%S}':x=w-tw-10:y=10:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7,fps=10" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -y rec-01.mp4
```
Decode-check it and look at the clock as above. Screenshots plus a timed log are a fallback only when no motion, timing or fleeting state matters; otherwise agree a narrower mission (step 8 of [write-charter](../../write-charter/SKILL.md)). A house-rules screencast helper is fine once its clips decode-check.

Sound and speech: `grok-bot-box-sound.md`, only when readiness names them.

## Leases

If your house rules provide a lease tool, take a lease before launching a browser, renew it before it expires, and release it after closing the browser (rules: "Leases and locks" in `test-session/references/resource-cleanup.md`). Recording needs no lease. Never leave a browser open between turns.

## Secrets

Ask through Grok Bot's secret request; the secret arrives as an environment variable you use by name (for example `process.env.SHOP_QA_PASSWORD`). Never print it: "Secrets" in `test-session/references/session-rules.md`.
