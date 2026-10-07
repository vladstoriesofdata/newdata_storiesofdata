---
title: Company
---

# One company

Search by name, brand, or CUI. The series is the reported statement. Sparse lines are blank when the filing did not include them.

```js
const companies = FileAttachment("data/companies.json").json();
const series = FileAttachment("data/company_year.json").json();
```

```js
const query = view(Inputs.text({label: "Name, brand, or CUI", placeholder: "McDonald"}));
```

```js
const matches = companies.filter(company => {
  const text = query.trim().toLowerCase();
  if (!text) return false;
  return [company.company_name, company.brand, String(company.cui)]
    .join(" ")
    .toLowerCase()
    .includes(text);
}).slice(0, 20);
```

```js
const options = matches.length
  ? matches
  : [{company_name: "Type a name or CUI", cui: null}];
const selected = view(Inputs.select(options, {
  label: "Match",
  format: company => company.cui ? `${company.company_name} (${company.cui})` : company.company_name
}));
```

```js
const history = series
  .filter(row => selected && selected.cui && row.cui === selected.cui)
  .sort((a, b) => a.fiscal_year - b.fiscal_year);
```

```js
display(selected && selected.cui
  ? html`<p>${selected.brand} · ${selected.county} · ${selected.locality} · CAEN ${selected.caen} ${selected.caen_label}</p>`
  : html`<p>Type a name or CUI.</p>`);
```

```js
Plot.lineY(history, {x: "fiscal_year", y: "turnover_ron", tip: true, marker: true}).plot({
  y: {label: "Turnover (RON)", tickFormat: "~s"},
  x: {label: "Year"}
})
```

```js
Inputs.table(history)
```
