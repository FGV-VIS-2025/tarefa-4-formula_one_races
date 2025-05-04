<!-- ╔══════════════════════════════════════════════════════════════╗
  Early‑Season Volatility Galaxy (2020‑2025) • v5
  – Six discrete colours (quantiles) with a tidy legend strip
  – Hover works reliably via invisible overlay paths
  – Tooltip: total · avg / race · peak swaps + race #
  – Race‑window slider (2–10) now top‑right *above* board, never overlaps
  – Scroll‑wheel still supported · Click row/line locks focus
╚══════════════════════════════════════════════════════════════╝ -->
<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";

  export let f1data;
  export let lines = 1; // initial GP window

  let wrapper, tip;
  let lockSeason = null;

  /* ─── wheel: change race window ─── */
  const wheel = (e) => {
    if (e.ctrlKey) return;
    e.preventDefault();
    lines = Math.min(10, Math.max(2, lines + (e.deltaY > 0 ? 1 : -1)));
  };

  $: if (f1data) draw();
  onMount(() => {
    const ro = new ResizeObserver(draw);
    ro.observe(wrapper);
    return () => ro.disconnect();
  });

  function draw() {
    if (!wrapper || !f1data) return;
    d3.select(wrapper).selectAll("*").remove();

    let seasonsFilter = f1data.driverStandings.map((d) => d.season);
    seasonsFilter = [...new Set(seasonsFilter)].sort((a, b) => a - b);
    let last_season = seasonsFilter[seasonsFilter.length - 1];
    seasonsFilter = seasonsFilter.filter((d) => d >= last_season - 4);

    /* — dims — */
    const W = wrapper.clientWidth,
      H = wrapper.clientHeight,
      M = { top: 70, right: 190, bottom: 50, left: 80 },
      iw = W - M.left - M.right,
      ih = H - M.top - M.bottom;

    /* — data prep — */
    const raw = f1data.driverStandings.filter((d) =>
      seasonsFilter.includes(d.season),
    );

    const seasons = d3
      .rollups(
        raw,
        (rows) => {
          rows.sort((a, b) => a.round - b.round);
          let season_lines = d3.max(rows, (d) => d.round);
          lines = Math.max(lines, season_lines);
          const per = Array(season_lines).fill(0);
          d3.group(rows, (d) => d.driverId).forEach((arr) => {
            for (let i = 1; i < arr.length && arr[i].round <= season_lines; i++)
              if (arr[i].position !== arr[i - 1].position)
                per[arr[i].round - 1]++;
          });
          const cum = per.reduce((a, v) => {
            a.push((a[a.length - 1] || 0) + v);
            return a;
          }, []);
          const std = per.map((_, i, arr) => 
            d3.deviation(arr.slice(Math.max(0, i - season_lines + 1), i + 1)) / 100
          ).slice(1)
          return {
            per,
            cum,
            std,
            total: d3.sum(per),
            avg: +d3.mean(per).toFixed(1),
            max: d3.max(per),
            maxRound: per.findIndex((v) => v === d3.max(per)) + 1,
          };
        },
        (d) => d.season,
      )
      .map(([season, obj]) => ({ season, ...obj }))
      .sort((a, b) => a.season - b.season);
      
    /* — scales — */
    const palette = [
      "#e10600",
      "#ff7a00",
      "#f8d100",
      "#17c964",
      "#0098ff",
      "#c400ff",
    ];
    const quant = d3
      .scaleQuantile()
      .domain(seasons.map((d) => d.total))
      .range(palette);
    const x = d3
      .scalePoint()
      .domain(d3.range(1, lines + 1))
      .range([0, iw])
      .padding(0.5);
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(seasons, (d) => d3.max(d.std))])
      .nice()
      .range([ih, 0]);

    /* — SVG — */
    const svg = d3
      .select(wrapper)
      .append("svg")
      .attr("width", W)
      .attr("height", H)
      .attr("class", "chaos-chart");

    /* title */
    svg
      .append("text")
      .attr("x", M.left)
      .attr("y", 30)
      .attr("fill", "#eee")
      .attr("font-size", "22px")
      .attr("font-weight", "bold")
      .style("font-family", "var(--font-f1)")
      .text(`Volatilidade das Trocas de Posição`);

    const g = svg
      .append("g")
      .attr("transform", `translate(${M.left},${M.top})`);
    const line = d3
      .line()
      .x((d, i) => x(i + 1))
      .y((d) => y(d))
      .curve(d3.curveMonotoneX);

    /* Labels */
    g.append("text")
      .attr("transform", `rotate(-90)`)
      .attr("x", -ih / 2)
      .attr("y", -M.left + 30)
      .attr("fill", "#ccc")
      .attr("text-anchor", "middle")
      .style("font-family", "var(--font-f1)")
      .text("Volatilidade até a rodada (%)");

    g.append("text")
      .attr("x", iw / 2)
      .attr("y", ih + M.bottom - 10)
      .attr("fill", "#ccc")
      .attr("text-anchor", "middle")
      .style("font-family", "var(--font-f1)")
      .text("Rodada");

    // Add a line of domain with small ticks
    const domainLine = g.append("g").attr("class", "domain-line");
    domainLine
      .append("line")
      .attr("x1", 0)
      .attr("x2", iw)
      .attr("y1", y(0))
      .attr("y2", y(0))
      .attr("stroke", "#ccc")
      .attr("stroke-width", 1);

    domainLine
      .append("line")
      .attr("x1", 0)
      .attr("x2", 0)
      .attr("y1", 0)
      .attr("y2", ih)
      .attr("stroke", "#ccc")
      .attr("stroke-width", 1);

    const ticksX = d3.range(1, lines + 1);
    domainLine
      .selectAll("line.tick-x")
      .data(ticksX)
      .enter()
      .append("line")
      .attr("class", "tick-x")
      .attr("x1", (d) => x(d))
      .attr("x2", (d) => x(d))
      .attr("y1", y(0))
      .attr("y2", y(0) + 5)
      .attr("stroke", "#ccc")
      .attr("stroke-width", 1);

    const ticksY = y.ticks(6);
    domainLine
      .selectAll("line.tick-y")
      .data(ticksY)
      .enter()
      .append("line")
      .attr("class", "tick-y")
      .attr("x1", 0)
      .attr("x2", -5)
      .attr("y1", (d) => y(d))
      .attr("y2", (d) => y(d))
      .attr("stroke", "#ccc")
      .attr("stroke-width", 1);

    /* paths + overlay */
    const seasonGrp = g
      .selectAll("g.season")
      .data(seasons)
      .enter()
      .append("g")
      .attr("class", "season");
    seasonGrp
      .append("path")
      .attr("d", (d) => line(d.std))
      .attr("stroke", (d) => quant(d.total)) // Set stroke color based on quantile scale
      .attr("stroke-width", 2)
      .attr("fill", "none")
      .attr("opacity", 0.75);
    // invisible wide hit‑area
    seasonGrp
      .append("path")
      .attr("d", (d) => line(d.std))
      .attr("stroke", "transparent")
      .attr("stroke-width", 12)
      .attr("fill", "none")
      .on("mousemove", (e, d) => hover(e, d))
      .on("mouseleave", () => hover())
      .on("click", (_, d) => toggleLock(d.season));

    const dots = g.append("g");

    /* axes */
    g.append("g")
      .attr("transform", `translate(0,${ih})`)
      .call(d3.axisBottom(x).tickFormat((r) => r + 1))
      .selectAll("text")
      .style("font-family", "var(--font-f1)")
      .attr("font-size", "10px")
      .attr("fill", "#ccc");
    g.append("g")
      .call(d3.axisLeft(y).ticks(5).tickFormat(d3.format(".0%")))
      .selectAll("text")
      .style("font-family", "var(--font-f1)")
      .attr("font-size", "10px")
      .attr("fill", "#ccc");

    /* leaderboard */
    const board = svg
      .append("g")
      .attr("transform", `translate(${W - M.right + 40},${M.top})`);
    board.append("text").attr("fill", "#ccc").attr("y", -20).text("Temporada");
    const yb = d3
      .scaleBand()
      .domain(d3.range(seasons.length))
      .range([0, ih])
      .padding(0.12);
    const rows = board
      .selectAll("g.row")
      .data(seasons)
      .enter()
      .append("g")
      .attr("class", "row")
      .attr("transform", (_, i) => `translate(0,${yb(i)})`)
      .attr("cursor", "pointer")
      .on("click", (_, d) => toggleLock(d.season))
      .on("mousemove", (e, d) => hover(e, d))
      .on("mouseleave", () => hover());
    rows
      .append("rect")
      .attr("width", 20)
      .attr("height", 20)
      .attr("fill", (d) => quant(d.total));
    rows
      .append("text")
      .attr("x", 25)
      .attr("y", 10)
      .attr("dy", "0.35em")
      .attr("fill", "#f0f0f0")
      .attr("font-size", "12px")
      .text((d) => d.season);

    /* hover handler */
    function hover(evt, d) {
      if (lockSeason) return;
      seasonGrp.select("path").attr("opacity", (s) => (s === d ? 1 : 0.15)); // first path in group
      rows.attr("opacity", (r) => (r === d ? 1 : 0.3));
      if (d) {
        const [mx] = evt ? d3.pointer(evt, g.node()) : [null];
        if (mx != null)
        dots
          .selectAll("circle")
          .data(d.std)
          .join("circle")
          .attr("cx", (v, i) => x(i + 1))
          .attr("cy", (v) => y(v))
          .attr("r", 4)
          .attr("fill", "#fff");
        tip.style.opacity = 1;
        if (evt) {
          tip.style.left = evt.clientX + 12 + "px";
          tip.style.top = evt.clientY + 12 + "px";
        }
        tip.innerHTML =
          `<b>${d.season}</b><br>Total: <span style='color:#ffd700'>${d.total}</span>` +
          `<br>Avg/race: ${d.avg}` +
          `<br>Peak: ${d.max} in race ${d.maxRound}`;
      } else {
        dots.selectAll("*").remove();
        tip.style.opacity = 0;
        seasonGrp.select("path").attr("opacity", 0.75);
        rows.attr("opacity", 1);
      }
    }

    function toggleLock(season) {
      if (lockSeason === season) {
        lockSeason = null;
        hover();
        return;
      }
      lockSeason = season;
      seasonGrp
        .select("path")
        .attr("opacity", (p) => (p.season === season ? 1 : 0.05));
      rows.attr("opacity", (r) => (r.season === season ? 1 : 0.1));
    }
  }
</script>

<div
  bind:this={wrapper}
  on:wheel|preventDefault={wheel}
  style="width:100%;height:100%;position:relative"
>
  <div bind:this={tip} class="galaxy-tip"></div>
</div>

<style>
  .chaos-chart {
    font-family: Roboto, Arial, sans-serif;
  }
  .galaxy-tip {
    position: absolute;
    pointer-events: none;
    background: rgba(0, 0, 0, 0.85);
    color: #fff;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
    opacity: 0;
    transition: opacity 0.15s;
  }
</style>
