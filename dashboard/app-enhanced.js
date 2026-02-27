/**
 * Auto Company Dashboard - Enhanced Edition
 * ==========================================
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

  // Activities
  activitiesTimeline: document.getElementById("activitiesTimeline"),
  agentStats: document.getElementById("agentStats"),
  activitiesCount: document.getElementById("activitiesCount"),

  // Controls
  btnStart: document.getElementById("btnStart"),
  btnStop: document.getElementById("btnStop"),
  btnRefresh: document.getElementById("btnRefresh"),
  btnConsensus: document.getElementById("btnConsensus"),
  btnLog: document.getElementById("btnLog"),
  autoRefresh: document.getElementById("autoRefresh"),
  refreshInterval: document.getElementById("refreshInterval"),
  engineSelect: document.getElementById("engineSelect"),

  // Tabs
  tabs: document.querySelectorAll(".tab"),
  tabContents: document.querySelectorAll(".tab-content"),

  // Files
  fileTree: document.getElementById("fileTree"),
  filePreview: document.getElementById("filePreview"),

  // Logs
  logType: document.getElementById("logType"),
  logSearch: document.getElementById("logSearch"),
  btnLogSearch: document.getElementById("btnLogSearch"),
  cycleSelector: document.getElementById("cycleSelector"),
  cycleSelect: document.getElementById("cycleSelect"),

  // Cycles
  cyclesList: document.getElementById("cyclesList"),
  btnRefreshCycles: document.getElementById("btnRefreshCycles"),
};

// State
let autoTimer = null;
let lastData = null;
let currentDir = "docs";
let currentFile = null;
let cyclesData = [];
let logCache = "";

// Constants
const ACTION_LABELS = {
  propose: "提出方案",
  review: "审查评估",
  analyze: "分析调研",
  decision: "做出决策",
  build: "编码构建",
  deploy: "部署发布",
};

const ACTION_COLORS = {
  propose: "#3b82f6",
  review: "#f59e0b",
  analyze: "#8b5cf6",
  decision: "#ef4444",
  build: "#10b981",
  deploy: "#06b6d4",
};

const AGENT_COLORS = {
  "ceo-bezos": "#ff6b35",
  "cto-vogels": "#004e89",
  "critic-munger": "#7209b7",
  "product-norman": "#f72585",
  "ui-duarte": "#4cc9f0",
  "interaction-cooper": "#4895ef",
  "fullstack-dhh": "#560bad",
  "qa-bach": "#00bbf9",
  "devops-hightower": "#00f5d4",
  "marketing-godin": "#9b5de5",
  "operations-pg": "#f15bb5",
  "sales-ross": "#fee440",
  "cfo-campbell": "#00cfcf",
  "research-thompson": "#2ec4b6",
};

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
  let inTable = false;

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

  const closeTable = () => {
    if (inTable) {
      out.push("</tbody></table>");
      inTable = false;
    }
  };

  for (const line of lines) {
    // Code blocks
    if (line.startsWith("```")) {
      closeParagraph();
      closeList();
      closeTable();
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

    // Table rows
    if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
      closeParagraph();
      closeList();
      
      const cells = line.trim().slice(1, -1).split("|").map(c => c.trim());
      
      if (!inTable) {
        out.push("<table><thead><tr>");
        cells.forEach(cell => {
          out.push(`<th>${renderInlineMarkdown(cell)}</th>`);
        });
        out.push("</tr></thead><tbody>");
        inTable = true;
        continue;
      }
      
      // Skip separator row
      if (cells.every(c => /^[-:]+$/.test(c))) {
        continue;
      }
      
      out.push("<tr>");
      cells.forEach(cell => {
        out.push(`<td>${renderInlineMarkdown(cell)}</td>`);
      });
      out.push("</tr>");
      continue;
    }
    
    closeTable();

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

    // Checkbox items
    const cb = line.match(/^\s*-\s+\[([ xX])\]\s+(.*)$/);
    if (cb) {
      closeParagraph();
      if (!inList) {
        out.push("<ul>");
        inList = true;
      }
      const checked = cb[1].toLowerCase() === 'x' ? 'checked' : '';
      out.push(`<li><input type="checkbox" ${checked} disabled> ${renderInlineMarkdown(cb[2].trim())}</li>`);
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
  closeTable();
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
 * Format file size
 */
function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

/**
 * Update status badge
 */
function updateStatusBadge(running, state) {
  els.statusBadge.className = `status-badge ${running ? "running" : "stopped"}`;
  els.statusText.textContent = running ? "运行中" : "已停止";
  els.cardLoop.className = `card ${running ? "good" : "warn"}`;
  els.cardEngine.className = `card ${running ? "good" : ""}`;
}

/**
 * Render agent avatar
 */
