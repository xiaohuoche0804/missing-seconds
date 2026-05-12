const { execSync } = require('child_process');
const fs = require('fs');

// Read the chapter content
const content = fs.readFileSync('/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第11章.md', 'utf8');

// Get snapshot to see current state
const snapshot = JSON.parse(execSync('openclaw browser --json snapshot', { encoding: 'utf8' }));
const refs = snapshot.refs;

console.log('URL:', snapshot.url);

// Find the paragraph with placeholder text (content area)
const paragraphEntry = Object.entries(refs).find(([ref, info]) => {
    return info.role === 'paragraph' && info.name && info.name.includes('正文');
});

if (paragraphEntry) {
    const [ref] = paragraphEntry;
    console.log('Found content area:', ref);
    
    // Click on it first
    execSync(`openclaw browser click ${ref}`, { encoding: 'utf8' });
    
    // Copy content to clipboard
    execSync(`echo '${content.replace(/'/g, "'\"'\"'")}' | pbcopy`, { shell: '/bin/bash' });
    
    // Now paste using Command+V
    execSync('openclaw browser press "Meta+v"', { encoding: 'utf8' });
    
    console.log('Content pasted via keyboard');
} else {
    console.log('Content area not found');
    console.log('All refs:', JSON.stringify(refs, null, 2));
}