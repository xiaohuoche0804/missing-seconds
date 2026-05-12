const { execSync } = require('child_process');

// First, get the current snapshot to see textboxes
const snapshot = JSON.parse(execSync('openclaw browser --json snapshot', { encoding: 'utf8' }));
const refs = snapshot.refs;

console.log('Current page URL:', snapshot.url);

// Find title textbox
const titleEntry = Object.entries(refs).find(([ref, info]) => 
  info.role === 'textbox' && info.name && info.name.includes('标题')
);

if (titleEntry) {
  const [ref] = titleEntry;
  console.log('Found title textbox:', ref);
  
  // Click on it
  execSync(`openclaw browser click ${ref}`, { encoding: 'utf8' });
  console.log('Clicked on title');
  
  // Use osascript to type Chinese via System Events
  const title = '第11章 电话';
  const script = `
    tell application "System Events"
      keystroke "a" using command down
      delay 0.1
      keystroke "${title}"
    end tell
  `;
  
  try {
    execSync(`osascript -e '${script}'`, { encoding: 'utf8' });
    console.log('Typed title via osascript');
  } catch (e) {
    console.log('osascript error:', e.message);
  }
} else {
  console.log('Title textbox not found, current refs:', JSON.stringify(refs, null, 2));
}