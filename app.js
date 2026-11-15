const API = {
  generation: "https://www.eso.bg/api/rabota_na_EEC_json.php",
  flows: "https://www.eso.bg/api/scada_live_json_pure.php",
  frequency: "https://www.eso.bg/api/freq.json.php",
  load: "https://raw.githubusercontent.com/yyoncho/eso-dashboard/data/data/today.jsonl",
  ibex: "https://api.energy-charts.info/price?bzn=BG",
  npp: "https://www.kznpp.org/bg/proizvodstvo/danni-za-elektroproizvodstvoto"
};

const translations={"ЕЛЕКТРОЕНЕРГИЙНА СИСТЕМА НА БЪЛГАРИЯ":"BULGARIAN POWER SYSTEM","ЗАРЕЖДАНЕ НА ОПЕРАТИВНИ ДАННИ":"LOADING OPERATIONAL DATA","ЧЕСТОТА:":"FREQUENCY:","Смяна на езика":"Change language","ЛИЧНИ УСТРОЙСТВА":"PERSONAL DEVICES","Енергиен хъб":"Energy Hub","ПРОИЗВОДСТВО ПО ЦЕНТРАЛИ / ИЗТОЧНИЦИ":"GENERATION BY PLANT / SOURCE","ТОВАР — ЕСО":"SYSTEM LOAD — ESO","РЕАЛИЗИРАН ТОВАР — ЕСО":"ACTUAL SYSTEM LOAD — ESO","ИЗЧАКВАНЕ НА ДАННИ ОТ ЕСО":"WAITING FOR ESO DATA","Графика на товара от ЕСО":"ESO system load chart","ТРАНСГРАНИЧНИ ПОТОЦИ (MW)":"CROSS-BORDER FLOWS (MW)","ТРАНСГРАНИЧНИ ПОТОЦИ":"CROSS-BORDER FLOWS","ТЕЦ „МАРИЦА ИЗТОК 2“ — ПРОИЗВОДСТВО ПО БЛОКОВЕ":"MARITSA EAST 2 TPP — UNIT GENERATION","Вертикални колонки с индивидуална скала: I–IV блок 0–185 MW · V–VIII блок 0–240 MW.":"Vertical bars with individual scales: Units I–IV 0–185 MW · Units V–VIII 0–240 MW.","ОБЩО ПРОИЗВОДСТВО":"TOTAL GENERATION","ЦЕНА НА ЕМИСИОННИТЕ ПРАВА CO₂ (EUA)":"CO₂ EMISSION ALLOWANCE PRICE (EUA)","Последна налична котировка:":"Last available quote:","Източник: oEnergetice · Борсова цена EUA":"Source: oEnergetice · EUA market price","България · Европа · Свят":"Bulgaria · Europe · World","Централизирано табло за новини от избрани надеждни източници в България, Европа и света.":"Centralized news dashboard from selected reliable sources in Bulgaria, Europe and worldwide.","МОДУЛЪТ Е ПРЕДВИДЕН · НЯМА ЗАРЕДЕНИ НОВИНИ":"MODULE PLANNED · NO NEWS LOADED","Метеорология · Планински камери · България · Малта":"Weather · Mountain Cameras · Bulgaria · Malta","ПРОГНОЗА ЗА ВРЕМЕТО — БЪЛГАРИЯ":"WEATHER FORECAST — BULGARIA","Текущи условия, почасова прогноза за следващите 12 часа и прогноза за 7 дни. Източник: Open-Meteo.":"Current conditions, hourly forecast for the next 12 hours and a 7-day forecast. Source: Open-Meteo.","СОФИЯ":"SOFIA","ДЖУЛЮНИЦА":"DZHULYUNITSA","ЗАРЕЖДАНЕ…":"LOADING…","Очакване на данни":"Waiting for data","Усеща се":"Feels like","Влажност":"Humidity","Вятър":"Wind","Автоматично обновяване на всеки 15 минути · Часова зона: Europe/Sofia":"Automatic refresh every 15 minutes · Time zone: Europe/Sofia","⛰️ ПЛАНИНСКИ КАМЕРИ":"⛰️ MOUNTAIN WEBCAMS","Три камери в планинския мониторинг. Двоен клик върху изображение отваря изглед на цял екран; ESC или двоен клик затваря.":"Three mountain monitoring cameras. Double-click an image to open full screen; press ESC or double-click to close.","РИЛА · БОРОВЕЦ":"RILA · BOROVETS","Маркуджик 1 · 2345 m":"Markudjik 1 · 2345 m","СТАРА ПЛАНИНА":"BALKAN MOUNTAINS","Заслон Ботев · 2056 m":"Botev Shelter · 2056 m","РОДОПИ":"RHODOPE MOUNTAINS","Пампорово – Студенец · ≈1650 m":"Pamporovo – Studenets · ≈1650 m","ВИТОША":"VITOSHA","Алеко · 1840 m":"Aleko · 1840 m","● LIVE VIDEO":"● LIVE VIDEO","● CONNECTING":"● CONNECTING","LIVE SNAPSHOT · ОБНОВЯВАНЕ 3 СЕК.":"LIVE SNAPSHOT · REFRESH EVERY 3 SEC.","ESC / ЗАТВОРИ ✕":"ESC / CLOSE ✕","Планинска камера":"Mountain webcam","Снимковите потоци се обновяват през 3 секунди. Видеоизлъчването е от YouTube.":"Image feeds refresh every 3 seconds. Video stream provided by YouTube.","Управление и мониторинг на лични устройства":"Personal device management and monitoring","Тук ще бъдат събрани личните устройства, сензори и системи за наблюдение.":"Personal devices, sensors and monitoring systems will be collected here.","МОДУЛЪТ Е ГОТОВ ЗА ДОБАВЯНЕ НА УСТРОЙСТВА":"MODULE READY FOR DEVICE INTEGRATION","ЛИЧЕН ИНФОРМАЦИОНЕН ЦЕНТЪР":"PERSONAL INFORMATION CENTER","ДЕМО ИНТЕРФЕЙС · НЕ Е ЗА ОПЕРАТИВНИ РЕШЕНИЯ":"DEMO INTERFACE · NOT FOR OPERATIONAL DECISIONS","ТОВАР НА РБ":"BULGARIAN SYSTEM LOAD","ВНОС / ИЗНОС":"IMPORT / EXPORT","ССЕЕ + ПОМПИ":"BESS + PUMPED STORAGE","АЕЦ":"NUCLEAR","ТЕЦ":"THERMAL","ВЕЦ + МАЛКИ ВЕЦ":"HYDRO + SMALL HYDRO","ВЕИ":"RENEWABLES","АЕЦ Козлодуй":"Kozloduy NPP","Кондензационни ТЕЦ":"Condensing thermal plants","Топлофикационни ТЕЦ":"District heating plants","Заводски ТЕЦ":"Industrial power plants","ВЕЦ":"Hydro plants","Малки ВЕЦ":"Small hydro plants","ВяЕЦ":"Wind farms","ФЕЦ":"Solar PV","Био ЕЦ":"Biomass plants","ССЕЕ":"BESS","Помпи ПАВЕЦ":"Pumped-storage pumping","Сърбия":"Serbia","Румъния":"Romania","Турция":"Türkiye","С. Македония":"North Macedonia","Гърция":"Greece","БЛОК 5":"UNIT 5","БЛОК 6":"UNIT 6","ОБЩО АЕЦ КОЗЛОДУЙ":"KOZLODUY NPP TOTAL","СТАТУС НЕПОТВЪРДЕН":"STATUS UNCONFIRMED","Източникът за данните на блокове 5 и 6 предстои да бъде свързан.":"The data source for Units 5 and 6 is pending integration.","В РАБОТА":"IN SERVICE","ИЗВЪН РАБОТА":"OUT OF SERVICE","НЯМА ДАННИ":"NO DATA","Ясно":"Clear","Предимно ясно":"Mainly clear","Променлива облачност":"Partly cloudy","Облачно":"Cloudy","Мъгла":"Fog","Ръмеж":"Drizzle","Дъжд":"Rain","Сняг":"Snow","Краткотрайни превалявания":"Rain showers","Снежни превалявания":"Snow showers","Гръмотевична буря":"Thunderstorm","Променливо":"Variable","ПОЧАСОВО — СЛЕДВАЩИТЕ 12 ЧАСА":"HOURLY — NEXT 12 HOURS","дъжд":"rain","ОБНОВЕНО":"UPDATED","ДАННИТЕ СА ОСТАРЕЛИ":"DATA IS OUTDATED","ЧАСТИЧНИ ДАННИ":"PARTIAL DATA","НЯМА ВРЪЗКА СЪС СЪРВЪРА":"SERVER CONNECTION LOST"};
let currentLanguage="bg";
const originalTextNodes=new WeakMap();
const originalAttributes=new WeakMap();
function applyLanguage(){
  const english=currentLanguage==="en";
  document.documentElement.lang=english?"en":"bg";
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    if(!originalTextNodes.has(node))originalTextNodes.set(node,node.nodeValue);
    const original=originalTextNodes.get(node),trimmed=original.trim();
    if(!trimmed)continue;
    const translated=translations[trimmed];
    if(english&&translated)node.nodeValue=original.replace(trimmed,translated);
    else node.nodeValue=original;
  }
  document.querySelectorAll("[aria-label],[title]").forEach(el=>{
    for(const attr of ["aria-label","title"]){
      if(!el.hasAttribute(attr))continue;
      const key=el.tagName+":"+attr;
      let store=originalAttributes.get(el);if(!store){store={};originalAttributes.set(el,store);}
      if(store[attr]===undefined)store[attr]=el.getAttribute(attr);
      const original=store[attr];el.setAttribute(attr,english?(translations[original]||original):original);
    }
  });
  const button=document.getElementById("languageBtn");
  if(button){button.textContent=english?"БЪЛГАРСКИ":"ENGLISH";button.setAttribute("aria-label",english?"Switch to Bulgarian":"Switch to English");}
}

