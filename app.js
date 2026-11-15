const API = {
  generation: "https://www.eso.bg/api/rabota_na_EEC_json.php",
  flows: "https://www.eso.bg/api/scada_live_json_pure.php",
  frequency: "https://www.eso.bg/api/freq.json.php",
  load: "https://raw.githubusercontent.com/yyoncho/eso-dashboard/data/data/today.jsonl",
  ibex: "https://api.energy-charts.info/price?bzn=BG",
  npp: "https://www.kznpp.org/bg/proizvodstvo/danni-za-elektroproizvodstvoto"
};
const $ = s => document.querySelector(s);
const fmt = (n,d=0) => Number(n).toLocaleString("bg-BG",{maximumFractionDigits:d,minimumFractionDigits:d});
const state = {lastUpdated:null, loadSeries:[], values:{}};
const gaugeDefs = [
  {key:"load",label:"ТОВАР НА РБ",min:0,max:10000,marks:["0","2.5k","5k","7.5k","10k"]},
  {key:"net",label:"ВНОС / ИЗНОС",min:-4000,max:4000,marks:["-4k","-2k","0","2k","4k"]},
  {key:"bess",label:"ССЕЕ + ПОМПИ",min:-5000,max:5000,marks:["-5k","-2.5k","0","2.5k","5k"]},
  {key:"nuclear",label:"АЕЦ",min:0,max:2500,marks:["0","0.625k","1.25k","1.875k","2.5k"]},
  {key:"thermal",label:"ТЕЦ",min:0,max:6500,marks:["0","1.625k","3.25k","4.875k","6.5k"]},
  {key:"hydro",label:"ВЕЦ + МАЛКИ ВЕЦ",min:0,max:3500,marks:["0","0.875k","1.75k","2.625k","3.5k"]},
  {key:"renew",label:"ВЕИ",min:0,max:10000,marks:["0","2.5k","5k","7.5k","10k"]}
];
const productionDefs = [["АЕЦ Козлодуй","АЕЦ"],["Кондензационни ТЕЦ","Кондензационни ТЕЦ"],["Топлофикационни ТЕЦ","Топлофикационни ТЕЦ"],["Заводски ТЕЦ","Заводски ТЕЦ"],["ВЕЦ","ВЕЦ"],["Малки ВЕЦ","Малки ВЕЦ"],["ВяЕЦ","ВяЕЦ"],["ФЕЦ","ФЕЦ"],["Био ЕЦ","Био ЕЦ"],["ССЕЕ","ССЕЕ"],["Помпи ПАВЕЦ","Помпи"]];
const countries = [["Сърбия","SR_mw"],["Румъния","RO_mw"],["Турция","TR_mw"],["С. Македония","MK_mw"],["Гърция","GR_mw"]];
function gaugeSvg(g,v){
  const cx=100,cy=91,r=77;
  const valid=v!==null&&v!==undefined&&Number.isFinite(Number(v));
  let ticks="";
  for(let i=0;i<=40;i++){
    const a=(150+i*6)*Math.PI/180;
    const inner=r-(i%5===0?15:8);
    ticks+=`<line x1="${cx+Math.cos(a)*inner}" y1="${cy+Math.sin(a)*inner}" x2="${cx+Math.cos(a)*r}" y2="${cy+Math.sin(a)*r}" stroke="${i%5===0?"#263b43":"#71838a"}" stroke-width="${i%5===0?2.8:1.5}"/>`;
  }
  const labels=g.marks.map((m,i)=>{
    const a=(150+i*60)*Math.PI/180;
    return `<text x="${cx+Math.cos(a)*54}" y="${cy+Math.sin(a)*54+4}" text-anchor="middle" font-size="9" font-weight="800" fill="#263b43">${m}</text>`;
  }).join("");
  let needle="";
  if(valid){
    const ratio=Math.max(0,Math.min(1,(Number(v)-g.min)/(g.max-g.min)));
    const a=(150+ratio*240)*Math.PI/180;
    const tipX=cx+Math.cos(a)*53,tipY=cy+Math.sin(a)*53;
    const tailX=cx-Math.cos(a)*11,tailY=cy-Math.sin(a)*11;
    needle=`<line x1="${tailX}" y1="${tailY}" x2="${tipX}" y2="${tipY}" stroke="#5b252a" stroke-width="8" stroke-linecap="round"/><line x1="${tailX}" y1="${tailY}" x2="${tipX}" y2="${tipY}" stroke="#e32636" stroke-width="4.5" stroke-linecap="round"/>`;
  }
  return `<svg class="gauge-svg" viewBox="0 0 200 184" role="img" aria-label="${g.label}: ${valid?fmt(Number(v))+" MW":"няма данни"}">
    <circle cx="100" cy="91" r="82" fill="#eef2f3" stroke="#71858d" stroke-width="4"/>
    ${ticks}${labels}${needle}
    <circle cx="100" cy="91" r="10" fill="#263b43" stroke="#eef2f3" stroke-width="2"/>
    <circle cx="100" cy="91" r="5" fill="#e32636"/>
  </svg>`;
}
function renderGauges(data={}){$("#gauges").innerHTML=gaugeDefs.map(g=>{const v=data[g.key];return `<article class="gauge-card"><h3>${g.label}</h3>${gaugeSvg(g,v)}<div class="gauge-value">${v==null?"—":fmt(v)}</div><div class="gauge-unit">MW</div></article>`;}).join("")+`<section class="panel npp npp-gauge-slot"><h2>АЕЦ КОЗЛОДУЙ — БЛОК 5 / БЛОК 6</h2><div class="unit"><b>БЛОК 5</b><strong class="blue">— MW</strong><small>СТАТУС НЕПОТВЪРДЕН</small></div><div class="unit"><b>БЛОК 6</b><strong class="green">— MW</strong><small>СТАТУС НЕПОТВЪРДЕН</small></div><div class="total"><b>ОБЩО АЕЦ КОЗЛОДУЙ</b><strong>— MW</strong></div><p class="note">Източникът за данните на блокове 5 и 6 предстои да бъде свързан.</p></section>`;}
function renderProduction(data={}){$("#production").innerHTML=productionDefs.map(([label,key])=>{const v=data[key];return `<div class="production-row"><span>${label}</span><strong>${v==null?"—":fmt(v)+" MW"}</strong></div>`;}).join("");}
function renderFlows(data={}){$("#flows").innerHTML=countries.map(([name,key])=>{const v=data[key];const width=v==null?0:Math.min(45,Math.abs(v)/1800*45);return `<div class="flow-row"><span>${name}</span><div class="track"><i class="bar ${v>=0?"pos":"neg"}" style="width:${width}%"></i></div><b class="flow-value ${v>=0?"pos-text":"neg-text"}">${v==null?"—":(v>0?"+":"")+fmt(v)}</b></div>`;}).join("");}
function flatten(obj,out={}){if(Array.isArray(obj)){for(const x of obj){if(Array.isArray(x)&&x.length>=2&&typeof x[0]==="string")out[x[0]]=x[1];flatten(x,out);}}else if(obj&&typeof obj==="object"){for(const [k,v] of Object.entries(obj)){if(v==null||typeof v!=="object")out[k]=v;else flatten(v,out);}}return out;}
function norm(s){return String(s).toLowerCase().replace(/\s+/g," ").trim();}
function num(v){if(typeof v==="number"&&Number.isFinite(v))return v;if(typeof v==="string"){const n=Number(v.replace(/\s/g,"").replace(",","."));if(Number.isFinite(n))return n;}return null;}
function pick(flat,...names){for(const name of names){const target=norm(name);for(const [k,v] of Object.entries(flat)){if(norm(k)===target||norm(k).startsWith(target)){const n=num(v);if(n!=null)return n;}}}return null;}
async function getJson(url){const u=url+(url.includes("?")?"&":"?")+"_="+Date.now();const r=await fetch(u,{cache:"no-store",headers:{"Accept":"application/json,text/plain,*/*"}});if(!r.ok)throw Error("HTTP "+r.status);return r.json();}
async function getText(url){const r=await fetch(url+"?t="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);return r.text();}
async function updateGeneration(){const raw=await getJson(API.generation);const f=flatten(raw);const d={};for(const k of ["АЕЦ","Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ","ВЕЦ","Малки ВЕЦ","ВяЕЦ","ФЕЦ","Био ЕЦ","Помпи"]){const v=pick(f,k);if(v!=null)d[k]=v;}const ch=pick(f,"ССЕБ - зареждане","ССЕЕ - зареждане"),dis=pick(f,"ССЕБ - разреждане","ССЕЕ - разреждане");if(ch!=null||dis!=null)d.bessNet=(dis||0)-(ch||0);const nuclear=d["АЕЦ"],thermal=["Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ"].some(k=>d[k]!=null)?["Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ"].reduce((s,k)=>s+(d[k]||0),0):null;const hydro=d["ВЕЦ"]!=null||d["Малки ВЕЦ"]!=null?(d["ВЕЦ"]||0)+(d["Малки ВЕЦ"]||0):null;const renew=["ВяЕЦ","ФЕЦ","Био ЕЦ"].some(k=>d[k]!=null)?(d["ВяЕЦ"]||0)+(d["ФЕЦ"]||0)+(d["Био ЕЦ"]||0):null;const pump=d["Помпи"], bess=d.bessNet;const battery=(pump??0)-(bess??0);state.values={...state.values,...d,nuclear,thermal,hydro,renew,bess:bess==null&&pump==null?null:battery};}
async function updateFlows(){const raw=await getJson(API.flows);const f=flatten(raw);const d={};for(const [key,...aliases] of [["SR_mw","SR","Сърбия","Serbia"],["RO_mw","RO","Румъния","Romania"],["TR_mw","TR","Турция","Turkey"],["MK_mw","MK","Македония","Северна Македония","North Macedonia"],["GR_mw","GR","Гърция","Greece"]])d[key]=pick(f,key,...aliases);if(Object.values(d).some(v=>v!=null)){state.values={...state.values,...d};const vals=Object.values(d).filter(v=>v!=null);state.values.net=-vals.reduce((a,b)=>a+b,0);}}
async function updateLoad(){const text=await getText(API.load);const rows=text.split(/\r?\n/).filter(Boolean).map(x=>{try{return JSON.parse(x)}catch{return null}}).filter(Boolean);const pts=rows.map(r=>({t:r.timestamp_utc||r.timestamp,v:num(r.load_mw??r["Товар на РБ"])})).filter(x=>x.t&&x.v!=null&&x.v>0).slice(-288);if(!pts.length)throw Error("Няма стойности в JSONL");state.loadSeries=pts;state.values.load=pts[pts.length-1].v;renderChart(pts);}
function renderChart(points){const svg=$("#chart");if(!points||points.length<2){svg.innerHTML="";return;}const vals=points.map(p=>p.v),lo=Math.min(...vals)-100,hi=Math.max(...vals)+100;const x0=42,x1=620,y0=25,y1=158;let grid="";for(let i=0;i<5;i++){const y=y0+i*(y1-y0)/4,v=hi-(hi-lo)*i/4;grid+=`<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="#d4dde0"/><text x="34" y="${y+4}" text-anchor="end" font-size="10" fill="#718087">${Math.round(v)}</text>`;}const coords=vals.map((v,i)=>`${x0+i*(x1-x0)/Math.max(1,vals.length-1)},${y1-(v-lo)/(hi-lo)*(y1-y0)}`).join(" ");let timeLabels="";for(let i=0;i<5;i++){const index=Math.round(i*(points.length-1)/4),stamp=Date.parse(points[index].t);const label=Number.isFinite(stamp)?new Date(stamp).toLocaleTimeString("bg-BG",{timeZone:"Europe/Sofia",hour:"2-digit",minute:"2-digit",hour12:false}):"";const x=x0+i*(x1-x0)/4;timeLabels+=`<line x1="${x}" y1="${y1}" x2="${x}" y2="${y1+4}" stroke="#718087"/><text x="${x}" y="180" text-anchor="middle" font-size="11" font-weight="700" fill="#52636a">${label}</text>`;}svg.innerHTML=grid+`<polyline points="${coords}" fill="none" stroke="#087f99" stroke-width="2.5"/>`+timeLabels;}
async function updateFrequency(){const raw=await getJson(API.frequency);const f=flatten(raw);let hz=null;for(const [k,v] of Object.entries(f)){if(/freq|hz|чест/i.test(k)){hz=num(v);if(hz>=45&&hz<=55)break;hz=null;}}if(hz==null)throw Error("Не е намерена честота");$(".frequency b").textContent=fmt(hz,2)+" Hz";}
async function updateIbex(){const raw=await getJson(API.ibex);const now=Date.now()/1000;let i=(raw.unix_seconds||[]).findLastIndex(t=>Number(t)<=now);if(i<0)i=0;const price=num(raw.price?.[i]);if(price==null)throw Error("Няма цена");$(".market b").textContent=fmt(price,2)+" €/MWh";}
async function updateNpp(){const html=await getText(API.npp);const txt=html.replace(/<script\b.*?<\/script>/gis," ").replace(/<style\b.*?<\/style>/gis," ").replace(/<[^>]+>/g," ").replace(/\s+/g," ");const parse=n=>{const m=txt.match(new RegExp("Блок\\s*"+n+"\\s+([0-9][0-9\\s.,]*)\\s*MW","i"));return m?num(m[1]):null;};const a=parse(5),b=parse(6);const cards=document.querySelectorAll(".npp .unit");if(cards[0]){cards[0].querySelector("strong").textContent=a==null?"— MW":fmt(a)+" MW";cards[0].querySelector("small").textContent=a==null?"НЯМА ДАННИ":a>1?"В РАБОТА":"ИЗВЪН РАБОТА";}if(cards[1]){cards[1].querySelector("strong").textContent=b==null?"— MW":fmt(b)+" MW";cards[1].querySelector("small").textContent=b==null?"НЯМА ДАННИ":b>1?"В РАБОТА":"ИЗВЪН РАБОТА";}$(".npp .total strong").textContent=a==null||b==null?"— MW":fmt(a+b)+" MW";}
function render(){renderGauges(state.values);renderProduction(state.values);renderFlows(state.values);}
async function cycle(){
  const errors=[];
  try{
    const response=await fetch("https://raw.githubusercontent.com/BGMIK/energy-monitoring--center/main/data.json?ts="+Date.now(),{cache:"no-store"});
    if(!response.ok)throw new Error("data.json HTTP "+response.status);
    const snapshot=await response.json();
    const v=snapshot.values||{};
    const src=snapshot.sources||{};
    const names=Object.keys(src);
    const ok=names.filter(k=>src[k]&&src[k].ok).length;
    for(const [name,item] of Object.entries(src)){if(!item.ok)errors.push(name+": "+(item.error||"source error"));}
    const updated=Date.parse(snapshot.updated_at||"");
    const age=updated?Math.max(0,(Date.now()-updated)/60000):Infinity;
    if(age>20)errors.push("Данните са остарели ("+Math.round(age)+" мин.)");
    state.values={
      load:num(v.load),
      net:num(v.net),
      bess:v.bess==null?null:-num(v.bess),
      nuclear:num(v.nuclear),
      thermal:num(v.thermal),
      hydro:num(v.hydro),
      renew:num(v.renew),
      "АЕЦ":num(v["АЕЦ"]),
      "Кондензационни ТЕЦ":num(v["Кондензационни ТЕЦ"]),
      "Топлофикационни ТЕЦ":num(v["Топлофикационни ТЕЦ"]),
      "Заводски ТЕЦ":num(v["Заводски ТЕЦ"]),
      "ВЕЦ":num(v["ВЕЦ"]),
      "Малки ВЕЦ":num(v["Малки ВЕЦ"]),
      "ВяЕЦ":num(v["ВяЕЦ"]),
      "ФЕЦ":num(v["ФЕЦ"]),
      "Био ЕЦ":num(v["Био ЕЦ"]),
      "ССЕЕ":v.batt_charge_mw==null&&v.batt_discharge_mw==null?null:num(v.batt_discharge_mw)-num(v.batt_charge_mw),
      "Помпи":num(v.pump_mw),
      SR_mw:v.SR_mw==null?null:-num(v.SR_mw),
      RO_mw:v.RO_mw==null?null:-num(v.RO_mw),
      TR_mw:v.TR_mw==null?null:-num(v.TR_mw),
      MK_mw:v.MK_mw==null?null:-num(v.MK_mw),
      GR_mw:v.GR_mw==null?null:-num(v.GR_mw)
    };
    const pts=(snapshot.series||[]).map(p=>({t:p.t,v:num(p.v)})).filter(p=>p.t&&p.v!=null);
    if(pts.length>=2){state.loadSeries=pts;renderChart(pts);}
    render();
    if(v.frequency!=null)$(".frequency b").textContent=fmt(v.frequency,2)+" Hz";
    if(v.ibex!=null)$(".market b").textContent=fmt(v.ibex,2)+" €/MWh";
    const cards=document.querySelectorAll(".npp .unit");
    for(const n of [5,6]){
      const x=v["block"+n],card=cards[n===5?0:1];
      if(card){card.querySelector("strong").textContent=x==null?"— MW":fmt(x)+" MW";card.querySelector("small").textContent=x==null?"СТАТУС НЕПОТВЪРДЕН":x>1?"В РАБОТА":"ИЗВЪН РАБОТА";}
    }
    const total=document.querySelector(".npp .total strong");
    if(total)total.textContent=v.block5==null||v.block6==null?"— MW":fmt(v.block5+v.block6)+" MW";
    const status=$(".online");
    status.innerHTML=errors.length?'<i style="background:#ffb84d"></i> ЧАСТИЧНИ ДАННИ ('+ok+'/'+names.length+')':'<i></i> LIVE DATA';
    status.title=errors.length?errors.join("\n"):"Всички източници са актуални";
    status.setAttribute("aria-label",status.title);
    $(".meta").textContent="ПОСЛЕДНО ОБНОВЯВАНЕ: "+(updated?new Date(updated).toLocaleTimeString("bg-BG"):"—");
    const chartLabel=document.querySelector(".chart-title small");
    if(chartLabel)chartLabel.textContent=pts.length>=2?"LIVE • "+pts.length+" ТОЧКИ":"НЯМА ДАННИ";
  }catch(e){
    errors.push(e.message);
    const status=$(".online");
    status.innerHTML='<i style="background:#ff525d"></i> НЯМА ВРЪЗКА СЪС СЪРВЪРА';
    status.title=errors.join("\n");
    status.setAttribute("aria-label",status.title);
    $(".meta").textContent="ПОСЛЕДНО ОБНОВЯВАНЕ: —";
  }
}
const tpp2BlockData = [
  {name:"ТЕЦ „Марица Изток 2“ — I блок",mw:170},
  {name:"ТЕЦ „Марица Изток 2“ — II блок",mw:152},
  {name:"ТЕЦ „Марица Изток 2“ — III блок",mw:157},
  {name:"ТЕЦ „Марица Изток 2“ — IV блок",mw:159},
  {name:"ТЕЦ „Марица Изток 2“ — V блок",mw:208},
  {name:"ТЕЦ „Марица Изток 2“ — VI блок",mw:208},
  {name:"ТЕЦ „Марица Изток 2“ — VII блок",mw:212},
  {name:"ТЕЦ „Марица Изток 2“ — VIII блок",mw:222}
];
function renderTpp2Blocks(){
  const chart=$("#tpp2Blocks"),total=$("#tpp2Total");
  if(!chart||!total)return;
  chart.innerHTML=tpp2BlockData.map((b,i)=>{
    const max=i<4?185:240;
    const value=Math.max(0,Math.min(Number(b.mw)||0,max));
    const pct=(value/max)*100;
    const blockRoman=["I","II","III","IV","V","VI","VII","VIII"][i];
    const ticks=[0,25,50,75,100].map(t=>'<span class="tpp2-gridline" style="bottom:'+t+'%"></span>').join("");
    return '<div class="tpp2-bar-col"><div class="tpp2-value">'+fmt(value,0)+' <small>MW</small></div><div class="tpp2-track" role="img" aria-label="'+blockRoman+' блок: '+fmt(value,0)+' от '+max+' MW">'+ticks+'<div class="tpp2-bar" style="height:'+pct+'%"></div></div><div class="tpp2-block">БЛОК '+blockRoman+'</div><div class="tpp2-scale">0–'+max+' MW</div></div>';
  }).join("");
  total.textContent=fmt(tpp2BlockData.reduce((sum,b)=>sum+b.mw,0),2)+" MW";
}
renderTpp2Blocks();
renderGauges();renderProduction();renderFlows();
function tick(){$("#clock").textContent=new Date().toLocaleTimeString("bg-BG",{hour12:false});}tick();setInterval(tick,1000);
document.querySelectorAll(".module").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll(".module").forEach(b=>b.classList.toggle("active",b===btn));document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id===btn.dataset.page));}));
$("#languageBtn").addEventListener("click",()=>alert("Английската версия ще бъде добавена в следващ етап."));
cycle();setInterval(cycle,60000);
