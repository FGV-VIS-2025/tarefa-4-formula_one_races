import * as d3 from "d3";
import { standingsBySeason } from "../standingsUtils";

export function createChart(containerSelector, datasets, optsInit = {}) {
  const cfg = {
    width: 850,
    height: 480,
    margin: { top: 20, right: 120, bottom: 40, left: 40 },
    transitionMs: 800,
    round: null,
    ...optsInit
  };

  const innerW = cfg.width - cfg.margin.left - cfg.margin.right;
  const innerH = cfg.height - cfg.margin.top - cfg.margin.bottom;

  const svg = d3
    .select(containerSelector)
    .append("svg")
    .attr("viewBox", `0 0 ${cfg.width} ${cfg.height}`)
    .attr("preserveAspectRatio", "xMidYMid meet");

  const g = svg
    .append("g")
    .attr("transform", `translate(${cfg.margin.left},${cfg.margin.top})`);

  const x = d3.scalePoint().range([0, innerW]).padding(0.5);
  const y = d3.scaleLinear().range([innerH, 0]);

  const lineGen = d3
    .line()
    .curve(d3.curveMonotoneX)
    .x((d) => x(d.round))
    .y((d) => y(d.position));

  function render() {
    const raw = standingsBySeason(
      cfg.mode === "constructor"
        ? datasets.constructorStandings
        : datasets.driverStandings,
      +cfg.season,
      cfg.mode === "constructor" ? "constructor" : "driver"
    );

    const roundsAll = [...new Set(raw.map((d) => d.round))].sort((a, b) => a - b);
    if (cfg.round === null) {
      cfg.round = roundsAll[roundsAll.length - 1];
    }
    const lastRound = Math.min(cfg.round, roundsAll[roundsAll.length - 1]);

    const filtered = raw.filter((d) => d.round <= lastRound);

    const rounds = roundsAll.filter((r) => r <= lastRound);

    const groups = d3.group(filtered, (d) => d.key);
    const series = Array.from(groups, ([key, vals]) => ({
      key,
      values: vals.sort((a, b) => a.round - b.round)
    }));

    x.domain(rounds);
    y.domain([d3.max(raw, (d) => d.position), 1]);

    g.selectAll(".axis").remove();
    g
      .append("g")
      .attr("class", "axis axis-x")
      .attr("transform", `translate(0,${innerH})`)
      .call(d3.axisBottom(x).tickSizeOuter(0));
    g
      .append("g")
      .attr("class", "axis axis-y")
      .call(
        d3
          .axisLeft(y)
          .tickValues([1, 5, 10, 15, 20])
          .tickFormat(d3.format("d"))
          .tickSizeOuter(0)
      );

    const lineGroup = g.selectAll(".series").data(series, (d) => d.key);
    lineGroup.exit().remove();
    const lineEnter = lineGroup.enter().append("g").attr("class", "series");

    lineEnter
      .append("path")
      .attr("class", "line")
      .attr("fill", "none")
      .attr("stroke-width", 1.5)
      .merge(lineGroup.select("path.line"))
      .transition()
      .duration(cfg.transitionMs)
      .attr("stroke", (d, i) => d3.schemeTableau10[i % 10])
      .attr("d", (d) => lineGen(d.values));

    lineEnter
      .selectAll("circle")
      .data((d) => d.values.map((v) => ({ key: d.key, data: v })))
      .enter()
      .append("circle")
      .attr("r", 3)
      .attr("fill", (d, i) => d3.schemeTableau10[i % 10])
      .merge(lineGroup.selectAll("circle"))
      .transition()
      .duration(cfg.transitionMs)
      .attr("cx", (d) => x(d.data.round))
      .attr("cy", (d) => y(d.data.position));

    const labels = g.selectAll(".end-label").data(series, (d) => d.key);
    labels.exit().remove();
    labels
      .enter()
      .append("text")
      .attr("class", "end-label")
      .merge(labels)
      .transition()
      .duration(cfg.transitionMs)
      .attr("x", innerW + 5)
      .attr("y", (d) => {
        const last = d.values.find((v) => v.round === lastRound);
        return last ? y(last.position) : y(d.values[d.values.length - 1].position);
      })
      .text((d) => d.key)
      .style("font-size", "0.75rem")
      .style("dominant-baseline", "middle");
  }

  render();

  return {
    update(opts = {}) {
      Object.assign(cfg, opts);
      render();
    },
    destroy() {
      d3.select(containerSelector).selectAll("*").remove();
    }
  };
}
