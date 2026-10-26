const LEETCODE_URL = "https://leetcode.com/problemset/";
const BRIDGE = "http://127.0.0.1:8765/state";
const REFRESH_ALARM = "streakmate-refresh-status";

function dateKey(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
function shiftDateKey(key, days) {
  const [y,m,d] = key.split("-").map(Number);
  const dt = new Date(y,m-1,d); dt.setDate(dt.getDate()+days); return dateKey(dt);
}
function moodFor(data) {
  const today = dateKey();
  if (data.lastCompletedDate === today) return "happy";
  const last = data.lastAcceptedAt ? new Date(data.lastAcceptedAt).getTime() : 0;
  if (last && Date.now() - last >= 23 * 60 * 60 * 1000) return "panic";
  return "chill";
}
async function syncBridge(data) {
  const mood = moodFor(data);
  const payload = {
    streakCount: Number(data.streakCount || 0),
    lastCompletedDate: data.lastCompletedDate || "",
    lastAcceptedAt: data.lastAcceptedAt || "",
    mood,
    updatedAt: new Date().toISOString()
  };
  try {
    await fetch(BRIDGE, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
  } catch (_) {
    // The desktop companion may not be running yet. Chrome remains functional without it.
  }
}
async function updateStatus() {
  const data = await chrome.storage.local.get(["streakCount","lastCompletedDate","lastAcceptedAt"]);
  const mood = moodFor(data);
  const icon = mood === "happy" ? "happy" : mood === "panic" ? "panic" : "chill";
  const paths = {};
  for (const size of [16,32,48,128]) paths[size] = `icons/${icon}${size}.png`;
  await chrome.action.setIcon({path: paths});
  await chrome.action.setBadgeText({text: String(Number(data.streakCount || 0))});
  await chrome.action.setBadgeBackgroundColor({color: mood === "happy" ? "#249B69" : mood === "panic" ? "#E34F42" : "#E58B42"});
  const status = mood === "happy" ? "Today's streak is secured!" :
    mood === "panic" ? "23+ hours since your last Accepted submission — save today's streak!" :
    "You haven't completed a problem today. Solve one before midnight to save your streak.";
  await chrome.action.setTitle({title:`StreakMate — ${Number(data.streakCount||0)}-day streak. ${status} Click to open LeetCode.`});
  await syncBridge(data);
}
async function recordAcceptedSubmission() {
  const today = dateKey();
  const data = await chrome.storage.local.get(["streakCount","lastCompletedDate"]);
  if (data.lastCompletedDate === today) { await updateStatus(); return; }
  const yesterday = shiftDateKey(today,-1);
  const count = Number(data.streakCount || 0);
  const next = data.lastCompletedDate === yesterday ? count + 1 : 1;
  await chrome.storage.local.set({
    streakCount: next,
    lastCompletedDate: today,
    lastAcceptedAt: new Date().toISOString()
  });
  await updateStatus();
}
chrome.action.onClicked.addListener(() => chrome.tabs.create({url: LEETCODE_URL}));
chrome.runtime.onMessage.addListener((msg, sender, respond) => {
  if (msg?.type === "STREAKMATE_ACCEPTED") {
    recordAcceptedSubmission().then(()=>respond({ok:true})).catch(()=>respond({ok:false}));
    return true;
  }
});
chrome.alarms.onAlarm.addListener((a)=>{ if(a.name===REFRESH_ALARM) updateStatus(); });
function init() {
  chrome.alarms.create(REFRESH_ALARM,{periodInMinutes:5});
  updateStatus();
}
chrome.runtime.onInstalled.addListener(init);
chrome.runtime.onStartup.addListener(init);
chrome.storage.onChanged.addListener(()=>updateStatus());
