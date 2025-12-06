const pptxgen = require('pptxgenjs');
const html2pptx = require('/home/fei/.claude/plugins/marketplaces/anthropic-agent-skills/document-skills/pptx/scripts/html2pptx.js');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Claude Code';
    pptx.title = 'AI Basics - Understanding AI';

    // Slide 1: Title
    await html2pptx('./slide1.html', pptx);

    // Slide 2: Content
    await html2pptx('./slide2.html', pptx);

    // Save
    await pptx.writeFile({ fileName: 'ai-basics.pptx' });
    console.log('Presentation created: ai-basics.pptx');
}

createPresentation().catch(console.error);
