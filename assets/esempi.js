/* Animazioni degli esempi Chat-to-CMS e 3Card: bolle di Chat-to-CMS in sequenza, QR e ingresso della card 3Card. */
(function(){
  var chat=document.getElementById('chatDemo');
  if(chat){
    chat.querySelectorAll('.bubble').forEach(function(b,i){b.style.setProperty('--i',i);});
    if('IntersectionObserver' in window){
      var co=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){chat.classList.add('in');co.disconnect();}});},{threshold:.35});
      co.observe(chat);
    }else chat.classList.add('in');
  }
  var qr=document.getElementById('tcQr');
  if(qr){
    var N=25,on=[];
    var finder=function(x,y){for(var i=0;i<7;i++)for(var j=0;j<7;j++){var e=i===0||i===6||j===0||j===6,c=i>1&&i<5&&j>1&&j<5;if(e||c)on.push([x+i,y+j]);}};
    finder(0,0);finder(N-7,0);finder(0,N-7);
    var seed=7,rnd=function(){return(seed=(seed*16807)%2147483647)/2147483647;};
    var inF=function(x,y){return(x<8&&y<8)||(x>N-9&&y<8)||(x<8&&y>N-9);};
    for(var x=0;x<N;x++)for(var y=0;y<N;y++)if(!inF(x,y)&&rnd()>.52)on.push([x,y]);
    qr.innerHTML=on.map(function(p){return'<rect x="'+p[0]+'" y="'+p[1]+'" width="1" height="1" fill="#111"/>';}).join('');
  }
  var stage=document.querySelector('.tc-stage');
  if(stage){
    if(!('IntersectionObserver' in window)){stage.classList.add('in');return;}
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){stage.classList.add('in');io.disconnect();}});},{threshold:.35});
    io.observe(stage);
  }
})();
