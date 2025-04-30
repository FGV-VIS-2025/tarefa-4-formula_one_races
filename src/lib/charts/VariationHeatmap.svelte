<!-- ╔══════════════════════════════════════════════════════════════╗
  Early‑Season Volatility Galaxy (2020‑2025) • v5
  – Six discrete colours (quantiles) with a tidy legend strip
  – Hover works reliably via invisible overlay paths
  – Tooltip: total · avg / race · peak swaps + race #
  – Race‑window slider (2–10) now top‑right *above* board, never overlaps
  – Scroll‑wheel still supported · Click row/line locks focus
╚══════════════════════════════════════════════════════════════╝ -->
<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let f1data;
  export let lines = 5;   // initial GP window

  let wrapper, tip;
  let lockSeason = null;

  /* ─── wheel: change race window ─── */
  const wheel = e => {
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
    d3.select(wrapper).selectAll('*').remove();

    /* — dims — */
    const seasonsFilter = [2020, 2021, 2022, 2023, 2024, 2025];
    const W = wrapper.clientWidth,
          H = wrapper.clientHeight,
          M = { top: 70, right: 190, bottom: 45, left: 60 },
          iw = W - M.left - M.right,
          ih = H - M.top - M.bottom;

    /* — data prep — */
    const raw = f1data.driverStandings.filter(d => seasonsFilter.includes(d.season));
    const seasons = d3.rollups(
      raw,
      rows => {
        rows.sort((a,b)=>a.round-b.round);
        const per=Array(lines).fill(0);
        d3.group(rows,d=>d.driverId).forEach(arr=>{
          for(let i=1;i<arr.length && arr[i].round<=lines;i++)
            if(arr[i].position!==arr[i-1].position) per[arr[i].round-1]++;
        });
        const cum=per.reduce((a,v)=>{a.push((a[a.length-1]||0)+v);return a;},[]);
        return {
          per,
          cum,
          total:d3.sum(per),
          avg:+(d3.mean(per)).toFixed(1),
          max:d3.max(per),
          maxRound:per.findIndex(v=>v===d3.max(per))+1
        };
      },
      d=>d.season
    ).map(([season,obj])=>({season,...obj})).sort((a,b)=>a.season-b.season);

    /* — scales — */
    const palette = ['#e10600','#ff7a00','#f8d100','#17c964','#0098ff','#c400ff'];
    const quant = d3.scaleQuantile().domain(seasons.map(d=>d.total)).range(palette);
    const x = d3.scalePoint().domain(d3.range(1,lines+1)).range([0,iw]).padding(0.5);
    const y = d3.scaleLinear().domain([0,d3.max(seasons,d=>d3.max(d.cum))]).nice().range([ih,0]);

    /* — SVG — */
    const svg = d3.select(wrapper).append('svg').attr('width',W).attr('height',H).attr('class','chaos-chart');

    /* title */
    svg.append('text')
      .attr('x',M.left).attr('y',30)
      .attr('fill','#eee').attr('font-size','16px')
      .text(`Cumulative swaps across first ${lines} races (2020‑25)`);

    /* legend strip */
    const legend = svg.append('g').attr('transform',`translate(${M.left},45)`);
    const boxW=14, gap=4;
    legend.selectAll('rect').data(palette).enter().append('rect')
      .attr('x',(_,i)=>i*(boxW+gap))
      .attr('width',boxW).attr('height',6).attr('fill',d=>d);

    /* slider (foreignObject) */
    svg.append('foreignObject')
      .attr('x',W-M.right+30).attr('y',22).attr('width',150).attr('height',24)
      .html(`<div xmlns='http://www.w3.org/1999/xhtml' style='font-size:12px;color:#eee;font-family:Roboto;'>
         Races: <input id='raceRange' type='range' min='2' max='10' value='${lines}' style='width:90px;vertical-align:middle;'>
       </div>`)
      .select('#raceRange')
      .on('input',function(){ lines = +this.value; });

    const g = svg.append('g').attr('transform',`translate(${M.left},${M.top})`);
    const line = d3.line().x((d,i)=>x(i+1)).y(d=>y(d)).curve(d3.curveMonotoneX);

    /* paths + overlay */
    const seasonGrp = g.selectAll('g.season').data(seasons).enter().append('g').attr('class','season');
    seasonGrp.append('path')
      .attr('d',d=>line(d.cum))
      .attr('stroke',d=>quant(d.total)).attr('stroke-width',2).attr('fill','none').attr('opacity',0.75);
    // invisible wide hit‑area
    seasonGrp.append('path')
      .attr('d',d=>line(d.cum))
      .attr('stroke','transparent').attr('stroke-width',12).attr('fill','none')
      .on('mousemove',(e,d)=>hover(e,d))
      .on('mouseleave',()=>hover())
      .on('click',(_,d)=>toggleLock(d.season));

    const dots = g.append('g');
    const track = g.append('line').attr('y1',0).attr('y2',ih).attr('stroke','#bbb').attr('opacity',0);

    /* axes */
    g.append('g').attr('transform',`translate(0,${ih})`).call(d3.axisBottom(x).tickFormat(r=>'Race '+r)).selectAll('text').attr('fill','#ccc');
    g.append('g').call(d3.axisLeft(y)).selectAll('text').attr('fill','#ccc');

    /* leaderboard */
    const board = svg.append('g').attr('transform',`translate(${W-M.right+40},${M.top})`);
    board.append('text').attr('fill','#ccc').attr('y',-20).text('Most swaps');
    const ranked=[...seasons].sort((a,b)=>b.total-a.total);
    const yb=d3.scaleBand().domain(d3.range(ranked.length)).range([0,ih]).padding(0.12);
    const rows=board.selectAll('g.row').data(ranked).enter().append('g').attr('class','row')
      .attr('transform',(_,i)=>`translate(0,${yb(i)})`).attr('cursor','pointer')
      .on('click',(_,d)=>toggleLock(d.season))
      .on('mousemove',(e,d)=>hover(e,d))
      .on('mouseleave',()=>hover());
    rows.append('rect').attr('width',100).attr('height',yb.bandwidth()).attr('fill',d=>quant(d.total));
    rows.append('text').attr('x',105).attr('y',yb.bandwidth()/2).attr('dy','0.35em').attr('fill','#f0f0f0').attr('font-size','12px')
      .text(d=>`${d.season}: ${d.total}`);

    /* hover handler */
    function hover(evt,d){
      if(lockSeason) return;
      seasonGrp.select('path').attr('opacity',s=>s===d?1:0.15); // first path in group
      rows.attr('opacity',r=>r===d?1:0.3);
      if(d){
        const [mx]=evt?d3.pointer(evt,g.node()):[null];
        if(mx!=null) track.attr('x1',mx).attr('x2',mx).attr('opacity',0.9);
        dots.selectAll('circle').data(d.cum).join('circle')
          .attr('cx',(v,i)=>x(i+1)).attr('cy',v=>y(v)).attr('r',4).attr('fill','#fff');
        tip.style.opacity=1;
        if(evt){tip.style.left=evt.clientX+12+'px'; tip.style.top=evt.clientY+12+'px';}
        tip.innerHTML=`<b>${d.season}</b><br>Total: <span style='color:#ffd700'>${d.total}</span>`+
          `<br>Avg/race: ${d.avg}`+
          `<br>Peak: ${d.max} in race ${d.maxRound}`;
      } else {
        track.attr('opacity',0);
        dots.selectAll('*').remove();
        tip.style.opacity=0;
        seasonGrp.select('path').attr('opacity',0.75);
        rows.attr('opacity',1);
      }
    }

    function toggleLock(season){
      if(lockSeason===season){lockSeason=null;hover();return;}
      lockSeason=season;
      seasonGrp.select('path').attr('opacity',p=>p.season===season?1:0.05);
      rows.attr('opacity',r=>r.season===season?1:0.1);
    }
  }
</script>

<div bind:this={wrapper} on:wheel|preventDefault={wheel} style="width:100%;height:100%;position:relative">
  <div bind:this={tip} class="galaxy-tip"></div>
</div>

<style>
  .chaos-chart{font-family:Roboto,Arial,sans-serif}
  .galaxy-tip{position:absolute;pointer-events:none;background:rgba(0,0,0,.85);color:#fff;padding:6px 10px;border-radius:4px;font-size:12px;opacity:0;transition:opacity .15s}
</style>
