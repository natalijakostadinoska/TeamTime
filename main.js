const { app, BrowserWindow, dialog } = require('electron');
const path = require('path'), fs = require('fs'), os = require('os'), crypto = require('crypto');
let win, quitting = false;
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
app.on('second-instance', () => { if (win) { win.restore(); win.focus() } });
app.whenReady().then(() => {
  if (!gotLock) return;
  const dir = app.getPath('userData'); fs.mkdirSync(dir, { recursive: true });
  const kf = path.join(dir, 'admin.json'); let key;
  try { key = JSON.parse(fs.readFileSync(kf)).key } catch {}
  if (!key) { key = crypto.randomBytes(16).toString('hex'); fs.writeFileSync(kf, JSON.stringify({ key })) }
  process.env.ADMIN_KEY = key; process.env.PORT = 3000;
  process.chdir(dir);               // data.json is saved in your AppData folder
  process.on('uncaughtException', err => {
    if (err.code === 'EADDRINUSE') { dialog.showErrorBox('TeamTime', 'Port 3000 is already in use by another program (maybe an old node server.js). Close it and start TeamTime Admin again.'); app.exit(1) }
    else dialog.showErrorBox('TeamTime error', String(err.stack || err));
  });
  require('./server.js');           // the server runs inside the app
  const ip = Object.values(os.networkInterfaces()).flat().find(i => i.family === 'IPv4' && !i.internal);
  const addr = 'http://' + (ip ? ip.address : 'localhost') + ':3000';
  win = new BrowserWindow({ width: 1280, height: 820, backgroundColor: '#0f1117', autoHideMenuBar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), additionalArguments: ['--key=' + key], sandbox: false } });
  win.on('page-title-updated', e => e.preventDefault());
  win.setTitle('TeamTime Admin  |  Teammates connect to ' + addr);
  win.loadURL('http://localhost:3000');
  win.on('close', e => {
    if (quitting) return;
    const r = dialog.showMessageBoxSync(win, { type: 'question', buttons: ['Minimize', 'Quit'], defaultId: 0,
      message: 'Quitting stops collecting data from your team.', detail: 'Minimize to keep tracking running in the background.' });
    if (r === 0) { e.preventDefault(); win.minimize() } else quitting = true;
  });
});
app.on('window-all-closed', () => app.quit());