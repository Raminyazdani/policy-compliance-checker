const startCase = (s) => String(s ?? '')
  .replace(/[_-]+/g,' ')
  .replace(/\b\w/g, c => c.toUpperCase());

const detectType = (values) => {
  const vs = values.filter(v => v !== null && v !== undefined);
  if (!vs.length) return 'string';
  const all = (pred) => vs.every(pred);
  if (all(v => typeof v === 'number' && Number.isFinite(v))) return 'number';
  if (all(v => typeof v === 'boolean' || v === 0 || v === 1)) return 'boolean';
  if (all(v => Array.isArray(v))) return 'array';
  if (all(v => typeof v === 'object' && !Array.isArray(v))) return 'object';
  return 'string';
};

export function inferColumns(rows, opts = {}) {
  const {
    exclude = [],                 // ['password', ...]
    labels = {},                  // { mfa_enabled: 'MFA' }
    order = [],                   // ['id','field',...]
    render = {},                  // { fieldName: (params)=> JSX }
    format = {},                  // { fieldName: (v)=> string }
    actions = null               // { width?:number, render:(params)=>JSX }
  } = opts;

  const keys = new Set();
  (rows || []).forEach(r => Object.keys(r || {}).forEach(k => {
    if (!exclude.includes(k)) keys.add(k);
  }));

  const ordered = [...order, ...[...keys].filter(k => !order.includes(k))];

  const columns = ordered.map(k => {
    const sampleVals = (rows || []).slice(0, 20).map(r => r?.[k]);
    const t = detectType(sampleVals);

    const col = {
      field: k,
      headerName: labels[k] || startCase(k),
      flex: 1,
      minWidth: 110
    };

    if (render[k]) col.renderCell = render[k];
    if (format[k]) col.valueFormatter = ({ value }) => format[k](value);

    if (!render[k]) {
      if (t === 'number') col.type = 'number';
      if (t === 'boolean') col.renderCell = (p) => (p.value ? 'Yes' : 'No');
      if (t === 'array') col.valueGetter = (value) =>
        Array.isArray(value) ? value.join(', ') : String(value ?? '');
      if (t === 'object') col.valueGetter = (value) =>
        value ? JSON.stringify(value) : '';
    }
    return col;
  });

  if (actions) {
    columns.push({
      field: '_actions',
      headerName: '',
      sortable: false,
      filterable: false,
      width: actions.width ?? 150,
      renderCell: actions.render
    });
  }

  return columns;
}
