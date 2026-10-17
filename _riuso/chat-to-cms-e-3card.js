/* Il blocco bubbles stava dentro gsap.matchMedia(...) e usa la variabile `reduced`; il blocco 3Card e' una IIFE a se'. */
  /* ---- Chat-to-CMS bubbles appear in sequence ---- */
  const bubbles=gsap.utils.toArray('#chatDemo .bubble');
  if(bubbles.length){
    if(reduced){ gsap.set(bubbles,{opacity:1,y:0}); }
    else{
      gsap.set(bubbles,{opacity:0,y:14});
      ScrollTrigger.create({trigger:'#chatDemo',start:'top 80%',once:true,onEnter:()=>{
        gsap.to(bubbles,{opacity:1,y:0,duration:.45,ease:'power2.out',stagger:0.6});
      }});
    }
  }

/* ---- 3Card: QR decorativo + animazione all'ingresso ---- */
(function(){
  const qr=document.getElementById('tcQr');
  if(qr){
    const N=25, on=[];
    const finder=(x,y)=>{ for(let i=0;i<7;i++)for(let j=0;j<7;j++){ const e=i===0||i===6||j===0||j===6, c=i>1&&i<5&&j>1&&j<5; if(e||c) on.push([x+i,y+j]); } };
    finder(0,0); finder(N-7,0); finder(0,N-7);
    let seed=7;
    const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
    const inFinder=(x,y)=>(x<8&&y<8)||(x>N-9&&y<8)||(x<8&&y>N-9);
    for(let x=0;x<N;x++)for(let y=0;y<N;y++) if(!inFinder(x,y)&&rnd()>.52) on.push([x,y]);
    qr.innerHTML=on.map(([x,y])=>'<rect x="'+x+'" y="'+y+'" width="1" height="1" fill="#111"/>').join('');
  }
  const stage=document.querySelector('.tc-stage');
  if(!stage) return;
  if(!('IntersectionObserver' in window)){ stage.classList.add('in'); return; }
  const io=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ stage.classList.add('in'); io.disconnect(); } }),{threshold:.35});
  io.observe(stage);
})();
