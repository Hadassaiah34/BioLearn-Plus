// Web assets already live in www. This verifies the entry point before Capacitor sync.
const fs=require('fs');
if(!fs.existsSync('www/index.html')) { console.error('Missing www/index.html'); process.exit(1); }
console.log('BioLearn Plus web assets are ready for Capacitor.');
