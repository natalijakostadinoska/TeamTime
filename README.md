# TeamTime

A transparent, consent-based time and productivity tracker for small teams, in the spirit of Workfolio.
Teammates clock in, take breaks and clock out; the admin sees who is working, for how long, and which apps they used.

**English and Македонски** · dark and light mode · Windows

## Features

**Admin app (desktop, Electron)**
- Live dashboard: working / on break / clocked out, worked time, break time, active and idle time
- Productivity ring per person, with apps labeled productive / unproductive / neutral
- Team name and picture, a picture for every person
- Animated background, greeting by time of day, filters, CSV export (7 days)
- Add, remove and re-key teammates (new token button)
- Auto clock-out when an agent goes silent, local-timezone days, automatic data retention

**Teammate app (Windows, Python)**
- Clock in / take a break / resume / clock out
- Progress ring toward a daily goal, live status, top apps, break reminder
- Sees its own stats (nothing hidden from the person being tracked)
- Offline buffering, start with Windows, dark/light and language switch

## Privacy by design

TeamTime tracks only **the name of the app in front** and **active/idle time**, and only while the person is clocked in and not on a break.
It does **not** record keystrokes, screenshots, window titles or website content.
The agent shows a consent screen on first run and displays what it sends.

> Always tell your team what is tracked and why. Tracking people without their knowledge is illegal in many places,
> and monitoring laws (e.g. GDPR-style data protection rules) may apply to you. This is not legal advice.

## Project layout

```
server.js      HTTP server + JSON storage (no dependencies)
index.html     Admin dashboard (served by the server)
main.js        Electron wrapper: runs the server inside a desktop window
preload.js     Passes the admin key to the dashboard
agent.py       Teammate app (Windows, Tkinter)
package.json   Electron + build config
build.bat      Builds TeamTimeAgent.exe and "TeamTime Admin.exe"
```

## Quick start

Requirements: [Node.js](https://nodejs.org) 18+, and for the agent [Python](https://python.org) 3.9+ on Windows.

**Admin app**
```powershell
npm install
npm start
```

**Teammate app**
```powershell
pip install -r requirements.txt
python agent.py
```
In the admin app, add a teammate, copy their token, then enter the server URL (shown in the admin window title) and the token in the agent.

**Server only** (e.g. on a VPS):
```powershell
$env:ADMIN_KEY="a-long-random-password"
node server.js
```
then open `http://localhost:3000` and log in with that key.

## Build the .exe files

```powershell
.\build.bat
```
Output in `dist/`: `TeamTimeAgent.exe` (for teammates) and `TeamTime Admin.exe` (for you).

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `ADMIN_KEY` | `change-me` | Admin password (the desktop app generates its own) |
| `PORT` | `3000` | Server port |
| `TZ_NAME` | `Europe/Skopje` | Timezone used for day boundaries |
| `AUTO_OUT_MIN` | `15` | Minutes of silence before auto clock-out |
| `KEEP_DAYS` | `90` | Days of data to keep |

## Security notes

- Change `ADMIN_KEY` if you run the server yourself; never commit `data.json`, `admin.json` or `config.json` (they are in `.gitignore`).
- The server speaks plain HTTP. For anything beyond a trusted LAN, put it behind HTTPS (Caddy, Cloudflare Tunnel, nginx).
- Tokens can be regenerated from the dashboard if one leaks.

## Roadmap

HTTPS/VPS guide · tray icon and auto-start for the admin app · charts and timelines · Telegram/email alerts · macOS/Linux agent · code signing

## License

MIT, see [LICENSE](mit_license.md).
