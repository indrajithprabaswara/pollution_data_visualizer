const { JSDOM } = require('jsdom');

const html = `<!DOCTYPE html><body class=""></body>`;
const dom = new JSDOM(html);

global.document = dom.window.document;

function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-mode');
    } else {
        document.body.classList.remove('light-mode');
    }
}

test('applyTheme adds light-mode class when theme is light', () => {
    applyTheme('light');
    expect(document.body.classList.contains('light-mode')).toBe(true);
});

test('applyTheme removes light-mode class when theme is dark', () => {
    document.body.classList.add('light-mode');
    applyTheme('dark');
    expect(document.body.classList.contains('light-mode')).toBe(false);
});
