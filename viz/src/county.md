---
title: County
---

# County totals

Same sums as the national page, split by the county recorded on the company. A blank county is NECUNOSCUT.

```js
const rows = FileAttachment("data/county_year.json").json();
```

```js
const years = [...new Set(rows.map(d => d.fiscal_year))].sort((a, b) => a - b);
const year = view(Inputs.select(years, {label: "Year", value: years[years.length - 1]}));
```

```js
const selected = rows
  .filter(d => d.fiscal_year === year)
  .sort((a, b) => b.turnover_ron - a.turnover_ron);
```

```js
Plot.barX(selected, {y: "county", x: "turnover_ron", tip: true}).plot({
  x: {label: "Turnover (RON)", tickFormat: "~s"},
  y: {label: null},
  marginLeft: 120,
  height: 28 * selected.length
})
```

```js
Inputs.table(selected)
```
