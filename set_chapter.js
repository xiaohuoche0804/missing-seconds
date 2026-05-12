const { execSync } = require('child_process');

// Get current snapshot
const snapshot = JSON.parse(execSync('openclaw browser --json snapshot', { encoding: 'utf8' }));
const targetId = snapshot.targetId;
const refs = snapshot.refs;

// Find chapter number textbox (should be e58 based on earlier output)
const chapterInput = refs.e58 ? refs.e58 : null;
const titleInput = Object.entries(refs).find(([ref, info]) => 
  info.role === 'textbox' && info.name && info.name.includes('标题')
);

console.log('Chapter input ref:', chapterInput);
console.log('Title input:', titleInput);

// Set chapter number via click and type
if (chapterInput) {
  execSync('openclaw browser click e58', { encoding: 'utf8' });
  execSync('openclaw browser press "Meta+a"', { encoding: 'utf8' });
  execSync('openclaw browser press "Backspace"', { encoding: 'utf8' });
  execSync('openclaw browser press "1"', { encoding: 'utf8' });
  execSync('openclaw browser press "1"', { encoding: 'utf8' });
  console.log('Chapter number set to 11');
}

// Set title
if (titleInput) {
  const [ref] = titleInput;
  execSync(`openclaw browser click ${ref}`, { encoding: 'utf8' });
  execSync('openclaw browser press "Meta+a"', { encoding: 'utf8' });
  execSync('openclaw browser press "Backspace"', { encoding: 'utf8' });
  
  // Type "第11章 电话" character by character
  const title = '第11章 电话';
  for (const char of title) {
    execSync(`openclaw browser press "${char}"`, { encoding: 'utf8' });
  }
  console.log('Title set to:', title);
}

console.log('Done!');