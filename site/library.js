/* The September 2026 source receipts, without full manuscript excerpts. */
const searchBox = document.getElementById('library-search');
const typeBox = document.getElementById('library-type');
const resultLine = document.getElementById('library-result');
const resultList = document.getElementById('library-results');
const moreWrap = document.getElementById('library-more-wrap');
const moreButton = document.getElementById('library-more');
let inventory = null;
let limit = 12;

function el(name, className, value) {
  const node = document.createElement(name);
  if (className) node.className = className;
  if (value != null) node.textContent = String(value);
  return node;
}

function link(label, href) {
  const anchor = el('a', '', label);
  anchor.href = href;
  return anchor;
}

function definition(list, term, content) {
  if (!content) return;
  list.append(el('dt', '', term), el('dd', '', content));
}

function pagesFor(record) {
  const groups = Object.entries(record.source_pages || {});
  return groups.map(([ssrn, pages]) => `SSRN ${ssrn}: pp. ${pages.join(', ')}`).join(' · ');
}

function paperCard(paper) {
  const card = el('article');
  card.id = `paper-${paper.key}`;
  card.append(el('span', 'library-meta', `${paper.key} · ${paper.kind} · ${paper.page_count} PDF pages`));
  const heading = el('h3');
  heading.append(link(paper.title, paper.url));
  card.append(heading);
  card.append(el('p', '', paper.contribution));
  const receipt = el('details');
  receipt.append(el('summary', '', 'Scope and source receipt'));
  const list = el('dl');
  definition(list, 'Programme role', paper.role);
  definition(list, 'Evidence in the source inventory', paper.evidence);
  definition(list, 'Current scope at review', paper.scope);
  definition(list, 'Source PDF SHA-256', paper.sha256);
  definition(list, 'Online version', paper.external_version_parity);
  receipt.append(list);
  receipt.append(el('p', 'library-pages', `Indexed prediction-bearing PDF pages: ${paper.indexed_pages.join(', ') || 'none'}. Abstract pages: ${(paper.abstract_pages || []).join(', ') || 'not listed'}. Closing pages: ${(paper.closing_pages || []).join(', ') || 'not listed'}.`));
  if (paper.notice) receipt.append(el('p', '', paper.notice));
  card.append(receipt);
  const footer = el('footer');
  footer.append(link('Original inventory record ↗', paper.original_source), link('SSRN record ↗', paper.url));
  card.append(footer);
  return card;
}

function predictionCard(record) {
  const card = el('article');
  card.id = `prediction-${record.id}`;
  card.append(el('span', 'library-meta', `${record.id} · ${record.domain} · ${record.record_kind}`));
  card.append(el('h3', '', record.title));
  card.append(el('p', '', `Status in the September 2026 inventory: ${record.status}`));
  card.append(el('p', '', `Next test: ${record.next_test}`));
  const receipt = el('details');
  receipt.append(el('summary', '', 'Loss condition, sources and scope'));
  const list = el('dl');
  definition(list, 'Success would mean', record.success_means);
  definition(list, 'Failure would mean', record.failure_means);
  definition(list, 'Original source pages', pagesFor(record));
  definition(list, 'Dependencies', (record.depends_on || []).join(', '));
  definition(list, 'Scope note', record.caveat || record.use_notice);
  definition(list, 'Provenance', record.provenance);
  receipt.append(list);
  card.append(receipt);
  const footer = el('footer');
  footer.append(link('Original inventory record ↗', record.original_source));
  for (const ssrn of record.sources || []) {
    footer.append(link(`SSRN ${ssrn} ↗`, `https://papers.ssrn.com/abstract=${ssrn}`));
  }
  card.append(footer);
  return card;
}

function searchable(record, type) {
  if (type === 'papers') {
    return [record.key, record.title, record.ssrn_id, record.role,
      record.contribution, record.evidence].join(' ').toLocaleLowerCase();
  }
  return [record.id, record.title, record.domain, record.record_kind,
    record.status, record.next_test, ...(record.sources || [])].join(' ').toLocaleLowerCase();
}

function render() {
  if (!inventory) return;
  const type = typeBox.value;
  const records = type === 'papers' ? inventory.papers : inventory.predictions;
  const query = searchBox.value.trim().toLocaleLowerCase();
  const matched = records.filter(record => searchable(record, type).includes(query));
  const fragment = document.createDocumentFragment();
  for (const record of matched.slice(0, limit)) {
    fragment.append(type === 'papers' ? paperCard(record) : predictionCard(record));
  }
  resultList.replaceChildren(fragment);
  const noun = type === 'papers'
    ? (matched.length === 1 ? 'manuscript' : 'manuscripts')
    : (matched.length === 1 ? 'prediction record' : 'prediction records');
  resultLine.textContent = `${matched.length} ${noun} found · showing ${Math.min(limit, matched.length)}. Source inventory dated ${inventory.as_of}.`;
  moreWrap.hidden = matched.length <= limit;
  const anchored = location.hash.slice(1);
  if (anchored && document.getElementById(anchored)) {
    requestAnimationFrame(() => document.getElementById(anchored)?.scrollIntoView({ block: 'start' }));
  }
}

function selectDeepLink() {
  let hash;
  try {
    hash = decodeURIComponent(location.hash.slice(1));
  } catch {
    return;
  }
  if (hash.startsWith('paper-')) {
    typeBox.value = 'papers';
    searchBox.value = hash.slice('paper-'.length);
  } else if (hash.startsWith('prediction-')) {
    typeBox.value = 'predictions';
    searchBox.value = hash.slice('prediction-'.length);
  } else {
    return;
  }
  limit = 12;
  render();
}

searchBox.addEventListener('input', () => { limit = 12; render(); });
typeBox.addEventListener('change', () => { limit = 12; render(); });
moreButton.addEventListener('click', () => { limit += 20; render(); });
window.addEventListener('hashchange', selectDeepLink);

fetch('library-data.json')
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (data.papers.length !== 41 || data.predictions.length !== 82) {
      throw new Error('Unexpected source inventory size');
    }
    inventory = data;
    selectDeepLink();
    render();
  })
  .catch(() => {
    resultLine.replaceChildren(el('span', '', 'The source ledger could not load. '), link('Open the original inventory ↗', 'https://github.com/thantiklermcirony/boundedness-atlas/blob/29a0cfca16ac088cd08e0267b07a50c20eacbc9b/content/atlas.json'));
  });