const $ = s => document.querySelector(s);
const fmt = (n,d=0) => Number(n).toLocaleString("bg-BG",{maximumFractionDigits:d,minimumFractionDigits:d});
const state = {lastUpdated:null, loadSeries:[], values:{}};
const gaugeDefs = [
  {key:"load",label:"ТОВАР НА РБ",min:0,max:10000,marks:["0","2k","4k","6k","8k","10k"]},
  {key:"net",label:"ВНОС / ИЗНОС",min:-4000,max:4000,marks:["-4k","-3.5k","-3k","-2.5k","-2k","-1.5k","-1k","-0.5k","0","0.5k","1k","1.5k","2k","2.5k","3k","3.5k","4k"]},
  {key:"bess",label:"ССЕЕ + ПОМПИ",min:-5000,max:5000,marks:["-5k","-4.5k","-4k","-3.5k","-3k","-2.5k","-2k","-1.5k","-1k","-0.5k","0","0.5k","1k","1.5k","2k","2.5k","3k","3.5k","4k","4.5k","5k"]},
  {key:"nuclear",label:"АЕЦ",min:0,max:2500,marks:["0","0.5k","1k","1.5k","2k","2.5k"]},
  {key:"thermal",label:"ТЕЦ",min:0,max:4000,marks:["0","0.5k","1k","1.5k","2k","2.5k","3k","3.5k","4k"]},
  {key:"hydro",label:"ВЕЦ + МАЛКИ ВЕЦ",min:0,max:3000,marks:["0","0.5k","1k","1.5k","2k","2.5k","3k"]},
  {key:"renew",label:"ВЕИ",min:0,max:10000,marks:["0","2k","4k","6k","8k","10k"]}
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
  const labelStride=Math.max(1,Math.ceil((g.marks.length-1)/8));
  const labels=g.marks.map((m,i)=>{
    if(i!==0&&i!==g.marks.length-1&&i%labelStride!==0)return "";
    const a=(150+(i/(g.marks.length-1))*240)*Math.PI/180;
    return `<text x="${cx+Math.cos(a)*49}" y="${cy+Math.sin(a)*49+3}" text-anchor="middle" font-size="12" font-weight="800" fill="#263b43">${m}</text>`;
  }).join("");
  let needle="";
  if(valid){
    const ratio=Math.max(0,Math.min(1,(Number(v)-g.min)/(g.max-g.min)));
    const a=(150+ratio*240)*Math.PI/180;
    const tipX=cx+Math.cos(a)*75,tipY=cy+Math.sin(a)*75;
    const tailX=cx-Math.cos(a)*7,tailY=cy-Math.sin(a)*7;
    needle=`<line x1="${tailX}" y1="${tailY}" x2="${tipX}" y2="${tipY}" stroke="#5b252a" stroke-width="3.2" stroke-linecap="round"/><line x1="${tailX}" y1="${tailY}" x2="${tipX}" y2="${tipY}" stroke="#e32636" stroke-width="1.8" stroke-linecap="round"/>`;
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
async function updateFrequency(){
  const end=Math.floor(Date.now()/1000),start=end-180;
  const url="https://api.energy-charts.info/v2/frequency?region=DE-Freiburg&start="+start+"&end="+end;
  const raw=await getJson(url);
  let hz=null,stamp=null;
  if(Array.isArray(raw.data)){
    for(let i=raw.data.length-1;i>=0;i--){
      const point=raw.data[i],values=point.values||{};
      const candidates=Object.values(values).map(num).filter(v=>v!=null&&v>=45&&v<=55);
      if(candidates.length){hz=candidates[0];stamp=point.timestamp||null;break;}
    }
  }
  if(hz==null&&Array.isArray(raw.data)&&Array.isArray(raw.unix_seconds)){
    for(let i=raw.data.length-1;i>=0;i--){const v=num(raw.data[i]);if(v!=null&&v>=45&&v<=55){hz=v;stamp=raw.unix_seconds[i]*1000;break;}}
  }
  if(hz==null)throw Error("Не е намерена актуална честота в Energy-Charts");
  $(".frequency b").textContent=fmt(hz,4)+" Hz";
  $(".frequency").title="Continental Europe · Fraunhofer ISE, Freiburg · измерване: "+(stamp?new Date(stamp).toLocaleTimeString("bg-BG"):"последна налична точка")+" · Energy-Charts";
}
async function updateIbex(){const raw=await getJson(API.ibex);const now=Date.now()/1000;let i=(raw.unix_seconds||[]).findLastIndex(t=>Number(t)<=now);if(i<0)i=0;const price=num(raw.price?.[i]);if(price==null)throw Error("Няма цена");$(".market b").textContent=fmt(price,2)+" €/MWh";}
async function updateNpp(){const html=await getText(API.npp);const txt=html.replace(/<script\b.*?<\/script>/gis," ").replace(/<style\b.*?<\/style>/gis," ").replace(/<[^>]+>/g," ").replace(/\s+/g," ");const parse=n=>{const m=txt.match(new RegExp("Блок\\s*"+n+"\\s+([0-9][0-9\\s.,]*)\\s*MW","i"));return m?num(m[1]):null;};const a=parse(5),b=parse(6);const cards=document.querySelectorAll(".npp .unit");if(cards[0]){cards[0].querySelector("strong").textContent=a==null?"— MW":fmt(a)+" MW";cards[0].querySelector("small").textContent=a==null?"НЯМА ДАННИ":a>1?"В РАБОТА":"ИЗВЪН РАБОТА";}if(cards[1]){cards[1].querySelector("strong").textContent=b==null?"— MW":fmt(b)+" MW";cards[1].querySelector("small").textContent=b==null?"НЯМА ДАННИ":b>1?"В РАБОТА":"ИЗВЪН РАБОТА";}$(".npp .total strong").textContent=a==null||b==null?"— MW":fmt(a+b)+" MW";}
function render(){renderGauges(state.values);renderProduction(state.values);renderFlows(state.values);applyLanguage();}
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
    if(v.frequency!=null)$(".frequency b").textContent=fmt(v.frequency,4)+" Hz";
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
renderGauges();renderProduction();renderFlows();applyLanguage();
function tick(){$("#clock").textContent=new Date().toLocaleTimeString("bg-BG",{hour12:false});}tick();setInterval(tick,1000);
document.querySelectorAll(".module").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll(".module").forEach(b=>b.classList.toggle("active",b===btn));document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id===btn.dataset.page));}));
$("#languageBtn").addEventListener("click",()=>{currentLanguage=currentLanguage==="bg"?"en":"bg";applyLanguage();});
cycle();setInterval(cycle,60000);
updateFrequency().catch(e=>{document.querySelector(".frequency").title="Energy-Charts: "+e.message;});
setInterval(()=>updateFrequency().catch(e=>{document.querySelector(".frequency").title="Energy-Charts: "+e.message;}),30000);

