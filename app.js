const gaugeData=[
{label:"ТОВАР НА РБ",value:5319,min:0,max:10000,marks:["0","2.5k","5k","7.5k","10k"]},
{label:"ВНОС / ИЗНОС",value:-1722,min:-4000,max:4000,marks:["-4k","-2k","0","2k","4k"]},
{label:"ССЕЕ + ПОМПИ",value:-2346,min:-5000,max:5000,marks:["-5k","-2.5k","0","2.5k","5k"]},
{label:"АЕЦ",value:1037,min:0,max:2500,marks:["0","0.625k","1.25k","1.875k","2.5k"]},
{label:"ТЕЦ",value:2370,min:0,max:6500,marks:["0","1.625k","3.25k","4.875k","6.5k"]},
{label:"ВЕЦ + МАЛКИ ВЕЦ",value:318,min:0,max:3500,marks:["0","0.875k","1.75k","2.625k","3.5k"]},
{label:"ВЕИ",value:2239,min:0,max:10000,marks:["0","2.5k","5k","7.5k","10k"]}
];
const production=[["АЕЦ Козлодуй","1,037"],["Кондензационни ТЕЦ","1,886"],["Топлофикационни ТЕЦ","375"],["Заводски ТЕЦ","109"],["ВЕЦ","226"],["Малки ВЕЦ","92"],["ВяЕЦ","37"],["ФЕЦ","2,187"],["Био ЕЦ","16"],["ССЕЕ","-2,346"],["Помпни ПАВЕЦ","0"]];
const flows=[["Сърбия",126],["Румъния",-1782],["Турция",-220],["С. Македония",41],["Гърция",113]];
const fmt=n=>n.toLocaleString("en-US");
function gaugeSVG(g){const cx=100,cy=91,r=77;let ticks="";for(let i=0;i<=40;i++){const a=(-135+i*6.75)*Math.PI/180,inner=r-(i%5===0?13:7);ticks+=`<line x1="${cx+Math.cos(a)*inner}" y1="${cy+Math.sin(a)*inner}" x2="${cx+Math.cos(a)*r}" y2="${cy+Math.sin(a)*r}" stroke="${i%5===0?'#43545b':'#9aa8ad'}" stroke-width="${i%5===0?2:1}"/>`}const labels=g.marks.map((m,i)=>{const a=(-135+i*67.5)*Math.PI/180;return `<text x="${cx+Math.cos(a)*54}" y="${cy+Math.sin(a)*54+3}" text-anchor="middle" font-size="8" fill="#45555b">${m}</text>`}).join("");const a=(-135+((g.value-g.min)/(g.max-g.min))*270)*Math.PI/180;return `<svg class="gauge-svg" viewBox="0 0 200 184"><circle cx="100" cy="91" r="82" fill="#e8edef" stroke="#81939a" stroke-width="4"/>${ticks}${labels}<line x1="100" y1="91" x2="${100+Math.cos(a)*49}" y2="${91+Math.sin(a)*49}" stroke="#e43f4d" stroke-width="3.5" stroke-linecap="round"/><circle cx="100" cy="91" r="8" fill="#e43f4d" stroke="#46565d" stroke-width="4"/></svg>`}
document.getElementById("gauges").innerHTML=gaugeData.map(g=>`<article class="gauge-card"><h3>${g.label}</h3>${gaugeSVG(g)}<div class="gauge-value">${fmt(g.value)}</div><div class="gauge-unit">MW</div></article>`).join("");
document.getElementById("production").innerHTML=production.map(([n,v])=>`<div class="production-row"><span>${n}</span><strong>${v} MW</strong></div>`).join("");
document.getElementById("flows").innerHTML=flows.map(([n,v])=>`<div class="flow-row"><span>${n}</span><div class="track"><i class="bar ${v>=0?'pos':'neg'}" style="width:${Math.max(2,Math.abs(v)/1800*45)}%"></i></div><b class="flow-value ${v>=0?'pos-text':'neg-text'}">${v>0?'+':''}${v}</b></div>`).join("");
const svg=document.getElementById("chart"),vals=Array.from({length:100},(_,i)=>3900+Math.sin(i/10)*250+(i>45?(i-45)*25:0)+Math.sin(i*2.1)*35);let grid="";[0,1,2,3,4].forEach(i=>{const y=25+i*35;grid+=`<line x1="35" y1="${y}" x2="620" y2="${y}" stroke="#d4dde0"/><text x="28" y="${y+4}" text-anchor="end" font-size="10" fill="#718087">${Math.round(5700-i*600)}</text>`});const pts=vals.map((v,i)=>`${35+i*5.8},${165-(v-3300)/(5700-3300)*140}`).join(" ");svg.innerHTML=grid+`<polyline points="${pts}" fill="none" stroke="#087f99" stroke-width="2.5"/>`;
function tick(){document.getElementById("clock").textContent=new Date().toLocaleTimeString("bg-BG",{hour12:false})}tick();setInterval(tick,1000);
document.querySelectorAll(".module").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll(".module").forEach(b=>b.classList.toggle("active",b===btn));document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id===btn.dataset.page))}));
document.getElementById("languageBtn").addEventListener("click",()=>alert("Английската версия ще бъде добавена в следващ етап."));
