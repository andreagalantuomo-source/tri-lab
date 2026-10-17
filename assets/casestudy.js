/* Case study: flusso animato di OrientaCampus (iniettato in [data-flow]) e tab della home */
(function(){
  var node=function(x,y,w,h,t,s,cls){return '<g class="n '+(cls||'')+'"><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="14"/><text class="t" x="'+(x+16)+'" y="'+(y+h/2-3)+'">'+t+'</text><text class="s" x="'+(x+16)+'" y="'+(y+h/2+16)+'">'+s+'</text></g>';};
  var svg='<svg viewBox="0 0 900 380" role="img" aria-label="Flusso di lavoro: il ticket in entrata arriva all\'agente AI centrale. Se la richiesta è ripetitiva risponde con le informazioni del company brain, se è straordinaria la smista al responsabile tecnico di riferimento.">'+
    '<path class="ln" d="M200,190 H270"/><path class="ln" d="M460,190 C505,190 505,70 540,70"/><path class="ln" d="M460,190 C505,190 505,315 540,315"/><path class="ln" d="M710,70 H750"/>'+
    node(30,155,170,70,'Ticket in entrata','email · chat · modulo')+
    node(270,140,190,100,'Agente AI centrale','capisce la richiesta','core')+
    '<text class="pill" x="540" y="22" fill="#067a41">RICHIESTA RIPETITIVA</text>'+node(540,30,170,80,'Company brain','attinge a tutte le info')+
    node(750,30,130,80,'Risposta','al cliente subito')+
    '<text class="pill" x="540" y="262" fill="#ff3b30">RICHIESTA STRAORDINARIA</text>'+node(540,270,200,90,'Responsabile tecnico','smistata a chi è di competenza')+
    '<circle class="dot d1" r="7"/><circle class="dot d2" r="7"/></svg>';
  document.querySelectorAll('[data-flow]').forEach(function(el){el.innerHTML=svg;});
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce)document.querySelectorAll('.cs-frame video').forEach(function(v){v.removeAttribute('autoplay');v.pause();});
  document.querySelectorAll('[data-cs-tabs]').forEach(function(box){
    var tabs=[].slice.call(box.querySelectorAll('[role=tab]')),panels=[].slice.call(box.parentNode.querySelectorAll('[data-cs-panel]'));
    tabs.forEach(function(t){t.addEventListener('click',function(){
      tabs.forEach(function(x){x.setAttribute('aria-selected',x===t);});
      panels.forEach(function(p){var on=p.id===t.getAttribute('aria-controls');p.hidden=!on;var v=p.querySelector('video');if(v){on&&!reduce?v.play():v.pause();}});
    });});
  });
})();
