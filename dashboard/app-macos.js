/**
 * Auto Company Dashboard - macOS Edition
 * ======================================
 * Web dashboard for monitoring and controlling Auto Company loop.
 */

// DOM Elements
const els = {
  // Status
  statusBadge: document.getElementById("statusBadge"),
  statusText: document.getElementById("statusText"),

  // Cards
  cardLoop: document.getElementById("cardLoop"),
  cardEngine: document.getElementById("cardEngine"),
  cardCycles: document.getElementById("cardCycles"),
  cardLastRun: document.getElementById("cardLastRun"),
  loopState: document.getElementById("loopState"),
  loopMeta: document.getElementById("loopMeta"),
  engineName: document.getElementById("engineName"),
  engineMeta: document.getElementById("engineMeta"),
  cycleCount: document.getElementById("cycleCount"),
  cycleMeta: document.getElementById("cycleMeta"),
  lastRun: document.getElementById("lastRun"),
  lastRunMeta: document.getElementById("lastRunMeta"),

  // Content
  consensusContent: document.getElementById("consensusContent"),
  stateList: document.getElementById("stateList"),
  logTerminal: document.getElementById("logTerminal"),
  updateTime: document.getElementById("updateTime"),

  // Controls
  btnStart: document.getElementById("btnStart"),
  btnStop: document.getElementById("btnStop"),
  btnRefresh: document.getElementById("btnRefresh"),
  btnConsensus: document.getElementById("btnConsensus"),
  btnLog: document.getElementById("btnLog"),
  autoRefresh: document.getElementById("autoRefresh"),
  refreshInterval: document.getElementById("refreshInterval"),
  engineSelect: document.getElementById("engineSelect"),
};

// State
let autoTimer = null;
let lastData = null;

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * Render inline markdown
 */
function renderInlineMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  return html;
}

/**
 * Render markdown to HTML
 */
function renderMarkdown(md) {
  const lines = String(md || "").replace(/\r\n?/g, "\n").split("\n");
  const out = [];
  let inList = false;
  let inCode = false;
  let inParagraph = false;

  const closeParagraph = () => {
    if (inParagraph) {
      out.push("</p>");
      inParagraph = false;
    }
  };
  
  const closeList = () => {
    if (inList) {
      out.push("</ul>");
      inList = false;
    }
  };

  for (const line of lines) {
    // Code blocks
    if (line.startsWith("```")) {
      closeParagraph();
      closeList();
      if (!inCode) {
        out.push("<pre><code>");
        inCode = true;
      } else {
        out.push("</code></pre>");
        inCode = false;
      }
      continue;
    }

    if (inCode) {
      out.push(`${escapeHtml(line)}\n`);
      continue;
    }

    // Empty line
    if (!line.trim()) {
      closeParagraph();
      closeList();
      continue;
    }

    // Headers
    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      closeParagraph();
      closeList();
      const level = h[1].length;
      out.push(`<h${level}>${renderInlineMarkdown(h[2].trim())}</h${level}>`);
      continue;
    }

    // List items
    const li = line.match(/^\s*[-*]\s+(.*)$/);
    if (li) {
      closeParagraph();
      if (!inList) {
        out.push("<ul>");
        inList = true;
      }
      out.push(`<li>${renderInlineMarkdown(li[1].trim())}</li>`);
      continue;
    }

    // Regular text
    closeList();
    if (!inParagraph) {
      out.push("<p>");
      inParagraph = true;
    } else {
      out.push("<br />");
    }
    out.push(renderInlineMarkdown(line.trim()));
  }

  closeParagraph();
  closeList();
  if (inCode) {
    out.push("</code></pre>");
  }

  return out.join("");
}

/**
 * Format timestamp
 */
