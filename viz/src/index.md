---
title: Daily revenue
---

# Daily revenue

Sample page for a mid-market client. The bars read `semantic/daily_revenue.sql`. Copy this file when the next chart needs a new page.

```js
const data = FileAttachment("data/daily_revenue.json").json();
```

```js
Plot.barY(data, {
  x: "order_date",
  y: "revenue",
  fill: "channel",
  tip: true
}).plot({color: {legend: true}})
```

The same extract is drawn with D3 in `viz/preview/index.html` when a deliverable should be one HTML file and nothing else.