const additionalThermalUnits = {
  cg3: [
    {name:"I",mw:null},{name:"II",mw:null},{name:"III",mw:null},{name:"IV",mw:null}
  ],
  bobovDol: [
    {name:"I",mw:null},{name:"II",mw:null},{name:"III",mw:null}
  ]
};
function renderThermalUnitBars(chartId,totalId,units){
  const chart=$("#"+chartId),total=$("#"+totalId);
  if(!chart||!total)return;
  const max=240;
  chart.innerHTML=units.map(unit=>{
    const valid=Number.isFinite(unit.mw);
    const value=valid?Math.max(0,Math.min(unit.mw,max)):0;
    const pct=(value/max)*100;
    const ticks=[0,25,50,75,100].map(t=>'<span class="tpp2-gridline" style="bottom:'+t+'%"></span>').join("");
    return '<div class="tpp2-bar-col"><div class="tpp2-value">'+(valid?fmt(value,0)+' <small>MW</small>':'— <small>MW</small>')+'</div><div class="tpp2-track" role="img" aria-label="Блок '+unit.name+': '+(valid?fmt(value,0):'няма данни')+' от 240 MW">'+ticks+(valid?'<div class="tpp2-bar" style="height:'+pct+'%"></div>':'')+'</div><div class="tpp2-block">БЛОК '+unit.name+'</div><div class="tpp2-scale">0–240 MW</div></div>';
  }).join("");
  const measured=units.filter(unit=>Number.isFinite(unit.mw));
  total.textContent=measured.length?fmt(measured.reduce((sum,unit)=>sum+unit.mw,0),2)+" MW":"НЯМА ДАННИ";
}
renderThermalUnitBars("cg3Blocks","cg3Total",additionalThermalUnits.cg3);
renderThermalUnitBars("bobovDolBlocks","bobovDolTotal",additionalThermalUnits.bobovDol);