function renderAgentAvatar(agent, role) {
  const color = AGENT_COLORS[agent] || "#6b7280";
  const initial = (role || agent || "?").charAt(0).toUpperCase();
  return `<div class="agent-avatar" style="background-color: ${color}">${initial}</div>`;
}

/**
 * Render activities timeline
 */
function renderActivities(activities) {
  if (!activities || activities.length === 0) {
    if (els.activitiesTimeline) {
      els.activitiesTimeline.innerHTML = `
        <div class="empty-state">
          <p>暂无 Agent 活动记录</p>
          <p style="font-size: 12px;">等待下一个工作周期开始...</p>
        </div>
      `;
    }
    if (els.activitiesCount) {
      els.activitiesCount.textContent = "0 条记录";
    }
    return;
  }

  if (els.activitiesCount) {
    els.activitiesCount.textContent = `${activities.length} 条记录`;
  }

  if (!els.activitiesTimeline) return;

  const html = activities.map((act) => {
    const agent = act.agent || "unknown";
    const role = act.role || agent;
    const action = act.action || "unknown";
    const actionLabel = ACTION_LABELS[action] || action;
    const actionColor = ACTION_COLORS[action] || "#6b7280";
    const time = formatShortTime(act.ts);
    const input = act.input || "";
    const output = act.output || "";
    const file = act.file || "";
    const cycle = act.cycle || "?";

    return `
      <div class="activity-item">
        <div class="activity-header">
          ${renderAgentAvatar(agent, role)}
          <div class="activity-meta" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span class="activity-agent">${escapeHtml(role)}</span>
            <span class="activity-action" style="color: ${actionColor}">${escapeHtml(actionLabel)}</span>
            <span class="activity-time">${escapeHtml(time)}</span>
          </div>
          <span class="activity-cycle">Cycle #${escapeHtml(String(cycle))}</span>
        </div>
        <div class="activity-content">
          ${input ? `<div class="activity-input"><strong>输入:</strong> ${escapeHtml(input)}</div>` : ""}
          ${output ? `<div class="activity-output"><strong>输出:</strong> ${escapeHtml(output)}</div>` : ""}
          ${file ? `<div class="activity-file"><strong>文件:</strong> <code>${escapeHtml(file)}</code></div>` : ""}
        </div>
      </div>
    `;
  }).join("");

  els.activitiesTimeline.innerHTML = html;
}

/**
 * Render agent stats
 */
