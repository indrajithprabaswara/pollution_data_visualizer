const { JSDOM } = require('jsdom');
const fs = require('fs');

const html = `<!DOCTYPE html><input id="input">`;
const dom = new JSDOM(html);

global.document = dom.window.document;

global.$ = require('jquery')(dom.window);
$.fn.autocomplete = function(opts) { this.data('opts', opts); };

const popularCities = ['New York', 'Los Angeles', 'Chicago', 'Houston'];

function initAutocomplete(input) {
  $(input).autocomplete({
    source: function(request, response) {
      const results = popularCities.filter(c => c.toLowerCase().startsWith(request.term.toLowerCase()));
      response(results);
    },
    minLength: 1,
    delay: 0
  });
}

test('initAutocomplete filters cities based on input', () => {
  initAutocomplete('#input');
  const input = $('#input');
  let results;
  const src = input.data('opts').source;
  src({term: 'n'}, r => results = r);
  expect(results).toEqual(['New York']);
});