/* Weather forecast for Sofia and Dzhulyunitsa — Open-Meteo, no API key */
const weatherPlaces=[
  {id:"weather-sofia",lat:42.6977,lon:23.3219},
  {id:"weather-dzhulyunitsa",lat:43.13668,lon:25.90033}
];
function weatherDescription(code){
  if(code===0)return ["☀️","Ясно"];
  if(code===1)return ["🌤️","Предимно ясно"];
  if(code===2)return ["⛅","Променлива облачност"];
  if(code===3)return ["☁️","Облачно"];
  if([45,48].includes(code))return ["🌫️","Мъгла"];
  if([51,53,55,56,57].includes(code))return ["🌦️","Ръмеж"];
  if([61,63,65,66,67].includes(code))return ["🌧️","Дъжд"];
  if([71,73,75,77].includes(code))return ["🌨️","Сняг"];
  if([80,81,82].includes(code))return ["🌧️","Краткотрайни превалявания"];
  if([85,86].includes(code))return ["🌨️","Снежни превалявания"];
  if([95,96,99].includes(code))return ["⛈️","Гръмотевична буря"];
  return ["🌡️","Променливо"];
}
function weatherTime(value,options){
  return new Intl.DateTimeFormat("bg-BG",{timeZone:"Europe/Sofia",...options}).format(new Date(value));
}
async function loadWeather(place){
  const card=document.getElementById(place.id);
  if(!card)return;
  try{
    const url="https://api.open-meteo.com/v1/forecast?latitude="+place.lat+"&longitude="+place.lon+"&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&forecast_days=7&timezone=Europe%2FSofia";
    const response=await fetch(url,{cache:"no-store"});
    if(!response.ok)throw new Error("HTTP "+response.status);
    const data=await response.json(),cur=data.current;
    const [icon,bgDesc]=weatherDescription(cur.weather_code);const desc=currentLanguage==="en"?(translations[bgDesc]||bgDesc):bgDesc;
    card.querySelector(".weather-icon").textContent=icon;
    card.querySelector(".weather-temp").textContent=Math.round(cur.temperature_2m)+"°C";
    card.querySelector(".weather-description").textContent=desc;
    card.querySelector(".weather-feels").textContent=Math.round(cur.apparent_temperature)+"°C";
    card.querySelector(".weather-humidity").textContent=cur.relative_humidity_2m+"%";
    card.querySelector(".weather-wind").textContent=Math.round(cur.wind_speed_10m)+" km/h";
    card.querySelector(".weather-updated").textContent=(currentLanguage==="en"?"UPDATED ":"ОБНОВЕНО ")+weatherTime(cur.time,{hour:"2-digit",minute:"2-digit"});
    const now=new Date(cur.time).getTime();
    const hours=data.hourly.time.map((t,i)=>({t,v:data.hourly.temperature_2m[i],p:data.hourly.precipitation_probability[i],w:data.hourly.weather_code[i]})).filter(x=>new Date(x.t).getTime()>=now).slice(0,12);
    card.querySelector(".weather-hourly").innerHTML='<h4>'+(currentLanguage==="en"?"HOURLY — NEXT 12 HOURS":"ПОЧАСОВО — СЛЕДВАЩИТЕ 12 ЧАСА")+'</h4><div class="weather-hour-row">'+hours.map(x=>{const wi=weatherDescription(x.w);const wd=currentLanguage==="en"?(translations[wi[1]]||wi[1]):wi[1];return '<div><span>'+weatherTime(x.t,{hour:"2-digit",minute:"2-digit"})+'</span><b>'+wi[0]+' '+Math.round(x.v)+'°</b><small>'+Math.round(x.p||0)+'% '+(currentLanguage==="en"?"rain":"дъжд")+'</small></div>';}).join("")+'</div>';
    card.querySelector(".weather-daily").innerHTML='<h4>'+(currentLanguage==="en"?"7-DAY FORECAST":"ПРОГНОЗА — 7 ДНИ")+'</h4><div class="weather-day-list">'+data.daily.time.map((t,i)=>{const wi=weatherDescription(data.daily.weather_code[i]);const wd=currentLanguage==="en"?(translations[wi[1]]||wi[1]):wi[1];return '<div><span>'+weatherTime(t+"T12:00",{weekday:"short",day:"2-digit",month:"2-digit"})+'</span><b>'+wi[0]+' '+Math.round(data.daily.temperature_2m_max[i])+'° / '+Math.round(data.daily.temperature_2m_min[i])+'°</b><small>'+Math.round(data.daily.precipitation_probability_max[i]||0)+'% '+(currentLanguage==="en"?"rain":"дъжд")+'</small></div>';}).join("")+'</div>';
  }catch(error){
    card.querySelector(".weather-updated").textContent=currentLanguage==="en"?"NO CONNECTION":"НЯМА ВРЪЗКА";
    card.querySelector(".weather-description").textContent=currentLanguage==="en"?"Forecast could not be loaded.":"Прогнозата не може да бъде заредена.";
    console.error("Weather load failed:",place.id,error);
  }
}
function refreshWeather(){weatherPlaces.forEach(loadWeather);}
refreshWeather();
setInterval(refreshWeather,15*60*1000);

