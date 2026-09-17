(function(){
  var f=document.getElementById('f');if(!f)return;
  var steps=[].slice.call(f.querySelectorAll('.fs')),bars=[].slice.call(f.querySelectorAll('.prog i')),cur=0;
  function show(i){cur=i;steps.forEach(function(s,j){s.classList.toggle('on',j===i)});bars.forEach(function(b,j){b.classList.toggle('on',j<=i)});}
  function valid(i){var ok=true;steps[i].querySelectorAll('[required]').forEach(function(el){var v=el.value.trim();var bad=!v||(el.type==='email'&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v));el.style.borderColor=bad?'#f87171':'';if(bad)ok=false;});return ok;}
  f.addEventListener('click',function(e){
    if(e.target.hasAttribute('data-next')){if(valid(cur))show(cur+1);}
    if(e.target.hasAttribute('data-back'))show(cur-1);
  });
  f.addEventListener('submit',function(e){
    e.preventDefault();if(!valid(cur))return;
    var d={};['name','email','company','project','source'].forEach(function(k){d[k]=f.querySelector('[name='+k+']').value.trim()});
    var body='Name: '+d.name+'\nEmail: '+d.email+'\nCompany / location: '+d.company+'\nSource: '+d.source+'\n\nDetails:\n'+d.project;
    window.location.href='mailto:hello@realset.ai?subject='+encodeURIComponent(f.getAttribute('data-subject')+' — '+d.company)+'&body='+encodeURIComponent(body);
    steps.forEach(function(s){s.classList.remove('on')});f.querySelector('.prog').style.display='none';f.querySelector('.done').classList.add('on');
  });
})();

document.addEventListener('click',function(e){var b=e.target.closest('[data-reveal]');if(!b)return;var t=document.getElementById(b.getAttribute('data-reveal'));if(t){t.hidden=false;b.hidden=true;}});
