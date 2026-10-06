"use strict";
const cameraGrid=document.getElementById('camera-grid'),cameraSelect=document.getElementById('camera-selection'),cameraNotice=document.getElementById('camera-notice');
const cameraPlayers=new Map();let cameraBusy=false;
function cameraIds(){return cameraSelect.value==='all'?[1,2,3,4,5,6]:[Number(cameraSelect.value)];}
for(let id=1;id<=6;id++){
 const card=document.createElement('article');card.className='camera-card';card.dataset.camera=id;
 card.innerHTML=`<div class="camera-video"><video muted playsinline controls preload="none" aria-label="Camera ${id} live video"></video></div><header><h2>Camera ${id}</h2><button class="camera-button" type="button">Enlarge</button></header><p class="camera-state" role="status">Connecting…</p>`;
 card.querySelector('button').addEventListener('click',()=>{cameraSelect.value=String(id);selectCameras();});cameraGrid.append(card);
}
function cameraStatus(id,text){document.querySelector(`[data-camera="${id}"] .camera-state`).textContent=text;}
function stopCamera(id){const p=cameraPlayers.get(id);if(!p)return;p.video.onerror=null;p.video.onwaiting=null;p.video.onplaying=null;p.hls?.destroy();p.video.pause();p.video.removeAttribute('src');p.video.load();cameraPlayers.delete(id);}
function startCamera(item){
 if(cameraPlayers.has(item.id))return;
 const video=document.querySelector(`[data-camera="${item.id}"] video`),player={video};cameraPlayers.set(item.id,player);
 const playing=()=>cameraStatus(item.id,'Live · short delay');video.onplaying=playing;
 video.onwaiting=()=>cameraStatus(item.id,'Buffering…');
 video.onerror=()=>{stopCamera(item.id);cameraStatus(item.id,'Connection interrupted. Retrying…');};
 function play(){video.play().catch(()=>cameraStatus(item.id,'Tap play to view this camera.'));}
 // Safari on phones supports native HLS; other supported browsers use hls.js.
 if(video.canPlayType('application/vnd.apple.mpegurl')){video.src=item.stream;play();}
 else if(window.Hls&&Hls.isSupported()){
  const hls=new Hls({maxBufferLength:12,maxMaxBufferLength:20,liveSyncDurationCount:2});player.hls=hls;
  hls.loadSource(item.stream);hls.attachMedia(video);hls.on(Hls.Events.MANIFEST_PARSED,play);
  hls.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal){stopCamera(item.id);cameraStatus(item.id,'Connection interrupted. Retrying…');}});
 }else{cameraPlayers.delete(item.id);cameraStatus(item.id,'Video playback is unavailable in this browser.');}
}
async function refreshCameras(){
 if(cameraBusy||document.hidden)return;cameraBusy=true;
 try{
  const d=await getJSON('/api/cameras?channels='+cameraIds().join(','));
  if(document.hidden)return;cameraNotice.textContent=d.note;
  for(const item of d.cameras){if(!cameraIds().includes(item.id))continue;
   if(item.state==='ready')startCamera(item);
   else{stopCamera(item.id);cameraStatus(item.id,item.state==='setup-required'?'Recorder login needed.':item.state==='signin-required'?'Recorder login or live-view permission needs checking.':item.state==='starting'?'Connecting…':'Camera unavailable. Retrying…');}
  }
 }catch{cameraNotice.textContent='Camera connection unavailable. Retrying automatically.';}
 finally{cameraBusy=false;}
}
function selectCameras(){const ids=cameraIds();cameraGrid.classList.toggle('single',ids.length===1);for(let id=1;id<=6;id++){document.querySelector(`[data-camera="${id}"]`).hidden=!ids.includes(id);if(!ids.includes(id))stopCamera(id);}refreshCameras();}
cameraSelect.addEventListener('change',selectCameras);
document.getElementById('camera-retry').addEventListener('click',()=>{for(const id of cameraPlayers.keys())stopCamera(id);refreshCameras();});
document.addEventListener('visibilitychange',()=>{if(document.hidden){for(const id of cameraPlayers.keys())stopCamera(id);}else{refreshCameras();}});
window.addEventListener('online',refreshCameras);window.addEventListener('pageshow',refreshCameras);
window.addEventListener('pagehide',()=>{for(const id of cameraPlayers.keys())stopCamera(id);});
selectCameras();setInterval(refreshCameras,5000);