/* Mountain cameras integrated into Weather Center */
function refreshMountainCamera(id,url,statusId){
  const img=document.getElementById(id),status=document.getElementById(statusId);
  if(!img)return;
  img.onload=()=>{if(status){status.textContent="● ONLINE";status.style.color="#21e38a";}};
  img.onerror=()=>{if(status){status.textContent="● NO FRAME";status.style.color="#ff5d63";}};
  // Pladi camera rejects cache-busting query parameters; use its exact image URL.
  if(id==="mountain-botev"){
    if(img.dataset.source!==url){img.dataset.source=url;img.src=url;}
    return;
  }
  img.src=url+(url.includes("?")?"&":"?")+"_="+Date.now();
}
function refreshMountainCameras(){
  refreshMountainCamera("mountain-botev","https://cams.pladi.bg/zaslon.jpg","mountain-botev-status");
  refreshMountainCamera("mountain-pamporovo","https://webcams.pamporovo.me/memfs/54d2de25-1031-438f-9088-ea70df4702a1.jpg","mountain-pamporovo-status");
  refreshMountainCamera("mountain-aleko","https://vod132.witmind.com/hls/cam1.jpg","mountain-aleko-status");
}
function mountainFullscreen(type,id){
  const box=document.getElementById("mountain-camera-fullscreen");
  const img=document.getElementById("mountain-fs-image");
  const frame=document.getElementById("mountain-fs-frame");
  img.hidden=true;frame.hidden=true;img.src="";frame.src="";
  const original=document.getElementById(id);
  if(type==="image"){img.src=original.src;img.hidden=false;}
  else{frame.src=original.src;frame.hidden=false;}
  box.classList.add("on");
}
function closeMountainFullscreen(){
  const box=document.getElementById("mountain-camera-fullscreen");
  box.classList.remove("on");
  document.getElementById("mountain-fs-image").src="";
  document.getElementById("mountain-fs-frame").src="";
}
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeMountainFullscreen();});
refreshMountainCameras();
setInterval(refreshMountainCameras,3000);
setTimeout(()=>{try{document.getElementById("mountain-maly").contentWindow.postMessage(JSON.stringify({event:"command",func:"playVideo",args:""}),"*");}catch(e){}},2500);
