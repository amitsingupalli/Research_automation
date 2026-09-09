<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agentic Research Lab — Autonomous Deep Research Agent</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            lab: {
              bg: '#f5f7fa',
              surface: '#ffffff',
              sidebar: '#0f1729',
              'sidebar-hover': '#1a2340',
              fg: '#1e293b',
              muted: '#64748b',
              border: '#e2e8f0',
              accent: '#16a34a',
              'accent-dim': '#dcfce7',
              'accent-hover': '#15803d',
              surface2: '#f8fafc',
              surface3: '#f1f5f9',
              danger: '#ef4444',
              warning: '#f59e0b',
            }
          },
          fontFamily: {
            display: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
            body: ['Inter', 'SF Pro Text', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'IBM Plex Mono', 'ui-monospace', 'monospace'],
          }
        }
      }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { font-family: 'Inter', system-ui, sans-serif; }
    .scrollbar-thin::-webkit-scrollbar { width: 6px; }
    .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
    .scrollbar-thin::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    .scrollbar-thin::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    .dark-scrollbar::-webkit-scrollbar-thumb { background: #334155; }
    .dark-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
    @keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .pulse-dot { animation: pulse-dot 1.5s ease-in-out infinite; }
    @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .spin-slow { animation: spin-slow 2s linear infinite; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in-up { animation: fadeInUp 0.3s ease-out forwards; }
    @keyframes progressBar { from { width: 0; } to { width: var(--target-width); } }
    .progress-animate { animation: progressBar 1.5s ease-out forwards; }
    .line-clamp-1 { overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 1; }
    .line-clamp-2 { overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
    /* Markdown Table Styling */
    .prose table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1.25rem;
      margin-bottom: 1.25rem;
      font-size: 0.875rem;
      border: 1px solid #cbd5e1;
      border-radius: 0.5rem;
      overflow: hidden;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .prose th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 600;
      text-align: left;
      padding: 0.625rem 0.875rem;
      border: 1px solid #cbd5e1;
    }
    .prose td {
      padding: 0.625rem 0.875rem;
      border: 1px solid #e2e8f0;
      color: #334155;
      vertical-align: top;
    }
    .prose tr:nth-child(even) {
      background-color: #f8fafc;
    }
    .prose tr:hover {
      background-color: #f1f5f9;
    }
  </style>
</head>
<body class="bg-lab-bg">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect, useRef, Fragment } = React;

    const ICONS = {
      Search: () => <i data-lucide="search" className="w-5 h-5"></i>,
      Bot: () => <i data-lucide="bot" className="w-5 h-5"></i>,
      Clock: () => <i data-lucide="clock" className="w-4 h-4"></i>,
      ChevronRight: () => <i data-lucide="chevron-right" className="w-4 h-4"></i>,
      ChevronDown: () => <i data-lucide="chevron-down" className="w-4 h-4"></i>,
      ChevronLeft: () => <i data-lucide="chevron-left" className="w-4 h-4"></i>,
      Settings: () => <i data-lucide="settings" className="w-5 h-5"></i>,
      User: () => <i data-lucide="user" className="w-5 h-5"></i>,
      FileText: () => <i data-lucide="file-text" className="w-5 h-5"></i>,
      Download: () => <i data-lucide="download" className="w-4 h-4"></i>,
      Copy: () => <i data-lucide="copy" className="w-4 h-4"></i>,
      ExternalLink: () => <i data-lucide="external-link" className="w-3.5 h-3.5"></i>,
      Check: () => <i data-lucide="check" className="w-4 h-4"></i>,
      Loader2: () => <i data-lucide="loader-2" className="w-4 h-4 spin-slow"></i>,
      Play: () => <i data-lucide="play" className="w-5 h-5"></i>,
      Newspaper: () => <i data-lucide="newspaper" className="w-5 h-5"></i>,
      BookOpen: () => <i data-lucide="book-open" className="w-5 h-5"></i>,
      MessageSquare: () => <i data-lucide="message-square" className="w-5 h-5"></i>,
      Zap: () => <i data-lucide="zap" className="w-5 h-5"></i>,
      Layers: () => <i data-lucide="layers" className="w-5 h-5"></i>,
      Terminal: () => <i data-lucide="terminal" className="w-4 h-4"></i>,
      MoreHorizontal: () => <i data-lucide="more-horizontal" className="w-4 h-4"></i>,
      FileCode: () => <i data-lucide="file-code" className="w-4 h-4"></i>,
      Hash: () => <i data-lucide="hash" className="w-3 h-3"></i>,
      ArrowUpRight: () => <i data-lucide="arrow-up-right" className="w-4 h-4"></i>,
      Globe: () => <i data-lucide="globe" className="w-4 h-4"></i>,
      Server: () => <i data-lucide="server" className="w-5 h-5"></i>,
    };

    const Icon = ({ name, className = '' }) => {
      const Ic = ICONS[name];
      return Ic ? <span className={className}><Ic /></span> : null;
    };

    const HISTORY = [];

    const REPORT_STEPS = [
      { id: 1, label: 'Searching Google for latest benchmarks', status: 'done' },
      { id: 2, label: 'Reading 14 articles from arXiv & TechCrunch', status: 'done' },
      { id: 3, label: 'Synthesizing findings into report', status: 'active' },
      { id: 4, label: 'Citing sources and formatting', status: 'pending' },
      { id: 5, label: 'Final review and quality check', status: 'pending' },
    ];

    const LOG_ENTRIES = [
      { ts: '14:32:01', level: 'info', msg: 'Agent initiated research on "transformer benchmark 2025"' },
      { ts: '14:32:03', level: 'info', msg: 'Tool: google_search(query="transformer benchmarks 2025 latest results")' },
      { ts: '14:32:05', level: 'ok', msg: 'Search returned 24 results, ranking by relevance...' },
      { ts: '14:32:12', level: 'info', msg: 'Tool: web_fetch(url="arxiv.org/abs/2501.12345")' },
      { ts: '14:32:14', level: 'ok', msg: 'Extracted 3,200 tokens from paper abstract' },
      { ts: '14:32:18', level: 'info', msg: 'Tool: web_fetch(url="techcrunch.com/2025/...")' },
      { ts: '14:32:20', level: 'ok', msg: 'Extracted 1,800 tokens from article' },
      { ts: '14:32:25', level: 'info', msg: 'Tool: reddit_search(subreddit="MachineLearning", query="benchmarks")' },
      { ts: '14:32:28', level: 'warn', msg: 'Reddit rate limit approaching, backing off...' },
      { ts: '14:32:35', level: 'ok', msg: 'Collected 8 relevant discussion threads' },
      { ts: '14:32:40', level: 'info', msg: 'Tool: synthesize_findings(sources=14, tokens=12400)' },
      { ts: '14:32:42', level: 'ok', msg: 'Drafting executive summary...' },
    ];

    const SOURCES = [
      { title: 'Transformer Benchmarks 2025', domain: 'arxiv.org', favicon: '📄', snippet: 'A comprehensive evaluation of LLM performance across 42 tasks...' },
      { title: 'AI Progress Report Q1 2025', domain: 'techcrunch.com', favicon: '📰', snippet: 'Major advances in efficiency and reasoning capabilities...' },
      { title: 'Discussion: Are benchmarks enough?', domain: 'reddit.com', favicon: '💬', snippet: 'Community debate on benchmark saturation vs real-world capability...' },
      { title: 'ML Benchmarks Survey', domain: 'paperswithcode.com', favicon: '📊', snippet: 'Aggregated leaderboard results across vision, NLP, and multimodal...' },
    ];

    /* ─── Sidebar ─── */
    const Sidebar = ({ isOpen, onClose, history, activeId, onSelect }) => (
      <aside className={`${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-72 bg-lab-sidebar text-white flex flex-col transition-transform duration-200`}>
        <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
          <div className="w-9 h-9 rounded-lg bg-lab-accent flex items-center justify-center">
            <Icon name="Bot" />
          </div>
          <div>
            <h1 className="text-sm font-semibold leading-tight">Agentic Research Lab</h1>
            <p className="text-xs text-slate-400 font-mono">v2.1.0-beta</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin dark-scrollbar py-3">
          <p className="px-5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Research History</p>
          {history.length === 0 ? (
            <div className="px-5 py-8 text-center">
              <Icon name="Clock" className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-xs text-slate-500">No research sessions yet</p>
              <p className="text-[11px] text-slate-600 mt-1">Start a query to begin</p>
            </div>
          ) : (
            history.map(item => (
              <button
                key={item.id}
                onClick={() => onSelect(item.id)}
                className={`w-full text-left px-5 py-3 hover:bg-lab-sidebar-hover transition-colors border-l-2 ${activeId === item.id ? 'border-lab-accent bg-lab-sidebar-hover' : 'border-transparent'}`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-sm font-medium line-clamp-1">{item.title}</span>
                  <Icon name="ChevronRight" />
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{item.time}</p>
                <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{item.snippet}</p>
              </button>
            ))
          )}
        </div>

        <div className="border-t border-white/10 px-5 py-4">
          <button className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm">
            <Icon name="Settings" /> Settings
          </button>
        </div>
      </aside>
    );

    /* ─── Search View (State A) ─── */
    const SearchView = ({ onStart }) => {
      const [query, setQuery] = useState('');
      const [depth, setDepth] = useState('deep');
      const [sources, setSources] = useState({ academic: true, web: true, reddit: false });

      const toggleSource = (key) => setSources(s => ({ ...s, [key]: !s[key] }));

      return (
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
          <div className="w-full max-w-2xl">
            <div className="text-center mb-10">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-lab-accent-dim text-lab-accent text-xs font-semibold mb-4">
                <Icon name="Zap" className="w-3.5 h-3.5" /> Research Agent Ready
              </div>
              <h2 className="text-3xl font-bold text-lab-fg tracking-tight">What topic do you want to research?</h2>
              <p className="text-lab-muted mt-2 text-sm">The agent will search, read, synthesize, and produce a structured report with citations.</p>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (query.trim()) onStart({ query, depth, sources });
              }}
              className="bg-lab-surface rounded-xl border border-lab-border shadow-sm"
            >
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-lab-muted"><Icon name="Search" /></div>
                <input
                  type="text"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      if (query.trim()) onStart({ query, depth, sources });
                    }
                  }}
                  placeholder="e.g. Latest advances in transformer efficiency..."
                  className="w-full pl-12 pr-24 py-4 bg-transparent text-lab-fg placeholder:text-slate-400 focus:outline-none text-sm rounded-t-xl"
                  autoFocus
                />
                <div className="absolute right-3.5 top-1/2 -translate-y-1/2 hidden sm:flex items-center gap-1 text-[11px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 pointer-events-none">
                  <span>Enter</span>
                  <span>↵</span>
                </div>
              </div>

              <div className="border-t border-lab-border px-4 py-3 space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-medium text-lab-muted">Research Depth</span>
                  <div className="flex bg-lab-surface2 rounded-lg p-0.5 border border-lab-border">
                    <button
                      type="button"
                      onClick={() => setDepth('quick')}
                      className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${depth === 'quick' ? 'bg-lab-surface shadow-sm text-lab-fg' : 'text-lab-muted hover:text-lab-fg'}`}
                    >
                      ⚡ Quick Brief
                    </button>
                    <button
                      type="button"
                      onClick={() => setDepth('deep')}
                      className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${depth === 'deep' ? 'bg-lab-surface shadow-sm text-lab-fg' : 'text-lab-muted hover:text-lab-fg'}`}
                    >
                      🔬 Deep Dive
                    </button>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-medium text-lab-muted">Sources</span>
                  {[
                    { key: 'academic', icon: 'BookOpen', label: 'Academic Papers' },
                    { key: 'web', icon: 'Globe', label: 'Web News' },
                    { key: 'reddit', icon: 'MessageSquare', label: 'Reddit/Discussions' },
                  ].map(src => (
                    <button
                      type="button"
                      key={src.key}
                      onClick={() => toggleSource(src.key)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${sources[src.key] ? 'bg-lab-accent/10 border-lab-accent/30 text-lab-accent' : 'bg-lab-surface2 border-lab-border text-lab-muted hover:border-slate-300'}`}
                    >
                      <Icon name={src.icon} className="w-3.5 h-3.5" />
                      {src.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="border-t border-lab-border px-4 py-3">
                <button
                  type="submit"
                  disabled={!query.trim()}
                  className="w-full py-2.5 rounded-lg bg-lab-accent hover:bg-lab-accent-hover disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors flex items-center justify-center gap-2"
                >
                  <Icon name="Play" className="w-4 h-4" /> Start Research
                </button>
              </div>
            </form>

            <div className="mt-6 grid grid-cols-3 gap-3">
              {[
                { icon: 'Layers', title: 'Multi-source', desc: 'Web, academic, discussions' },
                { icon: 'FileCode', title: 'Structured output', desc: 'Markdown with citations' },
                { icon: 'Server', title: 'Transparent process', desc: 'Watch every agent step' },
              ].map((f, i) => (
                <div key={i} className="bg-lab-surface border border-lab-border rounded-lg p-3 text-center">
                  <div className="inline-flex items-center justify-center w-8 h-8 rounded-md bg-lab-surface3 text-lab-muted mb-2">
                    <Icon name={f.icon} />
                  </div>
                  <p className="text-xs font-semibold text-lab-fg">{f.title}</p>
                  <p className="text-[11px] text-lab-muted mt-0.5">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    };

    /* ─── Activity Feed (State B — Left Column) ─── */
    const ActivityFeed = ({ steps = [], logs = [], logsOpen = true, onToggleLogs }) => {
      const safeSteps = Array.isArray(steps) ? steps : [];
      const safeLogs = Array.isArray(logs) ? logs : [];

      const done = safeSteps.filter(s => s && s.status === 'done').length;
      const active = safeSteps.find(s => s && s.status === 'active');
      const progress = safeSteps.length > 0 ? ((done + 0.5) / safeSteps.length) * 100 : 0;

      return (
        <div className="bg-lab-surface border border-lab-border rounded-xl flex flex-col h-full">
          <div className="px-4 py-3 border-b border-lab-border flex items-center justify-between">
            <h3 className="text-sm font-semibold text-lab-fg flex items-center gap-2">
              <Icon name="Bot" className="text-lab-accent" />
              Agent Activity
            </h3>
            <span className="text-[11px] font-mono text-lab-muted bg-lab-surface2 px-2 py-0.5 rounded">{done}/{safeSteps.length} steps</span>
          </div>

          <div className="px-4 py-3 border-b border-lab-border">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-lab-muted">{active?.label || (done === safeSteps.length ? 'Complete' : 'Processing...')}</span>
              <span className="text-xs font-semibold text-lab-accent font-mono">{Math.round(progress)}%</span>
            </div>
            <div className="w-full h-2 bg-lab-surface3 rounded-full overflow-hidden">
              <div className="h-full bg-lab-accent rounded-full progress-animate" style={{ '--target-width': `${progress}%`, width: `${progress}%` }}></div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-3 space-y-1">
            {safeSteps.map((step, i) => (
              <div key={step.id || i} className="flex items-start gap-3 py-2 px-2 rounded-lg hover:bg-lab-surface2 transition-colors">
                <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                  step.status === 'done' ? 'bg-lab-accent/15 text-lab-accent' :
                  step.status === 'active' ? 'bg-amber-100 text-amber-600' :
                  'bg-lab-surface3 text-slate-400'
                }`}>
                  {step.status === 'done' ? <Icon name="Check" /> :
                   step.status === 'active' ? <span className="w-2 h-2 rounded-full bg-amber-500 pulse-dot"></span> :
                   <span className="text-[10px] font-mono">{i + 1}</span>}
                </div>
                <div className="min-w-0">
                  <p className={`text-xs leading-relaxed ${step.status === 'pending' ? 'text-slate-400' : 'text-lab-fg'}`}>{step.label}</p>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                    {step.status === 'done' ? 'Completed' : step.status === 'active' ? 'Running...' : 'Queued'}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-lab-border">
            <button
              onClick={onToggleLogs}
              className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-medium text-lab-muted hover:text-lab-fg hover:bg-lab-surface2 transition-colors"
            >
              <span className="flex items-center gap-2"><Icon name="Terminal" /> Raw Agent Logs ({safeLogs.length})</span>
              {logsOpen ? <Icon name="ChevronDown" /> : <Icon name="ChevronRight" />}
            </button>
            {logsOpen && (
              <div className="border-t border-lab-border bg-slate-900 max-h-52 overflow-y-auto scrollbar-thin fade-in-up">
                {safeLogs.length === 0 ? (
                  <div className="px-4 py-3 font-mono text-[11px] text-slate-500">Initializing agent logs...</div>
                ) : (
                  safeLogs.map((log, i) => (
                    <div key={i} className="px-4 py-1.5 font-mono text-[11px] leading-relaxed border-b border-white/5 flex gap-3">
                      <span className="text-slate-500 flex-shrink-0">{log.ts || ''}</span>
                      <span className={`flex-shrink-0 w-10 ${log.level === 'ok' ? 'text-emerald-400' : log.level === 'warn' ? 'text-amber-400' : 'text-slate-400'}`}>
                        {(log.level || 'info').toUpperCase()}
                      </span>
                      <span className="text-slate-300">{log.msg || ''}</span>
                    </div>
                  ))
                )}
                <div className="px-4 py-2 flex items-center gap-1.5">
                  <span className="w-1.5 h-3 bg-emerald-400 pulse-dot"></span>
                  <span className="text-[11px] text-emerald-400 font-mono">Agent active...</span>
                </div>
              </div>
            )}
          </div>
        </div>
      );
    };

    /* ─── Report Panel (State B — Right Column) ─── */
    /* ─── Report Panel (State B — Full Width Output Area) ─── */
    const ReportPanel = ({ topic, reportText, isDone, timestamp, steps = [], logs = [], onOpenLogs }) => {
      const activeStep = steps.find(s => s && s.status === 'active');
      const latestLog = logs.length > 0 ? logs[logs.length - 1] : null;

      const handleDownload = () => {
        const blob = new Blob([reportText || ''], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const cleanTitle = (topic || 'research_report').slice(0, 40).replace(/[^a-zA-Z0-9_-]/g, '_');
        a.download = `${cleanTitle}.md`;
        a.click();
        URL.revokeObjectURL(url);
      };

      const renderContent = () => {
        if (!reportText) {
          return (
            <div className="flex flex-col items-center justify-center py-16 px-4 text-center max-w-2xl mx-auto">
              <div className="relative mb-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                  <Icon name="Bot" className="w-8 h-8" />
                </div>
                <span className="absolute -bottom-1 -right-1 flex h-4 w-4">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2 border-white"></span>
                </span>
              </div>

              <h3 className="text-xl font-bold text-slate-800 tracking-tight">
                {activeStep ? activeStep.label : 'Agentic Research in Progress...'}
              </h3>
              <p className="text-sm text-slate-500 mt-2 max-w-md">
                Querying live web sources, verifying facts, and generating a structured report with comparison tables.
              </p>

              {/* Horizontal Multi-Agent Stepper */}
              <div className="w-full mt-8 grid grid-cols-2 sm:grid-cols-5 gap-3">
                {steps.map((s, idx) => (
                  <div key={idx} className="flex flex-col items-center text-center p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold mb-1.5 transition-all ${
                      s.status === 'done' ? 'bg-emerald-500 text-white shadow-sm' :
                      s.status === 'active' ? 'bg-indigo-600 text-white ring-4 ring-indigo-100 shadow-sm' :
                      'bg-slate-200 text-slate-500'
                    }`}>
                      {s.status === 'done' ? '✓' : idx + 1}
                    </div>
                    <span className={`text-[11px] leading-tight line-clamp-2 ${
                      s.status === 'done' ? 'text-slate-700 font-medium' :
                      s.status === 'active' ? 'text-indigo-600 font-bold' :
                      'text-slate-400'
                    }`}>
                      {s.label}
                    </span>
                  </div>
                ))}
              </div>

              {/* Live Activity Ticker Bar */}
              {latestLog && (
                <div className="mt-8 w-full bg-slate-900 text-slate-300 px-4 py-3 rounded-xl font-mono text-xs flex items-center justify-between gap-3 shadow-md">
                  <div className="flex items-center gap-2.5 truncate">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot flex-shrink-0"></span>
                    <span className="truncate">{latestLog.msg}</span>
                  </div>
                  {onOpenLogs && (
                    <button
                      onClick={onOpenLogs}
                      className="text-xs text-indigo-400 hover:text-indigo-300 underline font-sans flex-shrink-0"
                    >
                      View Logs
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        }

        if (window.marked) {
          return (
            <div
              className="prose prose-slate max-w-none text-slate-800 leading-relaxed text-sm sm:text-base"
              dangerouslySetInnerHTML={{ __html: window.marked.parse(reportText) }}
            />
          );
        }
        return <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700 leading-relaxed">{reportText}</pre>;
      };

      return (
        <div className="bg-lab-surface border border-lab-border rounded-xl flex flex-col h-full shadow-sm overflow-hidden">
          {/* Output Header */}
          <div className="px-6 py-3.5 border-b border-lab-border flex items-center justify-between flex-shrink-0 bg-white">
            <div className="min-w-0 flex-1 pr-4">
              <div className="flex items-center gap-2">
                <Icon name="FileText" className="text-indigo-600" />
                <h2 className="text-base font-bold text-slate-900 truncate">{topic || 'Research Synthesis Report'}</h2>
              </div>
              <p className="text-[11px] text-slate-500 font-mono mt-0.5">{timestamp || 'Live Multi-Agent Synthesis'}</p>
            </div>
            {reportText && (
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => navigator.clipboard.writeText(reportText || '')}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-lab-border text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
                >
                  <Icon name="Copy" /> Copy
                </button>
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-sm"
                >
                  <Icon name="Download" /> Download .md
                </button>
              </div>
            )}
          </div>

          {/* Full Width Body Content */}
          <div className="flex-1 overflow-y-auto scrollbar-thin px-6 sm:px-12 py-8 bg-white">
            <div className="max-w-5xl mx-auto w-full">
              {renderContent()}
            </div>
          </div>
        </div>
      );
    };

    /* ─── Research View (State B — Full Width Screen) ─── */
    const ResearchView = ({ onBack, topic, steps, logs, reportText, isDone, timestamp }) => {
      const [logsDrawerOpen, setLogsDrawerOpen] = useState(false);
      const safeSteps = Array.isArray(steps) ? steps : [];
      const safeLogs = Array.isArray(logs) ? logs : [];
      const done = safeSteps.filter(s => s && s.status === 'done').length;
      const active = safeSteps.find(s => s && s.status === 'active');
      const progress = safeSteps.length > 0 ? ((done + (isDone ? 0 : 0.5)) / safeSteps.length) * 100 : 0;

      return (
        <div className="flex-1 flex flex-col h-screen overflow-hidden bg-lab-bg relative">
          {/* Sub Header */}
          <div className="px-5 py-2.5 border-b border-lab-border bg-lab-surface flex items-center justify-between gap-3 flex-shrink-0">
            <div className="flex items-center gap-3 min-w-0">
              <button onClick={onBack} className="text-lab-muted hover:text-lab-fg transition-colors px-2.5 py-1 rounded-lg hover:bg-lab-surface2 flex items-center gap-1.5 text-xs font-medium border border-lab-border">
                <Icon name="ChevronLeft" /> New Search
              </button>
              <div className="h-4 w-px bg-lab-border"></div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${isDone ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
                  <span className={`w-2 h-2 rounded-full ${isDone ? 'bg-emerald-500' : 'bg-amber-500 pulse-dot'}`}></span>
                  {isDone ? 'Research Complete' : (active?.label || 'Research in Progress...')}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => setLogsDrawerOpen(!logsDrawerOpen)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  logsDrawerOpen 
                    ? 'bg-slate-900 text-white border-slate-900' 
                    : 'border-lab-border text-lab-muted hover:text-lab-fg hover:bg-lab-surface2'
                }`}
                title="View Agent Terminal Logs"
              >
                <Icon name="Terminal" />
                <span className="hidden sm:inline">Agent Logs</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-200 text-slate-700 font-mono font-semibold">{safeLogs.length}</span>
              </button>
            </div>
          </div>

          {/* Thin Progress Indicator */}
          {!isDone && (
            <div className="w-full h-1 bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-indigo-600 to-emerald-500 transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(10, progress))}%` }}
              ></div>
            </div>
          )}

          {/* Full-Width Main Output Canvas */}
          <div className="flex-1 p-4 md:p-6 min-h-0 overflow-hidden flex flex-col">
            <ReportPanel
              topic={topic}
              reportText={reportText}
              isDone={isDone}
              timestamp={timestamp}
              steps={safeSteps}
              logs={safeLogs}
              onOpenLogs={() => setLogsDrawerOpen(true)}
            />
          </div>

          {/* Optional Slide-out Activity & Logs Drawer */}
          {logsDrawerOpen && (
            <div className="fixed inset-y-0 right-0 w-full sm:w-[440px] bg-slate-950 text-slate-200 shadow-2xl border-l border-slate-800 z-50 flex flex-col fade-in-up">
              <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900">
                <div className="flex items-center gap-2">
                  <Icon name="Terminal" className="text-emerald-400" />
                  <span className="text-sm font-semibold text-white">Live Agent Activity</span>
                  <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                    {done}/{safeSteps.length}
                  </span>
                </div>
                <button
                  onClick={() => setLogsDrawerOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800"
                >
                  ✕
                </button>
              </div>

              {/* Progress Steps Inside Drawer */}
              <div className="p-4 border-b border-slate-800 space-y-2 bg-slate-900/50">
                {safeSteps.map((s, idx) => (
                  <div key={idx} className="flex items-center gap-2.5 text-xs">
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                      s.status === 'done' ? 'bg-emerald-500/20 text-emerald-400' :
                      s.status === 'active' ? 'bg-amber-500/20 text-amber-400' :
                      'bg-slate-800 text-slate-500'
                    }`}>
                      {s.status === 'done' ? '✓' : s.status === 'active' ? '●' : idx + 1}
                    </span>
                    <span className={s.status === 'done' ? 'text-slate-300' : s.status === 'active' ? 'text-amber-300 font-medium' : 'text-slate-500'}>
                      {s.label}
                    </span>
                  </div>
                ))}
              </div>

              {/* Console Logs */}
              <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] space-y-2">
                {safeLogs.map((l, i) => (
                  <div key={i} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-slate-600 flex-shrink-0">{l.ts}</span>
                    <span className={`flex-shrink-0 uppercase font-semibold ${
                      l.level === 'ok' ? 'text-emerald-400' : l.level === 'warn' ? 'text-amber-400' : 'text-cyan-400'
                    }`}>[{l.level || 'info'}]</span>
                    <span className="text-slate-300">{l.msg}</span>
                  </div>
                ))}
                {!isDone && (
                  <div className="flex items-center gap-2 text-emerald-400 pt-2">
                    <span className="w-1.5 h-3 bg-emerald-400 pulse-dot"></span>
                    <span>Multi-agent pipeline running...</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      );
    };

    const INITIAL_STEPS = [
      { id: 1, label: 'Initializing agent and search parameters', status: 'pending' },
      { id: 2, label: 'Searching Google for latest information', status: 'pending' },
      { id: 3, label: 'Synthesizing findings into report', status: 'pending' },
      { id: 4, label: 'Citing sources and formatting', status: 'pending' },
      { id: 5, label: 'Final review and quality check', status: 'pending' },
    ];

    /* ─── App ─── */
    const App = () => {
      const [view, setView] = useState('search');
      const [history, setHistory] = useState(HISTORY);
      const [activeHistory, setActiveHistory] = useState(null);
      const [sidebarOpen, setSidebarOpen] = useState(false);
      const [currentQuery, setCurrentQuery] = useState('');

      const [steps, setSteps] = useState(INITIAL_STEPS);
      const [logs, setLogs] = useState([]);
      const [reportText, setReportText] = useState('');
      const [isDone, setIsDone] = useState(false);
      const [timestamp, setTimestamp] = useState('');

      const handleStart = (params) => {
        const query = params.query;
        setCurrentQuery(query);
        setView('research');
        setSteps(INITIAL_STEPS);
        setLogs([{ ts: new Date().toLocaleTimeString(), level: 'info', msg: `Initiated research query: "${query}"` }]);
        setReportText('');
        setIsDone(false);

        const newItem = {
          id: Date.now(),
          title: query.slice(0, 50),
          time: 'Just now',
          snippet: `Depth: ${params.depth === 'deep' ? 'Deep Dive' : 'Quick Brief'}...`,
        };
        setHistory(h => [newItem, ...h]);
        setActiveHistory(newItem.id);

        // Connect to SSE Endpoint /api/research/stream
        if (window.EventSource) {
          const sseUrl = `/api/research/stream?query=${encodeURIComponent(query)}&depth=${params.depth}`;
          const eventSource = new EventSource(sseUrl);

          eventSource.addEventListener('step_update', (e) => {
            const data = JSON.parse(e.data);
            setSteps(prev => prev.map(s => s.id === data.step_id ? { ...s, status: data.status, label: data.label || s.label } : s));
          });

          eventSource.addEventListener('log', (e) => {
            const data = JSON.parse(e.data);
            setLogs(prev => [...prev, data]);
          });

          eventSource.addEventListener('complete', (e) => {
            const data = JSON.parse(e.data);
            setReportText(data.report);
            setTimestamp(data.timestamp);
            setIsDone(true);
            eventSource.close();
          });

          eventSource.onerror = (err) => {
            console.warn("SSE error, falling back to POST REST endpoint", err);
            eventSource.close();
            fetchFallback(params);
          };
        } else {
          fetchFallback(params);
        }
      };

      const fetchFallback = async (params) => {
        try {
          const res = await fetch('/api/research', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
          });
          const data = await res.json();
          if (data.status === 'success' || data.report) {
            setReportText(data.report || 'No content generated.');
            setTimestamp(data.timestamp || 'Just now');
            setIsDone(true);
          } else {
            setReportText(`### Error\n\n${data.detail || 'Failed to complete research.'}`);
            setIsDone(true);
          }
        } catch (err) {
          setLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), level: 'warn', msg: `Error: ${err.message}` }]);
          setReportText(`### Error\n\nUnable to connect to backend: ${err.message}`);
          setIsDone(true);
        }
      };

      useEffect(() => {
        if (window.lucide) window.lucide.createIcons();
      });

      return (
        <div className="flex h-screen bg-lab-bg overflow-hidden">
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            history={history}
            activeId={activeHistory}
            onSelect={(id) => { setActiveHistory(id); }}
          />

          {sidebarOpen && (
            <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={() => setSidebarOpen(false)}></div>
          )}

          <div className="flex-1 flex flex-col min-w-0">
            <header className="h-14 border-b border-lab-border bg-lab-surface flex items-center px-4 gap-3 flex-shrink-0">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-lab-muted hover:text-lab-fg p-1"
              >
                <Icon name="MoreHorizontal" />
              </button>
              <div className="flex-1 flex items-center gap-3">
                {view === 'search' ? (
                  <>
                    <div className="w-7 h-7 rounded-md bg-lab-accent/15 flex items-center justify-center text-lab-accent"><Icon name="Bot" /></div>
                    <span className="text-sm font-semibold text-lab-fg">New Research</span>
                  </>
                ) : (
                  <div className="flex items-center gap-2 text-sm text-lab-muted">
                    <span className="text-slate-400">Researching:</span>
                    <span className="font-medium text-lab-fg">{currentQuery}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex items-center gap-2 text-[11px] font-mono text-lab-muted bg-lab-surface2 px-2.5 py-1 rounded-md border border-lab-border">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  Agent online
                </div>
              </div>
            </header>

            {view === 'search' ? (
              <SearchView onStart={handleStart} />
            ) : (
              <ResearchView
                onBack={() => setView('search')}
                topic={currentQuery}
                steps={steps}
                logs={logs}
                reportText={reportText}
                isDone={isDone}
                timestamp={timestamp}
              />
            )}
          </div>
        </div>
      );
    };

    class ErrorBoundary extends React.Component {
      constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
      }

      static getDerivedStateFromError(error) {
        return { hasError: true, error };
      }

      componentDidCatch(error, errorInfo) {
        console.error("React Error Boundary caught an error:", error, errorInfo);
      }

      render() {
        if (this.state.hasError) {
          return (
            <div className="flex flex-col items-center justify-center h-screen bg-lab-bg p-6 text-center">
              <div className="w-16 h-16 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mb-4 text-2xl font-bold">⚠️</div>
              <h2 className="text-xl font-bold text-slate-800">Research View Error</h2>
              <p className="text-sm text-slate-600 mt-2 max-w-md">{this.state.error?.toString()}</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-6 px-4 py-2 bg-lab-accent text-white text-sm font-semibold rounded-lg hover:bg-lab-accent-hover transition-colors"
              >
                Reload App
              </button>
            </div>
          );
        }
        return this.props.children;
      }
    }

    ReactDOM.createRoot(document.getElementById('root')).render(
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    );
  </script>
</body>
</html>