function renderAgentStats(stats) {
  if (!els.agentStats || !stats) return;

  const agents = Object.entries(stats).sort((a, b) => b[1].count - a[1].count);

  if (agents.length === 0) {
    els.agentStats.innerHTML = '<p style="color: var(--text-muted); font-size: 12px;">暂无统计数据</p>';
    return;
  }

  const html = agents.map(([agent, data]) => {
    const color = AGENT_COLORS[agent] || "#6b7280";
    const initial = (data.role || agent).charAt(0).toUpperCase();

    return `
      <div class="agent-stat-item">
        <div class="agent-avatar" style="background-color: ${color}; width: 28px; height: 28px; font-size: 11px;">${initial}</div>
        <div class="agent-stat-info">
          <span class="agent-name">${escapeHtml(data.role || agent)}</span>
          <span class="agent-count">${data.count} 次活动</span>
        </div>
      </div>
    `;
  }).join("");

  els.agentStats.innerHTML = html;
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

    updateStatusBadge(data.loop?.running, data.loop?.state);

    const loop = data.loop || {};

    els.loopState.textContent = loop.state === "running" ? "运行中" : "已停止";
    els.loopMeta.textContent = `PID: ${loop.pid || "--"} | 循环: ${loop.loopCount || "0"}`;

    els.engineName.textContent = (data.engine?.active || "qwen").toUpperCase();
    els.engineMeta.textContent = `模型: ${loop.model || "默认"}`;

    els.cycleCount.textContent = loop.loopCount || "0";
    els.cycleMeta.textContent = `错误: ${loop.errorCount || "0"}`;

    els.lastRun.textContent = formatShortTime(loop.lastRun);
    els.lastRunMeta.textContent = loop.status || "--";

    renderStateList(data);

    if (data.consensus) {
      els.consensusContent.innerHTML = renderMarkdown(data.consensus);
    }

    if (data.logTail) {
      logCache = data.logTail;
      if (els.logType.value === "main") {
        els.logTerminal.textContent = data.logTail;
        els.logTerminal.scrollTop = els.logTerminal.scrollHeight;
      }
    }

    renderActivities(data.activities || []);
    renderAgentStats(data.agentStats || {});

    els.updateTime.textContent = formatTime(data.timestamp);

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

    await fetchStatus();

  } catch (err) {
    alert(`请求失败: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

/**
 * Fetch files from API
 */
async function fetchFiles(dir) {
  try {
    const res = await fetch(`/api/files?dir=${encodeURIComponent(dir)}`, { cache: "no-store" });
    const data = await res.json();
    currentDir = dir;
    renderFileTree(data);
  } catch (err) {
    console.error("Failed to fetch files:", err);
    els.fileTree.innerHTML = `<div class="empty-state"><p>加载失败: ${err.message}</p></div>`;
  }
}

/**
 * Render file tree
 */
function renderFileTree(data) {
  if (data.error) {
    els.fileTree.innerHTML = `<div class="empty-state"><p>${escapeHtml(data.error)}</p></div>`;
    return;
  }

  const dirs = data.dirs || [];
  const files = data.files || [];

  let html = '<div class="file-tree-header">' + escapeHtml(currentDir) + '/</div>';

  dirs.forEach(d => {
    html += `
      <div class="file-item dir" data-path="${escapeHtml(d.path)}" data-type="dir">
        <span style="flex: 1">${escapeHtml(d.name)}</span>
      </div>
    `;
  });

  files.forEach(f => {
    const itemClass = f.type === "markdown" ? "file-markdown" : 
                      f.type === "code" ? "file-code" :
                      f.type === "json" ? "file-json" :
                      f.type === "log" ? "file-log" : "file";
    html += `
      <div class="file-item ${itemClass}" data-path="${escapeHtml(f.path)}" data-type="${f.type}">
        <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(f.name)}</span>
        <span class="size">${formatSize(f.size)}</span>
      </div>
    `;
  });

  els.fileTree.innerHTML = html;

  // Bind click events
  els.fileTree.querySelectorAll(".file-item").forEach(item => {
    item.addEventListener("click", () => {
      els.fileTree.querySelectorAll(".file-item").forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      
      if (item.dataset.type === "dir") {
        browseSubdir(item.dataset.path);
      } else {
        fetchFileContent(item.dataset.path);
      }
    });
  });
}

/**
 * Browse subdirectory
 */
async function browseSubdir(path) {
  try {
    const res = await fetch(`/api/files/${encodeURIComponent(path)}`, { cache: "no-store" });
    const data = await res.json();
    renderFileTree(data);
  } catch (err) {
    console.error("Failed to browse subdir:", err);
  }
}

/**
 * Fetch file content
 */
async function fetchFileContent(path) {
  try {
    const res = await fetch(`/api/file/${encodeURIComponent(path)}`, { cache: "no-store" });
    const data = await res.json();

    if (data.error) {
      els.filePreview.innerHTML = `<div class="empty-state"><p>${escapeHtml(data.error)}</p></div>`;
      return;
    }

    currentFile = data;

    let content = "";
    if (data.type === "markdown") {
      content = `<div class="markdown-preview">${renderMarkdown(data.content)}</div>`;
    } else if (data.type === "json") {
      try {
        const json = JSON.parse(data.content);
        content = `<pre>${escapeHtml(JSON.stringify(json, null, 2))}</pre>`;
      } catch {
        content = `<pre>${escapeHtml(data.content)}</pre>`;
      }
    } else {
      content = `<pre>${escapeHtml(data.content)}</pre>`;
    }

    els.filePreview.innerHTML = `
      <div class="file-preview-header">
        <h4>📄 ${escapeHtml(data.name)}</h4>
        <div style="display: flex; gap: 8px;">
          <span style="font-size: 11px; color: var(--text-muted);">${formatSize(data.size)}</span>
          <a href="/api/download/${encodeURIComponent(path)}" class="btn btn-secondary small" download>下载</a>
        </div>
      </div>
      <div class="file-preview-content">${content}</div>
    `;
  } catch (err) {
    console.error("Failed to fetch file:", err);
    els.filePreview.innerHTML = `<div class="empty-state"><p>加载失败: ${err.message}</p></div>`;
  }
}

/**
 * Fetch cycle logs
 */
async function fetchCycles() {
  try {
    const res = await fetch("/api/cycles", { cache: "no-store" });
    const data = await res.json();
    cyclesData = data.cycles || [];
    
    renderCyclesList(cyclesData);
    renderCycleSelector(cyclesData);
  } catch (err) {
    console.error("Failed to fetch cycles:", err);
    els.cyclesList.innerHTML = `<div class="empty-state"><p>加载失败: ${err.message}</p></div>`;
  }
}

/**
 * Render cycles list
 */
function renderCyclesList(cycles) {
  if (!cycles || cycles.length === 0) {
    els.cyclesList.innerHTML = '<div class="empty-state"><p>暂无周期记录</p></div>';
    return;
  }

  const html = cycles.slice(0, 20).map(c => `
    <div class="activity-item" style="cursor: pointer;" data-filename="${escapeHtml(c.filename)}">
      <div class="activity-header">
        <span class="activity-agent">Cycle #${c.cycle}</span>
        <span class="activity-action" style="color: var(--accent)">${c.engine.toUpperCase()}</span>
        <span class="activity-time">${formatTime(c.mtime)}</span>
        <span class="activity-cycle">${formatSize(c.size)}</span>
      </div>
      <div class="activity-content">
        <code>${escapeHtml(c.filename)}</code>
      </div>
    </div>
  `).join("");

  els.cyclesList.innerHTML = html;

  // Bind click events
  els.cyclesList.querySelectorAll(".activity-item").forEach(item => {
    item.addEventListener("click", () => {
      fetchCycleLog(item.dataset.filename);
    });
  });
}

/**
 * Render cycle selector
 */
function renderCycleSelector(cycles) {
  if (!cycles || cycles.length === 0) {
    els.cycleSelect.innerHTML = '<option value="">无周期日志</option>';
    return;
  }

  const html = cycles.slice(0, 50).map(c => 
    `<option value="${escapeHtml(c.filename)}">Cycle #${c.cycle} - ${c.engine.toUpperCase()} - ${formatTime(c.mtime)}</option>`
  ).join("");

  els.cycleSelect.innerHTML = html;
}