function formatTime(isoText) {
  if (!isoText) return "--";
  try {
    const date = new Date(isoText);
    return date.toLocaleString("zh-CN", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  } catch {
    return isoText;
  }
}

/**
 * Short time format
 */
function formatShortTime(isoText) {
  if (!isoText) return "--";
  try {
    const date = new Date(isoText);
    return date.toLocaleTimeString("zh-CN");
  } catch {
    return isoText;
  }
}

/**
 * Update status badge
 */
function updateStatusBadge(running, state) {
  els.statusBadge.className = `status-badge ${running ? "running" : "stopped"}`;
  els.statusText.textContent = running ? "运行中" : "已停止";
  
  // Update card styles
  els.cardLoop.className = `card ${running ? "good" : "warn"}`;
  els.cardEngine.className = `card ${running ? "good" : ""}`;
}

/**
 * Render state list
 */
function renderStateList(data) {
  const loop = data.loop || {};
  const state = data.state || {};
  const progress = data.progress || {};
  
  const rows = [
    ["引擎", loop.engine || state.ENGINE || "qwen"],
    ["模型", loop.model || state.MODEL || "default"],
    ["状态", loop.status || state.STATUS || "--"],
    ["循环次数", loop.loopCount || state.LOOP_COUNT || "0"],
    ["错误次数", loop.errorCount || state.ERROR_COUNT || "0"],
    ["最后运行", formatTime(loop.lastRun || state.LAST_RUN)],
    ["进程 PID", loop.pid || "--"],
    ["停止请求", loop.stopRequested ? "是" : "否"],
  ];
  
  if (progress.last_action) {
    rows.push(["最近动作", progress.last_action]);
  }
  if (progress.status) {
    rows.push(["动作状态", progress.status]);
  }
  
  els.stateList.innerHTML = rows
    .map(([k, v]) => `
      <div class="state-row">
        <dt>${escapeHtml(k)}</dt>
        <dd>${escapeHtml(String(v))}</dd>
      </div>
    `).join("");
}

/**
 * Fetch status from API
 */
async function fetchStatus() {
  try {
    const res = await fetch("/api/status", { cache: "no-store" });
    const data = await res.json();
    lastData = data;
    
    // Update status badge
    updateStatusBadge(data.loop?.running, data.loop?.state);
    
    // Update cards
    const loop = data.loop || {};
    
    els.loopState.textContent = loop.state === "running" ? "运行中" : "已停止";
    els.loopMeta.textContent = `PID: ${loop.pid || "--"} | 循环: ${loop.loopCount || "0"}`;
    
    els.engineName.textContent = (data.engine?.active || "qwen").toUpperCase();
    els.engineMeta.textContent = `模型: ${loop.model || "默认"}`;
    
    els.cycleCount.textContent = loop.loopCount || "0";
    els.cycleMeta.textContent = `错误: ${loop.errorCount || "0"}`;
    
    els.lastRun.textContent = formatShortTime(loop.lastRun);
    els.lastRunMeta.textContent = loop.status || "--";
    
    // Update state list
    renderStateList(data);
    
    // Update consensus
    if (data.consensus) {
      els.consensusContent.innerHTML = renderMarkdown(data.consensus);
    }
    
    // Update log
    if (data.logTail) {
      els.logTerminal.textContent = data.logTail;
      // Auto scroll to bottom
      els.logTerminal.scrollTop = els.logTerminal.scrollHeight;
    }
    
    // Update time
    els.updateTime.textContent = `更新: ${formatTime(data.timestamp)}`;
    
  } catch (err) {
    console.error("Failed to fetch status:", err);
    els.statusText.textContent = "连接失败";
    els.statusBadge.className = "status-badge stopped";
  }
}

/**
 * Run an action (start/stop)
 */
async function runAction(action) {
  const btn = action === "start" ? els.btnStart : els.btnStop;
  const originalText = btn.textContent;

  btn.disabled = true;
  btn.textContent = "处理中...";

  try {
    let url = `/api/action/${action}`;
    if (action === "start" && els.engineSelect) {
      const engine = els.engineSelect.value;
      url += `?engine=${encodeURIComponent(engine)}`;
    }

    const res = await fetch(url, { method: "POST" });
    const data = await res.json();

    if (!data.ok) {
      alert(`操作失败: ${data.error || "未知错误"}`);
    }

    // Refresh status
    await fetchStatus();

  } catch (err) {
    alert(`请求失败: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

/**
 * Reset auto-refresh timer
 */
function resetAutoTimer() {
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
  }
  
  if (els.autoRefresh.checked) {
    const interval = parseInt(els.refreshInterval.value, 10);
    autoTimer = setInterval(fetchStatus, interval);
  }
}

// Event Listeners
els.btnStart.addEventListener("click", () => runAction("start"));
els.btnStop.addEventListener("click", () => runAction("stop"));
els.btnRefresh.addEventListener("click", fetchStatus);
els.btnConsensus.addEventListener("click", fetchStatus);
els.btnLog.addEventListener("click", fetchStatus);
els.autoRefresh.addEventListener("change", resetAutoTimer);
els.refreshInterval.addEventListener("change", resetAutoTimer);

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // R = Refresh
  if (e.key === "r" || e.key === "R") {
    if (!e.ctrlKey && !e.metaKey && document.activeElement.tagName !== "INPUT") {
      fetchStatus();
    }
  }
  // S = Start
  if (e.key === "s" && e.shiftKey && !e.ctrlKey && !e.metaKey) {
    runAction("start");
  }
  // X = Stop
  if (e.key === "x" && e.shiftKey && !e.ctrlKey && !e.metaKey) {
    runAction("stop");
  }
});

// Initialize
fetchStatus();
resetAutoTimer();

console.log("Auto Company Dashboard initialized");
console.log("Keyboard shortcuts: R=Refresh, Shift+S=Start, Shift+X=Stop");