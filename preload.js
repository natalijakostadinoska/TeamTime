const { contextBridge } = require('electron');
const a = process.argv.find(x => x.startsWith('--key='));
contextBridge.exposeInMainWorld('ADMIN_KEY', a ? a.slice(6) : '');
