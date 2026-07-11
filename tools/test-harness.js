/**
 * bai-tuan 驗收 harness — 整段貼進 Claude Preview 的 preview_eval 執行。
 *
 * 為什麼需要：preview 分頁在背景時瀏覽器暫停 requestAnimationFrame，
 * 遊戲主迴圈不會跑、截圖工具逾時。此 harness 把 index.html 載進 iframe，
 * 用 shim 接管 rAF 與 performance.now，改成「虛擬時鐘」：
 *   w.__step(n, dtms)  → 手動推進 n 幀（預設每幀 50ms，可快轉，例如 1900 幀 = 95 秒）
 *   w.__errs           → 頁面內收集到的 JS 錯誤
 *
 * 用法（在 preview_eval 內）：
 *   const { w, idoc, spr, pt } = await setupDogTest(390);   // 390 = 手機寬
 *   w.__step(1900);                                          // 快轉 95 秒 → lonely
 *   spr.dataset.pose                                         // 讀當前姿勢
 *   pt('pointerdown', x, y); pt('pointermove', x+10, y); ... // 模擬觸控
 *   驗完記得 document.getElementById('dogTestFrame').remove();
 */
async function setupDogTest(width) {
  var html = await fetch('/index.html?nc=' + Date.now()).then(function(r){ return r.text(); });
  var ifr = document.createElement('iframe');
  ifr.id = 'dogTestFrame';
  ifr.style.cssText = 'position:fixed;left:0;top:0;width:' + (width || 390) +
                      'px;height:700px;border:0;z-index:999;background:#fff';
  document.body.appendChild(ifr);
  var shim = '<scr' + 'ipt>window.__vt=0;window.__frames=[];' +
    'window.requestAnimationFrame=function(cb){window.__frames.push(cb);return 1};' +
    'performance.now=function(){return window.__vt};' +
    'window.__step=function(n,dtms){dtms=dtms||50;for(var i=0;i<n;i++){window.__vt+=dtms;' +
    'var f=window.__frames;window.__frames=[];for(var j=0;j<f.length;j++)f[j](window.__vt);}};' +
    'window.__errs=[];window.addEventListener("error",function(e){window.__errs.push(String(e.message))});' +
    '</scr' + 'ipt>';
  html = html.replace('<script>', shim + '<script>');
  var idoc = ifr.contentDocument;
  idoc.open(); idoc.write(html); idoc.close();
  await new Promise(function(r){ setTimeout(r, 300); });
  var w = ifr.contentWindow;
  function pt(type, x, y) {
    var el = idoc.elementFromPoint(x, y) || idoc.getElementById('scene');
    el.dispatchEvent(new w.PointerEvent(type, { bubbles: true, clientX: x, clientY: y, pointerId: 1 }));
  }
  return { w: w, idoc: idoc, spr: idoc.getElementById('dogSprite'), pt: pt, frame: ifr };
}
