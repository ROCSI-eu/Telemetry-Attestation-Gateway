#!/usr/bin/env node
/** Author-side deterministic TAG social share images (1200x630, bilingual).
 * No npm packages, external assets, user data, real telemetry or network calls.
 * The Cloudflare Pages build copies committed PNG assets; it never runs this tool.
 * Run: node showcase/social_og_builder.mjs
 */
import { mkdirSync, writeFileSync } from "node:fs";
function render(lang){
 const W=1200,H=630,P=[
 [7,21,31],[10,29,39],[15,42,53],[19,58,70],
 [27,78,86],[43,110,121],[59,163,170],
 [103,215,213],[157,245,235],[232,250,248],
 [185,217,218],[74,104,111],[231,154,96],[155,103,74],[18,48,59],[4,14,21]
 ];
 const px=new Uint8Array(W*H);
 const rect=(x,y,w,h,c)=>{for(let j=Math.max(0,y);j<Math.min(H,y+h);j++){let b=j*W;for(let i=Math.max(0,x);i<Math.min(W,x+w);i++)px[b+i]=c}};
 const line=(x0,y0,x1,y1,c,t=1)=>{let dx=x1-x0,dy=y1-y0,n=Math.ceil(Math.max(Math.abs(dx),Math.abs(dy)));for(let i=0;i<=n;i++){let x=Math.round(x0+dx*i/n),y=Math.round(y0+dy*i/n);rect(x-Math.floor(t/2),y-Math.floor(t/2),t,t,c)}};
 const ellipse=(cx,cy,rx,ry,c,fill=false,t=2)=>{if(fill){for(let y=-ry;y<=ry;y++){let span=rx*Math.sqrt(Math.max(0,1-(y*y)/(ry*ry)));rect(Math.round(cx-span),Math.round(cy+y),Math.round(span*2)+1,1,c)}}else{let n=Math.ceil(Math.PI*(rx+ry)*2);for(let i=0;i<n;i++){let a=2*Math.PI*i/n;rect(Math.round(cx+rx*Math.cos(a)),Math.round(cy+ry*Math.sin(a)),t,t,c)}}};
 const poly=(coords,c)=>{let ys=coords.map(q=>q[1]);for(let y=Math.max(0,Math.ceil(Math.min(...ys)));y<=Math.min(H-1,Math.floor(Math.max(...ys)));y++){let ints=[];for(let i=0;i<coords.length;i++){let a=coords[i],b=coords[(i+1)%coords.length];if((a[1]<=y&&b[1]>y)||(b[1]<=y&&a[1]>y))ints.push(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))}ints.sort((a,b)=>a-b);for(let k=0;k+1<ints.length;k+=2)rect(Math.round(ints[k]),y,Math.round(ints[k+1]-ints[k])+1,1,c)}};
 const FONT={
 "A":"01110/10001/10001/11111/10001/10001/10001","B":"11110/10001/10001/11110/10001/10001/11110","C":"01111/10000/10000/10000/10000/10000/01111",
 "D":"11110/10001/10001/10001/10001/10001/11110","E":"11111/10000/10000/11110/10000/10000/11111","F":"11111/10000/10000/11110/10000/10000/10000",
 "G":"01111/10000/10000/10111/10001/10001/01110","H":"10001/10001/10001/11111/10001/10001/10001","I":"11111/00100/00100/00100/00100/00100/11111",
 "J":"00111/00010/00010/00010/10010/10010/01100","K":"10001/10010/10100/11000/10100/10010/10001","L":"10000/10000/10000/10000/10000/10000/11111",
 "M":"10001/11011/10101/10101/10001/10001/10001","N":"10001/11001/10101/10011/10001/10001/10001","O":"01110/10001/10001/10001/10001/10001/01110",
 "P":"11110/10001/10001/11110/10000/10000/10000","Q":"01110/10001/10001/10001/10101/10010/01101","R":"11110/10001/10001/11110/10100/10010/10001",
 "S":"01111/10000/10000/01110/00001/00001/11110","T":"11111/00100/00100/00100/00100/00100/00100","U":"10001/10001/10001/10001/10001/10001/01110",
 "V":"10001/10001/10001/10001/10001/01010/00100","W":"10001/10001/10001/10101/10101/10101/01010","X":"10001/10001/01010/00100/01010/10001/10001",
 "Y":"10001/10001/01010/00100/00100/00100/00100","Z":"11111/00001/00010/00100/01000/10000/11111",
 "0":"01110/10011/10101/10101/11001/10001/01110","1":"00100/01100/00100/00100/00100/00100/01110",
 "2":"01110/10001/00001/00010/00100/01000/11111","3":"11110/00001/00001/00110/00001/00001/11110",
 "4":"00010/00110/01010/10010/11111/00010/00010","5":"11111/10000/11110/00001/00001/10001/01110",
 "6":"00110/01000/10000/11110/10001/10001/01110","7":"11111/00001/00010/00100/01000/01000/01000",
 "8":"01110/10001/10001/01110/10001/10001/01110","9":"01110/10001/10001/01111/00001/00010/11100",
 ".":"00000/00000/00000/00000/00000/01100/01100",":":"00000/01100/01100/00000/01100/01100/00000",
 "/":"00001/00001/00010/00100/01000/10000/10000","-":"00000/00000/00000/11111/00000/00000/00000",
 "|":"00100/00100/00100/00100/00100/00100/00100",
 " ":"00000/00000/00000/00000/00000/00000/00000",
 "·":"00000/00000/01100/01100/00000/00000/00000"
 };
 const textDraw=(s,x,y,scale,c)=>{let xx=x;for(let ch of s.toUpperCase()){let special=({"Ă":"A","Â":"A","Î":"I","Ș":"S","Ş":"S","Ț":"T","Ţ":"T"})[ch],g=FONT[special||ch]||FONT[" "];let rows=g.split("/");for(let k=0;k<7;k++)for(let p=0;p<5;p++)if(rows[k][p]==="1")rect(xx+p*scale,y+k*scale,scale,scale,c);if(special){if(ch==="Ă")line(xx+1*scale,y-scale,xx+3*scale,y-scale,8,Math.max(1,scale/3|0));else if(ch==="Ț"||ch==="Ş"||ch==="Ș"||ch==="Ţ")rect(xx+2*scale,y+7*scale,Math.max(2,scale/2|0),scale/2|0,c);else rect(xx+2*scale,y-scale,scale,Math.max(1,scale/3|0),c)}xx+=6*scale}return xx};
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){let r=Math.hypot((x-960)/1.1,(y-290)/1.1);px[y*W+x]=x<615?(y<102?0:(y>555?15:1)):(r<175?3:r<305?2:r<470?14:0)}
 rect(0,0,W,7,7);rect(0,H-7,W,7);
 for(let x=650;x<=1150;x+=37)line(x,126,x,509,4);
 for(let y=145;y<=508;y+=37)line(650,y,1153,y,3);
 for(let r of [116,190,274])ellipse(933,318,r,r*.68,5,false,2);
 ellipse(934,318,72,48,6,false,2);
 line(634,489,1163,489,5,2);
 const pts=[[678,432],[887,390],[1100,441]];
 for(let i=0;i<pts.length-1;i++){let a=pts[i],b=pts[i+1];line(a[0],a[1],b[0],b[1],5,7);for(let j=0;j<23;j++){let t=j/23;rect(Math.round(a[0]+(b[0]-a[0])*t),Math.round(a[1]+(b[1]-a[1])*t),3,3,8)}}
 for(let i=0;i<pts.length;i++){ellipse(pts[i][0],pts[i][1],11,11,8,true);ellipse(pts[i][0],pts[i][1],5,5,0,true);textDraw("ABC"[i],pts[i][0]-10,pts[i][1]+20,3,9)}
 for(let [cx,cy] of [[785,244],[1007,244],[800,345],[996,345]]){ellipse(cx,cy,48,10,11,true);ellipse(cx,cy,42,7,7,false,2);ellipse(cx,cy,8,8,8,true)}
 poly([[886,266],[789,247],[789,257],[870,291]],5);
 poly([[907,266],[1006,247],[1006,257],[918,291]],5);
 poly([[875,297],[800,345],[811,350],[898,316]],6);
 poly([[917,296],[993,345],[986,355],[898,314]],6);
 poly([[895,252],[927,269],[933,300],[901,326],[867,299],[870,269]],9);
 poly([[895,264],[918,281],[921,299],[900,313],[878,297],[879,278]],6);
 ellipse(899,301,13,13,0,true);ellipse(899,301,6,6,8,true);
 line(899,322,899,388,7,2);
 rect(655,526,497,48,0);rect(655,526,497,2,5);
 for(let [x,n,s] of [[671,"01","DATE"],[830,"02","REGULĂ"],[987,"03","REZULTAT"]]){
 textDraw(n,x,542,3,8);textDraw(lang==="ro"?s:({"DATE":"DATA","REGULĂ":"RULE","REZULTAT":"RESULT"}[s]),x+45,544,2,10)
 }
 rect(72,71,42,42,7);rect(80,79,26,26,0);
 textDraw("TAG",127,83,5,9);
 textDraw("ROCSI",76,140,3,7);
 rect(76,178,470,3,6);
 const ro=lang==="ro";
 textDraw(ro?"VERIFICAREA":"TELEMETRY",75,208,7,9);
 textDraw(ro?"TELEMETRIEI":"ATTESTATION",75,285,7,9);
 textDraw(ro?"CU DIVULGARE MINIMĂ":"WITH LIMITED DISCLOSURE",77,386,3,8);
 rect(76,449,12,12,7);
 textDraw(ro?"SCENARII SINTETICE":"SYNTHETIC SCENARIOS",99,444,3,10);
 textDraw(ro?"FĂRĂ TELEMETRIE LIVE":"NO LIVE TELEMETRY",99,480,3,10);
 rect(76,558,470,1,5);textDraw("TAG.ROCSI.EU",76,578,3,9);
 textDraw("A0_SYNTHETIC",945,585,2,7);
 const raw=new Uint8Array((W/2+1)*H),stride=W/2+1;
 for(let y=0;y<H;y++){let o=y*stride;raw[o]=0;for(let x=0;x<W;x+=2)raw[o+1+(x>>1)]=(px[y*W+x]<<4)|px[y*W+x+1]}
 let a=1,b=0;for(let i=0;i<raw.length;i++){a=(a+raw[i])%65521;b=(b+a)%65521}
 let z=[0x78,0x01];for(let off=0;off<raw.length;){let n=Math.min(65535,raw.length-off),v=(off+n===raw.length)?1:0;z.push(v,n&255,n>>8,(~n)&255,((~n)>>8)&255);for(let i=0;i<n;i++)z.push(raw[off+i]);off+=n}z.push((b>>>8)&255,b&255,(a>>>8)&255,a&255);
 const crc=(data)=>{let v=0xffffffff;for(let j=0;j<data.length;j++){v^=data[j];for(let k=0;k<8;k++)v=(v>>>1)^((v&1)?0xedb88320:0)}return(v^0xffffffff)>>>0};
 const be=(v)=>[(v>>>24)&255,(v>>>16)&255,(v>>>8)&255,v&255];
 const chunk=(name,data)=>{let head=name.split("").map(x=>x.charCodeAt(0));return [...be(data.length),...head,...data,...be(crc([...head,...data]))]};
 let palette=[];for(let rgb of P)palette.push(...rgb);
 return new Uint8Array([137,80,78,71,13,10,26,10,...chunk("IHDR",[...be(W),...be(H),4,3,0,0,0]),...chunk("PLTE",palette),...chunk("IDAT",z),...chunk("IEND",[])]);
}
const folder = new URL("./assets/og/", import.meta.url);
mkdirSync(folder, {recursive:true});
for (const lang of ["ro","en"]) writeFileSync(new URL(lang+".png", folder), render(lang));
