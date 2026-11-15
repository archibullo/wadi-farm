/* Offline-first FIELD LOG ONLY. No stock/finance/actuation functions. */
(() => {
  const $ = id => document.getElementById(id);
  const DB = 'wadi-farm-mobile-v1';
  let context = null;
  let db;
  function inform(message, bad = false) { $('message').textContent = message; $('message').style.color = bad ? '#ad392c' : '#28654b'; }
  function openDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB, 1);
      request.onupgradeneeded = () => { const d = request.result; d.createObjectStore('records', { keyPath: 'client_event_uuid' }); d.createObjectStore('settings'); };
      request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error);
    });
  }
  function table(name, mode, operation) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(name, mode), os = tx.objectStore(name);
      const request = operation(os);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
  const getSetting = key => table('settings','readonly', s => s.get(key));
  const putSetting = (key, value) => table('settings','readwrite', s => s.put(value,key));
  const getRecords = () => table('records','readonly', s => s.getAll());
  const saveRecord = item => table('records','readwrite', s => s.put(item));
  function connectionState() { $('connection').textContent = navigator.onLine ? '● متصل' : '● دون اتصال'; }
  function fillOptions() {
    if (!context) return;
    const sel = $('farm'), keep = sel.value;
    sel.replaceChildren(new Option('اختر المزرعة',''));
    for (const farm of context.farms) sel.add(new Option(farm.farm_name, farm.name));
    if ([...sel.options].some(x => x.value === keep)) sel.value = keep;
    updateFields();
  }
  function updateFields() {
    const sel = $('field'), farm = $('farm').value, keep = sel.value;
    sel.replaceChildren(new Option('بدون حقل محدد',''));
    for (const field of (context?.fields || []).filter(x => x.farm === farm)) sel.add(new Option(field.field_name,field.name));
    if ([...sel.options].some(x => x.value === keep)) sel.value = keep;
  }
  async function bootstrap() {
    try {
      const resp = await fetch('/api/method/wadi_farm.api.mobile.get_mobile_context', { credentials: 'same-origin', cache: 'no-store' });
      if (!resp.ok) throw Error(`HTTP ${resp.status}; يلزم تسجيل الدخول إلى ERPNext`);
      const data = await resp.json();
      context = data.message;
      if (!context || !Array.isArray(context.farms)) throw Error('بيانات المستخدم غير متاحة');
      const {csrf_token, ...safeContext} = context;
      await putSetting('context',safeContext); // CSRF token is session-bound; never persist it offline. 
      fillOptions(); inform('تم تحديث المزارع والحقول.');
    } catch(error) {
      context = await getSetting('context');
      if (context) { fillOptions(); inform('تستخدم البيانات المحفوظة محليًا؛ ستتم المزامنة بعد الاتصال.'); }
      else inform('افتح التطبيق أثناء الاتصال وسجّل الدخول إلى ERPNext أول مرة: ' + error.message, true);
    }
  }
  async function displayRecords() {
    const entries = (await getRecords()).sort((a,b) => b.event_at.localeCompare(a.event_at));
    const pending = entries.filter(r => ['pending','retry'].includes(r.local_status)).length;
    $('pending-badge').textContent = pending + ' قيد الإرسال';
    $('records').replaceChildren();
    for (const x of entries.slice(0,60)) {
      const wrap = document.createElement('div'); wrap.className = 'record';
      const div = document.createElement('div'); const title = document.createElement('strong');
      title.textContent = x.activity_type + (x.quantity === null ? '' : ` (${x.quantity} ${x.unit || ''})`);
      const desc = document.createElement('div');desc.className='meta';desc.textContent= x.event_at.replace('T',' ').slice(0,19) + ' · ' + (x.notes || 'بدون ملاحظات');
      div.append(title,desc);
      const state = document.createElement('div');state.className='status'+(['conflict','rejected','retry'].includes(x.local_status)?' fail':'');state.textContent=({pending:'قيد المزامنة',retry:'إعادة المحاولة',created:'تم',duplicate:'مكرر مطابق',conflict:'تعارض',rejected:'مرفوض'})[x.local_status]||x.local_status;
      wrap.append(div,state);$('records').append(wrap);
    }
  }
  async function createEvent(e) {
    e.preventDefault();
    if (!context || !$('farm').value) return inform('اختر مزرعة بعد تحميل بياناتك.',true);
    const entry = { client_event_uuid: crypto.randomUUID(),farm:$('farm').value,field:$('field').value || null,
      activity_type:$('activity').value,event_at:new Date().toISOString(),
      quantity:$('quantity').value === '' ? null : Number($('quantity').value),unit:$('unit').value.trim(),notes:$('notes').value.trim(),
      device_id:'mobile-web-v1',local_status:'pending',local_user:context.user };
    if (entry.quantity !== null && (!Number.isFinite(entry.quantity) || entry.quantity < 0)) return inform('الكمية يجب أن تكون رقمًا غير سالب.',true);
    await saveRecord(entry);$('notes').value='';$('quantity').value='';$('unit').value='';
    inform('تم الحفظ محليًا؛ لم تُعتمد أي حركة مخزون أو تشغيل.');
    await displayRecords();
  }
  async function sync() {
    if (!navigator.onLine) return inform('لا يوجد اتصال؛ السجلات محفوظة.',true);
    const token = context?.csrf_token;
    if (!token) { await bootstrap(); if (!context?.csrf_token) return inform('سجّل الدخول إلى ERPNext لتفعيل المزامنة.',true); }
    const entries = (await getRecords()).filter(r => ['pending','retry'].includes(r.local_status) && r.local_user === context?.user);
    if (!entries.length) return inform('لا توجد سجلات جديدة للمزامنة.');
    $('sync').disabled=true;
    try {
      for (let i=0;i<entries.length;i+=25) {
        const group=entries.slice(i,i+25);
        const events=group.map(({local_status,server_name,local_user,...item}) => item);
        const resp=await fetch('/api/method/wadi_farm.api.mobile.sync_batch',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Frappe-CSRF-Token':context.csrf_token},body:JSON.stringify({events})});
        if (!resp.ok) throw Error('فشل طلب المزامنة: HTTP '+resp.status);
        const data=await resp.json(), results=data?.message?.results;
        if (!Array.isArray(results)) throw Error('رد السيرفر غير معروف');
        for (const result of results) {
          const entry=group.find(x => x.client_event_uuid===result.id);if (!entry) continue;
          entry.local_status=result.status; entry.server_name=result.name||''; await saveRecord(entry);
        }
      }
      inform('اكتملت محاولة المزامنة. راجع التعارضات والمرفوضات إن وجدت.');
    } catch(e) {inform(e.message+'؛ ستبقى السجلات دون فقد، ويمكن إعادة المحاولة.',true);}
    finally {$('sync').disabled=false;await displayRecords();}
  }
  async function main() {
    db=await openDB();connectionState();window.addEventListener('online',connectionState);window.addEventListener('offline',connectionState);
    $('farm').addEventListener('change',updateFields);$('field-form').addEventListener('submit',createEvent);$('sync').addEventListener('click',sync);
    $('clear-local').addEventListener('click', async () => {
      const records=await getRecords();
      if (records.some(x=>['pending','retry'].includes(x.local_status))) return inform('يوجد سجلات لم تُزامن؛ لا يمكن المسح.',true);
      if (!confirm('هل قمت بمراجعة السجلات على ERPNext وتريد مسح النسخة المحلية على هذا الجهاز؟')) return;
      await table('records','readwrite', store=>store.clear()); await table('settings','readwrite',store=>store.clear());
      context=null;await displayRecords();inform('تم مسح البيانات المحلية. يلزم الاتصال لتسجيل الدخول مجددًا.');
    });
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
    await bootstrap();await displayRecords();
  }
  main().catch(error => inform('خطأ في قاعدة البيانات المحلية: '+error.message,true));
})();
