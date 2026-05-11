const CDP = require('./node_modules/chrome-remote-interface');
const fs = require('fs');

const TAB_ID = 'D3920DE23A41CA1AFCC4979AF629B860';

async function main() {
  const client = await CDP({ port: 18800, target: TAB_ID });
  console.log('Connected');
  
  const { Page, Runtime } = client;
  await Page.enable();

  // Navigate to fresh publish page
  console.log('Navigating...');
  await Page.navigate('https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter');
  await new Promise(r => setTimeout(r, 8000));

  // Fill chapter number
  await Runtime.evaluate({
    expression: `var ns=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;var ins=document.querySelectorAll('input');if(ins[0]){ns.call(ins[0],'17');ins[0].dispatchEvent(new Event('input',{bubbles:true}));ins[0].dispatchEvent(new Event('change',{bubbles:true}))}`,
    returnByValue: true
  });
  console.log('Chapter filled');

  // Fill title
  await Runtime.evaluate({
    expression: `var ins=document.querySelectorAll('input');for(var i=0;i<ins.length;i++){if(ins[i].placeholder.includes('标题')){var ns=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;ns.call(ins[i],'第17章 困局');ins[i].dispatchEvent(new Event('input',{bubbles:true}));ins[i].dispatchEvent(new Event('change',{bubbles:true}));return ins[i].value}}`,
    returnByValue: true
  });
  console.log('Title filled');

  // Verify fields
  const fields = await Runtime.evaluate({
    expression: `JSON.stringify(Array.from(document.querySelectorAll('input')).slice(0,5).map(i=>({p:i.placeholder,v:i.value})))`,
    returnByValue: true
  });
  console.log('Fields:', fields);

  // Read chapter content
  let content = fs.readFileSync('第17章.md', 'utf8');
  content = content.replace(/^---\n[\s\S]*?\n---\n/, '');

  // Split by paragraph, wrap in <p>, escape for JS
  const paragraphs = content.split(/\n\n+/);
  const htmlParts = paragraphs.map(p => {
    const cleaned = p.trim().replace(/\n/g, '<br>').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
    return '<p>' + cleaned + '</p>';
  });
  const html = htmlParts.join('');

  // Inject into contenteditable
  console.log('Injecting content...');
  const len = await Runtime.evaluate({
    expression: `(function(){var el=document.querySelector('[contenteditable="true"]');el.focus();el.innerHTML="${html}";el.dispatchEvent(new Event('input',{bubbles:true}));return el.innerText.length})()`,
    returnByValue: true
  });
  console.log('Content length:', len);

  await new Promise(r => setTimeout(r, 2000));

  // Click 存草稿 button
  const btnResult = await Runtime.evaluate({
    expression: `(function(){var btns=document.querySelectorAll('button');for(var i=0;i<btns.length;i++){var t=btns[i].textContent.trim();if(t==='存草稿'){btns[i].click();return 'draft clicked'}else if(t==='下一步'){btns[i].click();return 'next clicked'}}return 'no btn:'+btns.length})()`,
    returnByValue: true
  });
  console.log('Button result:', btnResult);

  await new Promise(r => setTimeout(r, 3000));

  const url = await Runtime.evaluate({ expression: 'window.location.href', returnByValue: true });
  console.log('Current URL:', url);

  console.log('DONE');
  await client.close();
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });