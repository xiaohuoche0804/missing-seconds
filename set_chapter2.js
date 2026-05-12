const { execSync } = require('child_process');

// Get current snapshot
const snapshot = JSON.parse(execSync('openclaw browser --json snapshot', { encoding: 'utf8' }));
const targetId = snapshot.targetId;
const refs = snapshot.refs;

// Find textboxes
const textboxes = Object.entries(refs).filter(([ref, info]) => info.role === 'textbox');
console.log('Textboxes found:', textboxes.map(([ref, info]) => `${ref}: ${info.name || 'chapter number'}`));

// e36 should be the title textbox
const titleRef = 'e36';

// Set title via clipboard paste
const title = '第11章 电话';

// Use pbcopy to set clipboard content
const clipCommand = `echo '${title}' | tr -d '\n' | pbcopy`;
execSync(clipCommand, { shell: '/bin/bash' });
console.log('Clipboard set to:', title);

// Click on title input
execSync('openclaw browser click e36', { encoding: 'utf8' });

// Select all and paste
execSync('openclaw browser press "Meta+a"', { encoding: 'utf8' });
execSync('openclaw browser press "Meta+v"', { encoding: 'utf8' });

console.log('Title should be set');

// Verify
const newSnapshot = JSON.parse(execSync('openclaw browser --json snapshot', { encoding: 'utf8' }));
const newRefs = newSnapshot.refs;
const titleBox = newRefs.e36;
console.log('Title box after input:', titleBox);