/**
 * Fetch single cycle log
 */
async function fetchCycleLog(filename) {
  if (!filename) {
    els.logTerminal.textContent = "请选择周期日志";
    return;
  }

  try {
    const res = await fetch(`/api/cycle/${encodeURIComponent(filename)}`, { cache: "no-store" });
    const data = await res.json();

    if (data.error) {
      els.logTerminal.textContent = data.error;
      return;
    }

    els.logTerminal.textContent = data.content || "(空日志)";
    els.logTerminal.scrollTop = 0;
  } catch (err) {
    console.error("Failed to fetch cycle log:", err);
    els.logTerminal.textContent = `加载失败: ${err.message}`;
  }
}

/**
 * Filter log by search term
 */
function filterLog(search) {
  if (!search) {
    els.logTerminal.textContent = logCache;
    return;
  }

  const lines = logCache.split("\n");
  const filtered = lines.filter(line => 
    line.toLowerCase().includes(search.toLowerCase())
  );
  els.logTerminal.textContent = filtered.join("\n") || "(无匹配结果)";
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

// Tab switching
els.tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    els.tabs.forEach(t => t.classList.remove("active"));
    els.tabContents.forEach(c => c.classList.remove("active"));
    
    tab.classList.add("active");
    const tabId = `tab-${tab.dataset.tab}`;
    document.getElementById(tabId)?.classList.add("active");

    // Load data for specific tabs
    if (tab.dataset.tab === "files") {
      fetchFiles(currentDir);
    } else if (tab.dataset.tab === "cycles") {
      fetchCycles();
    }
  });
});

// Directory buttons
document.querySelectorAll("[data-dir]").forEach(btn => {
  btn.addEventListener("click", () => {
    fetchFiles(btn.dataset.dir);
  });
});

// Log type selector
els.logType?.addEventListener("change", () => {
  if (els.logType.value === "main") {
    els.cycleSelector.style.display = "none";
    els.logTerminal.textContent = logCache;
  } else {
    els.cycleSelector.style.display = "flex";
    fetchCycles();
  }
});

// Cycle selector
els.cycleSelect?.addEventListener("change", () => {
  fetchCycleLog(els.cycleSelect.value);
});

// Event Listeners
els.btnStart?.addEventListener("click", () => runAction("start"));
els.btnStop?.addEventListener("click", () => runAction("stop"));
els.btnRefresh?.addEventListener("click", fetchStatus);
els.btnConsensus?.addEventListener("click", fetchStatus);
els.btnLog?.addEventListener("click", fetchStatus);
els.btnRefreshCycles?.addEventListener("click", fetchCycles);
els.autoRefresh?.addEventListener("change", resetAutoTimer);
els.refreshInterval?.addEventListener("change", resetAutoTimer);

els.btnLogSearch?.addEventListener("click", () => {
  filterLog(els.logSearch?.value);
});

els.logSearch?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    filterLog(els.logSearch.value);
  }
});

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  if (e.key === "r" && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== "INPUT") {
    fetchStatus();
  }
  if (e.key === "s" && e.shiftKey && !e.ctrlKey && !e.metaKey) {
    runAction("start");
  }
  if (e.key === "x" && e.shiftKey && !e.ctrlKey && !e.metaKey) {
    runAction("stop");
  }
});

// Initialize
fetchStatus();
resetAutoTimer();

console.log("Auto Company Dashboard - Enhanced Edition initialized");
console.log("Keyboard shortcuts: R=Refresh, Shift+S=Start, Shift+X=Stop");