'use strict';
(() => {
 const group=document.querySelector('.rail-group');
 if(!group)return;
 const toggle=group.querySelector('.rail-group-toggle');
 const submenu=group.querySelector('.rail-submenu');
 const links=[...submenu.querySelectorAll('a')];
 const setOpen=open=>{toggle.setAttribute('aria-expanded',String(open));submenu.hidden=!open;};
 toggle.addEventListener('click',()=>setOpen(toggle.getAttribute('aria-expanded')!=='true'));
 toggle.addEventListener('keydown',event=>{if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();setOpen(true);(event.key==='ArrowDown'?links[0]:links[links.length-1]).focus();}});
 document.addEventListener('click',event=>{if(!group.contains(event.target))setOpen(false);});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setOpen(false);toggle.focus();}});
})();
