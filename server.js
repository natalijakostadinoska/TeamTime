const http=require('http'),fs=require('fs'),crypto=require('crypto');
const ADMIN=(process.env.ADMIN_KEY||'change-me').trim(),PORT=process.env.PORT||3000;
let db=fs.existsSync('data.json')?JSON.parse(fs.readFileSync('data.json')):{users:{},days:{}};
db.cats??={};db.team??={name:'',pic:''};
const save=()=>fs.writeFileSync('data.json',JSON.stringify(db));
const TZ=process.env.TZ_NAME||'Europe/Skopje',today=()=>new Date().toLocaleDateString('sv-SE',{timeZone:TZ});
const live=(id,date)=>{const u=db.users[id],d=(db.days[date]||{})[id]||{},e=(date===today()&&u.since&&u.status&&u.status!=='out')?Math.round((Date.now()-u.since)/1000):0;return{worked:(d.worked||0)+(u.status==='working'?e:0),brk:(d.brk||0)+(u.status==='break'?e:0)}};
const okPic=x=>typeof x==='string'&&x.length<150000&&/^data:image\/png;base64,[A-Za-z0-9+\/=]+$/.test(x)?x:'';
const me=id=>{const u=db.users[id],d=(db.days[today()]||{})[id]||{};return{name:u.name,pic:u.pic||'',team:db.team,status:u.status||'out',...live(id,today()),stretch:u.status==='working'?Math.round((Date.now()-u.since)/1000):0,active:d.active||0,idle:d.idle||0,apps:d.apps||{}}};
const roll=(id,to,at=Date.now())=>{const u=db.users[id],d=((db.days[today()]??={})[id]??={active:0,idle:0,apps:{}}),e=Math.max(0,Math.round((at-(u.since||at))/1000));
 if(u.status==='working')d.worked=(d.worked||0)+e;else if(u.status==='break')d.brk=(d.brk||0)+e;u.status=to;u.since=at;save()};
const send=(r,c,o)=>{r.writeHead(c,{'Content-Type':'application/json'});r.end(JSON.stringify(o))};
http.createServer((req,res)=>{
 const url=new URL(req.url,'http://x');let body='';
 req.on('data',c=>body+=c);
 req.on('end',()=>{
  let j={};try{j=JSON.parse(body||'{}')}catch{}
  const auth=(req.headers.authorization||'').replace('Bearer ','');
  const user=Object.entries(db.users).find(([,u])=>u.token===auth);
  const p=url.pathname,m=req.method;
  if(m==='GET'&&(p==='/'||p==='/index.html')){res.writeHead(200,{'Content-Type':'text/html'});return res.end(fs.readFileSync(__dirname+'/index.html'))}
  if(p==='/api/track'&&m==='POST'){
   if(!user)return send(res,401,{});
   if(user[1].status!=='working')return send(res,200,{paused:1});
   const d=((db.days[today()]??={})[user[0]]??={active:0,idle:0,apps:{}});
   const s=Math.min(Math.max(+j.secs||0,0),30);
   if(j.idle)d.idle+=s;else{const a=String(j.app||'Unknown').slice(0,60);d.active+=s;d.apps[a]=(d.apps[a]||0)+s}
   d.last=Date.now();save();return send(res,200,{ok:1});
  }
  if(p==='/api/me'&&user){user[1].seen=Date.now();return send(res,200,me(user[0]))}
  if(p==='/api/clock'&&m==='POST'&&user){const to={in:'working',resume:'working',break:'break',out:'out'}[j.action];if(!to)return send(res,400,{});roll(user[0],to);return send(res,200,me(user[0]))}
  if(auth!==ADMIN)return send(res,401,{error:'unauthorized'});
  if(p==='/api/users'&&m==='POST'){const id=crypto.randomUUID().slice(0,8),token=crypto.randomBytes(16).toString('hex');db.users[id]={name:String(j.name||'').slice(0,40),token};save();return send(res,200,{id,token})}
  if(p==='/api/team'&&m==='POST'){if('name' in j)db.team.name=String(j.name).slice(0,60);if('pic' in j)db.team.pic=okPic(j.pic);save();return send(res,200,db.team)}
  if(p.startsWith('/api/users/')&&m==='POST'){const u=db.users[p.split('/').pop()];if(!u)return send(res,404,{});if('name' in j)u.name=String(j.name).slice(0,40);if('pic' in j)u.pic=okPic(j.pic);if(j.regen)u.token=crypto.randomBytes(16).toString('hex');save();return send(res,200,{ok:1})}
  if(p.startsWith('/api/users/')&&m==='DELETE'){delete db.users[p.split('/').pop()];save();return send(res,200,{ok:1})}
  if(p==='/api/cats'&&m==='POST'){const c=['p','u','n'].includes(j.cat)?j.cat:'n';db.cats[String(j.app).slice(0,60)]=c;save();return send(res,200,{ok:1})}
  if(p==='/api/report'){const to=url.searchParams.get('to')||today(),n=Math.min(+url.searchParams.get('days')||7,93),rows=[];
   for(let i=n-1;i>=0;i--){const dt=new Date(to+'T12:00:00Z');dt.setUTCDate(dt.getUTCDate()-i);const date=dt.toISOString().slice(0,10);
    for(const[id,u]of Object.entries(db.users)){const d=(db.days[date]||{})[id];if(!d)continue;let P=0,U=0;for(const[a,v]of Object.entries(d.apps||{})){if(db.cats[a]=='p')P+=v;else if(db.cats[a]=='u')U+=v}
     rows.push({date,name:u.name,worked:d.worked||0,brk:d.brk||0,active:d.active||0,idle:d.idle||0,productive:P,unproductive:U})}}
   return send(res,200,rows)}
  if(p==='/api/stats'){const date=url.searchParams.get('date')||today();
   return send(res,200,{cats:db.cats,team:db.team,users:Object.entries(db.users).map(([id,u])=>({id,name:u.name,pic:u.pic||'',token:u.token,active:0,idle:0,apps:{},...((db.days[date]||{})[id]||{}),status:u.status||'out',...live(id,date)}))})}
  send(res,404,{});
 });
}).listen(PORT,()=>console.log('TeamTime running on http://localhost:'+PORT));

// auto clock-out when an agent goes silent, and delete old data
const AUTO=(+process.env.AUTO_OUT_MIN||15)*60000,KEEP=+process.env.KEEP_DAYS||90;
setInterval(()=>{const now=Date.now();for(const[id,u]of Object.entries(db.users))if(u.status&&u.status!=='out'&&now-(u.seen||u.since||now)>AUTO)roll(id,'out',u.seen||u.since);
 const cut=new Date(now-KEEP*864e5).toLocaleDateString('sv-SE',{timeZone:TZ});let ch=0;for(const d of Object.keys(db.days))if(d<cut){delete db.days[d];ch=1}if(ch)save()},60000);