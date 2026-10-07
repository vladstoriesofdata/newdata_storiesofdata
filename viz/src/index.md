---
title: National
---

# National totals

Every reporting company, summed within the fiscal year. Amounts are RON. Profit margin is sum of reported profit divided by sum of turnover.

```js
const rows = FileAttachment("data/national_year.json").json();
```

```js
Plot.barY(rows, {x: "fiscal_year", y: "turnover_ron", tip: true}).plot({
  y: {label: "Turnover (RON)", tickFormat: "~s"},
  x: {label: "Year"}
})
```

```js
Inputs.table(rows, {format: {
  turnover_ron: d => d.toLocaleString("en-US", {maximumFractionDigits: 0}),
  profit_ron: d => d.toLocaleString("en-US", {maximumFractionDigits: 0}),
  profit_margin: d => (d * 100).toFixed(1) + "%"
}})
```
