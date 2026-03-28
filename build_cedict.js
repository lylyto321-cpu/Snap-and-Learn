const https = require('https');
const zlib = require('zlib');
const fs = require('fs');
const path = require('path');

const URL = 'https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz';
const OUTPUT = path.join(__dirname, 'www', 'cedict.json');

// Tone mark mappings for numbered pinyin -> tone-marked pinyin
const toneMarks = {
  a: ['ā', 'á', 'ǎ', 'à', 'a'],
  e: ['ē', 'é', 'ě', 'è', 'e'],
  i: ['ī', 'í', 'ǐ', 'ì', 'i'],
  o: ['ō', 'ó', 'ǒ', 'ò', 'o'],
  u: ['ū', 'ú', 'ǔ', 'ù', 'u'],
  ü: ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
};

function convertSyllable(syllable) {
  // Handle "r5", "xx5" etc (neutral tone / no tone number)
  const match = syllable.match(/^([a-züÜ]+?)([1-5])$/i);
  if (!match) return syllable.toLowerCase();

  let letters = match[1].toLowerCase();
  const tone = parseInt(match[2]);

  // Replace v/u: with ü
  letters = letters.replace(/u:/g, 'ü').replace(/v/g, 'ü');

  if (tone === 5) return letters; // neutral tone, no mark

  // Find which vowel to put the tone mark on (standard rules):
  // 1. If there is an 'a' or 'e', put tone on it
  // 2. If there is 'ou', put tone on 'o'
  // 3. Otherwise put tone on the last vowel
  const vowels = 'aeiouü';

  let idx = -1;
  if (letters.includes('a')) {
    idx = letters.indexOf('a');
  } else if (letters.includes('e')) {
    idx = letters.indexOf('e');
  } else if (letters.includes('ou')) {
    idx = letters.indexOf('o');
  } else {
    // last vowel
    for (let i = letters.length - 1; i >= 0; i--) {
      if (vowels.includes(letters[i])) {
        idx = i;
        break;
      }
    }
  }

  if (idx === -1) return letters;

  const vowel = letters[idx];
  const marked = toneMarks[vowel] ? toneMarks[vowel][tone - 1] : vowel;
  return letters.substring(0, idx) + marked + letters.substring(idx + 1);
}

function numberedToToneMarked(pinyin) {
  // Split pinyin string into syllables and convert each
  // CEDICT pinyin looks like: "ni3 hao3"
  return pinyin
    .split(/\s+/)
    .map(s => convertSyllable(s))
    .join(' ');
}

function download(url) {
  return new Promise((resolve, reject) => {
    const request = (u) => {
      https.get(u, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          request(res.headers.location);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}`));
          return;
        }
        const chunks = [];
        res.on('data', c => chunks.push(c));
        res.on('end', () => resolve(Buffer.concat(chunks)));
        res.on('error', reject);
      }).on('error', reject);
    };
    request(url);
  });
}

async function main() {
  console.log('Downloading CEDICT...');
  const gzData = await download(URL);
  console.log(`Downloaded ${(gzData.length / 1024).toFixed(0)} KB compressed`);

  const raw = zlib.gunzipSync(gzData).toString('utf-8');
  const lines = raw.split('\n');

  const dict = {};
  let count = 0;

  for (const line of lines) {
    if (line.startsWith('#') || !line.trim()) continue;

    // CEDICT format: traditional simplified [pinyin] /def1/def2/.../
    const m = line.match(/^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+\/(.+)\/\s*$/);
    if (!m) continue;

    const simplified = m[2];
    const pinyinRaw = m[3];
    const defsRaw = m[4];

    // Only include entries up to 4 characters
    if (simplified.length > 4) continue;

    // Skip if already have this entry (keep first occurrence = most common)
    if (dict[simplified]) continue;

    const py = numberedToToneMarked(pinyinRaw);
    // Take first definition, clean it up
    const en = defsRaw.split('/')[0].trim();

    if (!en) continue;

    dict[simplified] = { py, en };
    count++;
  }

  console.log(`Parsed ${count} entries`);

  const json = JSON.stringify(dict);
  fs.writeFileSync(OUTPUT, json, 'utf-8');
  const sizeMB = (Buffer.byteLength(json, 'utf-8') / (1024 * 1024)).toFixed(2);
  console.log(`Wrote ${OUTPUT} (${sizeMB} MB)`);
}

main().catch(err => { console.error(err); process.exit(1); });
