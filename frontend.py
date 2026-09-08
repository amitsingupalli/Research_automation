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

            <div className="bg-lab-surface rounded-xl border border-lab-border shadow-sm">
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-lab-muted"><Icon name="Search" /></div>
                <input
                  type="text"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="e.g. Latest advances in transformer efficiency..."
                  className="w-full pl-12 pr-4 py-4 bg-transparent text-lab-fg placeholder:text-slate-400 focus:outline-none text-sm rounded-t-xl"
                />
              </div>

              <div className="border-t border-lab-border px-4 py-3 space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-medium text-lab-muted">Research Depth</span>
                  <div className="flex bg-lab-surface2 rounded-lg p-0.5 border border-lab-border">
                    <button
                      onClick={() => setDepth('quick')}
                      className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${depth === 'quick' ? 'bg-lab-surface shadow-sm text-lab-fg' : 'text-lab-muted hover:text-lab-fg'}`}
                    >
                      ⚡ Quick Brief
                    </button>
                    <button
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
                  onClick={() => query.trim() && onStart({ query, depth, sources })}
                  disabled={!query.trim()}
                  className="w-full py-2.5 rounded-lg bg-lab-accent hover:bg-lab-accent-hover disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors flex items-center justify-center gap-2"
                >
                  <Icon name="Play" className="w-4 h-4" /> Start Research
                </button>
              </div>
            </div>

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
    const ActivityFeed = ({ steps, logsOpen, onToggleLogs }) => {
      const done = steps.filter(s => s.status === 'done').length;
      const active = steps.find(s => s.status === 'active');
      const progress = ((done + 0.5) / steps.length) * 100;

      return (
        <div className="bg-lab-surface border border-lab-border rounded-xl flex flex-col h-full">
          <div className="px-4 py-3 border-b border-lab-border flex items-center justify-between">
            <h3 className="text-sm font-semibold text-lab-fg flex items-center gap-2">
              <Icon name="Bot" className="text-lab-accent" />
              Agent Activity
            </h3>
            <span className="text-[11px] font-mono text-lab-muted bg-lab-surface2 px-2 py-0.5 rounded">{done}/{steps.length} steps</span>
          </div>

          <div className="px-4 py-3 border-b border-lab-border">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-lab-muted">{active?.label || 'Complete'}</span>
              <span className="text-xs font-semibold text-lab-accent font-mono">{Math.round(progress)}%</span>
            </div>
            <div className="w-full h-2 bg-lab-surface3 rounded-full overflow-hidden">
              <div className="h-full bg-lab-accent rounded-full progress-animate" style={{ '--target-width': `${progress}%`, width: `${progress}%` }}></div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-3 space-y-1">
            {steps.map((step, i) => (
              <div key={step.id} className="flex items-start gap-3 py-2 px-2 rounded-lg hover:bg-lab-surface2 transition-colors">
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
              <span className="flex items-center gap-2"><Icon name="Terminal" /> Raw Agent Logs</span>
              {logsOpen ? <Icon name="ChevronDown" /> : <Icon name="ChevronRight" />}
            </button>
            {logsOpen && (
              <div className="border-t border-lab-border bg-slate-900 max-h-52 overflow-y-auto scrollbar-thin fade-in-up">
                {logs.map((log, i) => (
                  <div key={i} className="px-4 py-1.5 font-mono text-[11px] leading-relaxed border-b border-white/5 flex gap-3">
                    <span className="text-slate-500 flex-shrink-0">{log.ts}</span>
                    <span className={`flex-shrink-0 w-10 ${log.level === 'ok' ? 'text-emerald-400' : log.level === 'warn' ? 'text-amber-400' : 'text-slate-400'}`}>
                      {log.level.toUpperCase()}
                    </span>
                    <span className="text-slate-300">{log.msg}</span>
                  </div>
                ))}
                <div className="px-4 py-2 flex items-center gap-1.5">
                  <span className="w-1.5 h-3 bg-emerald-400 pulse-dot"></span>
                  <span className="text-[11px] text-emerald-400 font-mono">Waiting for next tool call...</span>
                </div>
              </div>
            )}
          </div>
        </div>
      );
    };

    /* ─── Report Panel (State B — Right Column) ─── */
    const ReportPanel = ({ topic }) => {
      const [showSources, setShowSources] = useState(true);

      return (
        <div className="bg-lab-surface border border-lab-border rounded-xl flex flex-col h-full">
          <div className="px-5 py-3 border-b border-lab-border flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-lab-fg">{topic || 'Transformer Benchmark Analysis'}</h3>
              <p className="text-[11px] text-lab-muted font-mono mt-0.5">Generated Sep 8, 2026 · 4 sources · 1,247 words</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium border border-lab-border text-lab-muted hover:text-lab-fg hover:border-slate-300 transition-colors">
                <Icon name="Copy" /> Markdown
              </button>
              <button className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-lab-surface2 border border-lab-border text-lab-fg hover:bg-lab-surface3 transition-colors">
                <Icon name="Download" /> PDF
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin px-5 py-5">
            <div className="max-w-none">
              <h4 className="text-lg font-bold text-lab-fg mb-3">Executive Summary</h4>
              <p className="text-sm text-slate-600 leading-relaxed mb-5">
                Transformer efficiency has improved dramatically over the past 12 months. New architectures like
                <strong> Mixture-of-Depths</strong> and <strong>Native Sparse Attention</strong> have reduced inference
                costs by 40–60% while maintaining or improving benchmark performance across GLUE, MMLU, and HumanEval.
                The most significant shift is toward compute-optimal training at scale, challenging the "bigger is always better" paradigm.
              </p>

              <h4 className="text-lg font-bold text-lab-fg mb-3">Key Findings</h4>
              <div className="grid gap-3 mb-5">
                {[
                  { stat: '42%', label: 'Reduction in inference cost using MoD vs dense baselines (arXiv 2501.12345)' },
                  { stat: '94.2%', label: 'MMLU accuracy achieved by compute-optimal 7B model, matching 70B dense baseline' },
                  { stat: '3.1x', label: 'Throughput improvement with Native Sparse Attention on long-context tasks' },
                ].map((f, i) => (
                  <div key={i} className="bg-lab-surface3 border border-lab-border rounded-lg px-4 py-3 flex items-start gap-3">
                    <span className="text-lg font-bold text-lab-accent font-mono flex-shrink-0">{f.stat}</span>
                    <span className="text-xs text-slate-600 leading-relaxed pt-0.5">{f.label}</span>
                  </div>
                ))}
              </div>

              <h4 className="text-lg font-bold text-lab-fg mb-3">Detailed Analysis</h4>
              <p className="text-sm text-slate-600 leading-relaxed mb-3">
                The transformer landscape in 2025 is defined by three converging trends: architectural sparsity,
                compute-optimal scaling, and inference-time optimization. Mixture-of-Depths (MoD) models dynamically
                allocate compute per token, routing easy tokens through smaller sub-networks while reserving full-model
                capacity for complex reasoning <sup className="text-lab-accent cursor-pointer">[1]</sup>.
              </p>
              <p className="text-sm text-slate-600 leading-relaxed mb-5">
                Native Sparse Attention extends this principle to the attention mechanism itself, reducing the quadratic
                complexity of self-attention to near-linear for sequences beyond 128K tokens <sup className="text-lab-accent cursor-pointer">[2]</sup>.
                Meanwhile, the Chinchilla-optimal training regime has been validated at scale, with models trained on
                4–8x more tokens than their parameter count suggesting achieving superior performance <sup className="text-lab-accent cursor-pointer">[3]</sup>.
              </p>

              <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 mb-5">
                <p className="text-xs font-semibold text-amber-800 mb-1">⚠ Caveat</p>
                <p className="text-xs text-amber-700 leading-relaxed">
                  Benchmark saturation remains a concern. Several researchers note that MMLU and HumanEval may no longer
                  differentiate frontier models meaningfully. New evaluations like GAIA and SWE-bench are gaining traction.
                </p>
              </div>

              <h4 className="text-lg font-bold text-lab-fg mb-3">Cited Sources</h4>
              <div className="space-y-2">
                {SOURCES.map((src, i) => (
                  <div key={i} className="flex items-start gap-3 px-3 py-2.5 rounded-lg border border-lab-border hover:border-slate-300 transition-colors cursor-pointer group">
                    <span className="text-lg mt-0.5">{src.favicon}</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-lab-accent bg-lab-accent/10 px-1.5 py-0.5 rounded">[{i + 1}]</span>
                        <p className="text-xs font-semibold text-lab-fg line-clamp-1">{src.title}</p>
                        <span className="text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity"><Icon name="ArrowUpRight" /></span>
                      </div>
                      <p className="text-[11px] text-lab-muted mt-0.5 line-clamp-1">{src.domain} — {src.snippet}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    };

    /* ─── Research View (State B) ─── */
    const ResearchView = ({ onBack, topic }) => {
      const [logsOpen, setLogsOpen] = useState(false);

      return (
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <div className="px-4 py-2 border-b border-lab-border bg-lab-surface flex items-center gap-3">
            <button onClick={onBack} className="text-lab-muted hover:text-lab-fg transition-colors p-1 rounded-md hover:bg-lab-surface2">
              <Icon name="ChevronLeft" />
            </button>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-[10px] font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 pulse-dot"></span>
                  Research in Progress
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-lab-muted">
              <Icon name="Clock" className="w-3.5 h-3.5" />
              <span className="font-mono">14:32 · 42s elapsed</span>
            </div>
          </div>

          <div className="flex-1 flex gap-4 p-4 min-h-0">
            <div className="w-[42%] min-w-0">
              <ActivityFeed steps={REPORT_STEPS} logsOpen={logsOpen} onToggleLogs={() => setLogsOpen(o => !o)} />
            </div>
            <div className="flex-1 min-w-0">
              <ReportPanel topic={topic} />
            </div>
          </div>
        </div>
      );
    };

    /* ─── App ─── */
    const App = () => {
      const [view, setView] = useState('search');
      const [history, setHistory] = useState(HISTORY);
      const [activeHistory, setActiveHistory] = useState(null);
      const [sidebarOpen, setSidebarOpen] = useState(false);
      const [currentQuery, setCurrentQuery] = useState('');

      const handleStart = (params) => {
        setCurrentQuery(params.query);
        setView('research');
        const newItem = {
          id: Date.now(),
          title: params.query.slice(0, 50),
          time: 'Just now',
          snippet: `Depth: ${params.depth === 'deep' ? 'Deep Dive' : 'Quick Brief'}...`,
        };
        setHistory(h => [newItem, ...h]);
        setActiveHistory(newItem.id);
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
              <ResearchView onBack={() => setView('search')} topic={currentQuery} />
            )}
          </div>
        </div>
      );
    };

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>