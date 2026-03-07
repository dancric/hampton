"""
display.py - Export simulation results to a self-contained HTML file.
"""

import json
from pathlib import Path

from dataclasses import asdict

from .agent import AgentList
from .api import AgentAction
from .gamestate import GameState


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hampton Simulation</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg: #f0f2f5;
            --card-bg: #ffffff;
            --text: #1a1a2e;
            --text-muted: #6b7280;
            --border: #e5e7eb;
            --accent: #3b82f6;
            --radius: 10px;
            --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
            --shadow-lg: 0 4px 12px rgba(0,0,0,0.1);

            --color-mayor: #dc2626;
            --color-rep: #2563eb;
            --color-ceo: #7c3aed;
            --color-substacker: #ea580c;
            --color-union: #16a34a;
            --color-admiral: #0891b2;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }

        #app {
            max-width: 820px;
            margin: 0 auto;
            padding: 24px 16px 60px;
        }

        /* Header */
        header {
            text-align: center;
            margin-bottom: 28px;
        }
        header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .subtitle {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 4px;
        }

        /* Tab bar */
        .tab-bar {
            display: flex;
            gap: 4px;
            background: var(--card-bg);
            border-radius: var(--radius);
            padding: 4px;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
        }
        .tab-btn {
            flex: 1;
            padding: 10px 16px;
            border: none;
            background: transparent;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab-btn:hover { background: var(--bg); }
        .tab-btn.active {
            background: var(--accent);
            color: #fff;
            box-shadow: 0 1px 4px rgba(59,130,246,0.3);
        }

        /* Filter bar (character view) */
        .filter-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .char-btn {
            padding: 6px 14px;
            border: 2px solid var(--border);
            background: var(--card-bg);
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .char-btn:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
        .char-btn.active { color: #fff; border-color: transparent; }

        /* Cards */
        .card {
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 16px 20px;
            margin-bottom: 12px;
            border-left: 4px solid var(--border);
            transition: box-shadow 0.2s;
        }
        .card:hover { box-shadow: var(--shadow-lg); }

        .card--mayor    { border-left-color: var(--color-mayor); }
        .card--rep      { border-left-color: var(--color-rep); }
        .card--ceo      { border-left-color: var(--color-ceo); }
        .card--substacker { border-left-color: var(--color-substacker); }
        .card--union    { border-left-color: var(--color-union); }
        .card--admiral  { border-left-color: var(--color-admiral); }

        /* Sent / received styling in character view */
        .card--sent {
            margin-left: 0;
            margin-right: 40px;
        }
        .card--received {
            margin-left: 40px;
            margin-right: 0;
            background: #f8fafc;
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .speaker {
            font-weight: 700;
            font-size: 0.95rem;
        }
        .arrow {
            color: var(--text-muted);
            font-size: 0.85rem;
        }
        .targets {
            color: var(--text-muted);
            font-size: 0.85rem;
        }
        .turn-num {
            margin-left: auto;
            font-size: 0.75rem;
            color: var(--text-muted);
            background: var(--bg);
            padding: 2px 8px;
            border-radius: 10px;
        }

        .message {
            font-size: 0.92rem;
            line-height: 1.7;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Reasoning toggle */
        .reasoning {
            margin-top: 12px;
            border-top: 1px solid var(--border);
            padding-top: 8px;
        }
        .reasoning summary {
            font-size: 0.8rem;
            color: var(--text-muted);
            cursor: pointer;
            user-select: none;
            font-weight: 500;
            padding: 4px 0;
        }
        .reasoning summary:hover { color: var(--accent); }
        .reasoning p {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 6px;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        /* Chart cards */
        .chart-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        .chart-card {
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 16px;
        }
        .chart-card:hover { box-shadow: var(--shadow-lg); }
        .chart-card h3 {
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text);
        }
        .chart-card canvas {
            width: 100%;
            height: 180px;
        }
        .chart-card .chart-range {
            display: flex;
            justify-content: space-between;
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 4px;
        }
        @media (max-width: 600px) {
            .chart-grid { grid-template-columns: 1fr; }
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            color: var(--text-muted);
            padding: 40px 20px;
            font-size: 0.95rem;
        }

        /* Responsive */
        @media (max-width: 600px) {
            #app { padding: 16px 10px 40px; }
            header h1 { font-size: 1.35rem; }
            .card--sent { margin-right: 16px; }
            .card--received { margin-left: 16px; }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <h1 id="page-title"></h1>
            <p class="subtitle" id="action-count"></p>
        </header>

        <nav class="tab-bar">
            <button class="tab-btn active" data-tab="timeline" onclick="switchTab('timeline')">
                Full Timeline
            </button>
            <button class="tab-btn" data-tab="character" onclick="switchTab('character')">
                By Character
            </button>
            <button class="tab-btn" data-tab="gamestate" onclick="switchTab('gamestate')">
                Game State
            </button>
        </nav>

        <section id="timeline-view">
            <div id="timeline-cards"></div>
        </section>

        <section id="character-view" style="display:none">
            <div class="filter-bar" id="filter-bar"></div>
            <div id="character-cards"></div>
        </section>

        <section id="gamestate-view" style="display:none">
            <div class="chart-grid" id="chart-grid"></div>
        </section>
    </div>

    <script>
        const DATA = __DATA_JSON__;

        /* --- Utilities --- */

        function escapeHtml(text) {
            var el = document.createElement('span');
            el.textContent = text;
            return el.innerHTML;
        }

        function speakerColor(title) {
            return 'var(--color-' + title + ')';
        }

        /* --- Tab switching --- */

        function switchTab(tab) {
            document.getElementById('timeline-view').style.display =
                tab === 'timeline' ? 'block' : 'none';
            document.getElementById('character-view').style.display =
                tab === 'character' ? 'block' : 'none';
            document.getElementById('gamestate-view').style.display =
                tab === 'gamestate' ? 'block' : 'none';
            document.querySelectorAll('.tab-btn').forEach(function(btn) {
                btn.classList.toggle('active', btn.dataset.tab === tab);
            });
            if (tab === 'gamestate' && !chartsRendered) renderCharts();
        }

        /* --- Card creation --- */

        function createCard(action, mode) {
            var card = document.createElement('div');
            var cls = 'card card--' + action.speaker;
            if (mode === 'sent') cls += ' card--sent';
            if (mode === 'received') cls += ' card--received';
            card.className = cls;

            var headerHtml =
                '<div class="card-header">' +
                    '<span class="speaker" style="color:' + speakerColor(action.speaker) + '">' +
                        escapeHtml(action.speakerName) +
                    '</span>' +
                    '<span class="arrow">&rarr;</span>' +
                    '<span class="targets">' + action.targetNames.map(escapeHtml).join(', ') + '</span>' +
                    '<span class="turn-num">#' + (action.index + 1) + '</span>' +
                '</div>';

            var bodyHtml =
                '<div class="card-body">' +
                    '<p class="message">' + escapeHtml(action.message) + '</p>' +
                '</div>';

            var reasoningHtml =
                '<details class="reasoning">' +
                    '<summary>Show reasoning</summary>' +
                    '<p>' + escapeHtml(action.reasoning) + '</p>' +
                '</details>';

            card.innerHTML = headerHtml + bodyHtml + reasoningHtml;
            return card;
        }

        /* --- Timeline view --- */

        function renderTimeline() {
            var container = document.getElementById('timeline-cards');
            container.innerHTML = '';
            if (DATA.actions.length === 0) {
                container.innerHTML = '<div class="empty-state">No actions to display.</div>';
                return;
            }
            DATA.actions.forEach(function(action) {
                container.appendChild(createCard(action, 'timeline'));
            });
        }

        /* --- Character view --- */

        var activeCharacter = null;

        function renderCharacterView(title) {
            activeCharacter = title;
            var container = document.getElementById('character-cards');
            container.innerHTML = '';

            document.querySelectorAll('.char-btn').forEach(function(btn) {
                btn.classList.toggle('active', btn.dataset.title === title);
            });

            var relevant = DATA.actions.filter(function(a) {
                return a.speaker === title || a.targets.indexOf(title) !== -1;
            });

            if (relevant.length === 0) {
                container.innerHTML = '<div class="empty-state">No conversations involving this character.</div>';
                return;
            }

            relevant.forEach(function(action) {
                var mode = action.speaker === title ? 'sent' : 'received';
                container.appendChild(createCard(action, mode));
            });
        }

        function buildFilterBar() {
            var bar = document.getElementById('filter-bar');
            var titles = Object.keys(DATA.characters);
            titles.forEach(function(title) {
                var btn = document.createElement('button');
                btn.className = 'char-btn';
                btn.dataset.title = title;
                btn.textContent = DATA.characters[title];
                btn.onclick = function() { renderCharacterView(title); };
                bar.appendChild(btn);
            });

            /* Dynamic active-state styles per character color */
            var style = document.createElement('style');
            var rules = '';
            titles.forEach(function(title) {
                rules += '.char-btn.active[data-title="' + title + '"]{' +
                    'background:var(--color-' + title + ');' +
                    'border-color:var(--color-' + title + ');' +
                    'color:#fff;}';
            });
            style.textContent = rules;
            document.head.appendChild(style);
        }

        /* --- Chart rendering --- */

        var chartsRendered = false;

        var CHART_LABELS = {
            contracts: 'Contracts',
            repairs: 'Repairs',
            employees: 'Employees',
            mayor_reelection: 'Mayor Reelection Prob',
            mayor_likability: 'Mayor Likability',
            rep_reelection: 'Rep Reelection Prob',
            rep_likability: 'Rep Likability',
            ceo_stock: 'Stock Price',
            substack_subs: 'Substack Subscribers',
            union_rate: 'Union Rate',
            admiral_passage: 'Admiral Passage Prob',
            admiral_likability: 'Admiral Likability',
            mayor_funds: 'Mayor Funds',
            rep_funds: 'Rep Funds',
            ceo_funds: 'CEO Funds',
            union_funds: 'Union Funds'
        };

        function drawChart(canvas, values, label) {
            var ctx = canvas.getContext('2d');
            var dpr = window.devicePixelRatio || 1;
            var rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            ctx.scale(dpr, dpr);

            var w = rect.width;
            var h = rect.height;
            var pad = { top: 10, right: 12, bottom: 24, left: 50 };
            var plotW = w - pad.left - pad.right;
            var plotH = h - pad.top - pad.bottom;

            var min = Math.min.apply(null, values);
            var max = Math.max.apply(null, values);
            if (min === max) { min -= 1; max += 1; }
            var range = max - min;

            /* Background */
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, w, h);

            /* Grid lines */
            ctx.strokeStyle = '#f0f0f0';
            ctx.lineWidth = 1;
            for (var g = 0; g <= 4; g++) {
                var gy = pad.top + plotH - (g / 4) * plotH;
                ctx.beginPath();
                ctx.moveTo(pad.left, gy);
                ctx.lineTo(pad.left + plotW, gy);
                ctx.stroke();
            }

            /* Y-axis labels */
            ctx.fillStyle = '#6b7280';
            ctx.font = '10px -apple-system, sans-serif';
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            for (var g = 0; g <= 4; g++) {
                var val = min + (g / 4) * range;
                var gy = pad.top + plotH - (g / 4) * plotH;
                var label_text = val >= 1000000 ? (val / 1000000).toFixed(1) + 'M' :
                                 val >= 1000 ? (val / 1000).toFixed(1) + 'K' :
                                 val % 1 === 0 ? val.toFixed(0) : val.toFixed(2);
                ctx.fillText(label_text, pad.left - 6, gy);
            }

            /* X-axis labels */
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            for (var i = 0; i < values.length; i++) {
                var x = pad.left + (values.length === 1 ? plotW / 2 : (i / (values.length - 1)) * plotW);
                ctx.fillText(i === 0 ? 'Start' : 'S' + i, x, pad.top + plotH + 6);
            }

            /* Data line */
            if (values.length < 2) return;
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2.5;
            ctx.lineJoin = 'round';
            ctx.beginPath();
            for (var i = 0; i < values.length; i++) {
                var x = pad.left + (i / (values.length - 1)) * plotW;
                var y = pad.top + plotH - ((values[i] - min) / range) * plotH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            /* Data points */
            ctx.fillStyle = '#3b82f6';
            for (var i = 0; i < values.length; i++) {
                var x = pad.left + (i / (values.length - 1)) * plotW;
                var y = pad.top + plotH - ((values[i] - min) / range) * plotH;
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function renderCharts() {
            chartsRendered = true;
            var grid = document.getElementById('chart-grid');
            grid.innerHTML = '';

            if (!DATA.states || DATA.states.length === 0) {
                grid.innerHTML = '<div class="empty-state">No game state data available.</div>';
                return;
            }

            var keys = Object.keys(DATA.states[0]);
            keys.forEach(function(key) {
                var values = DATA.states.map(function(s) { return s[key]; });

                var card = document.createElement('div');
                card.className = 'chart-card';

                var title = document.createElement('h3');
                title.textContent = CHART_LABELS[key] || key;
                card.appendChild(title);

                var canvas = document.createElement('canvas');
                canvas.style.width = '100%';
                canvas.style.height = '180px';
                card.appendChild(canvas);

                var rangeDiv = document.createElement('div');
                rangeDiv.className = 'chart-range';
                var first = values[0];
                var last = values[values.length - 1];
                var fmt = function(v) {
                    return v >= 1000000 ? (v/1000000).toFixed(1)+'M' :
                           v >= 1000 ? (v/1000).toFixed(1)+'K' :
                           v % 1 === 0 ? v.toString() : v.toFixed(2);
                };
                rangeDiv.innerHTML = '<span>Start: ' + fmt(first) + '</span><span>Latest: ' + fmt(last) + '</span>';
                card.appendChild(rangeDiv);

                grid.appendChild(card);

                /* Draw after append so canvas has layout dimensions */
                requestAnimationFrame(function() { drawChart(canvas, values, key); });
            });
        }

        /* --- Init --- */

        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('page-title').textContent = DATA.title;
            document.getElementById('action-count').textContent =
                DATA.actions.length + ' conversation actions';

            renderTimeline();
            buildFilterBar();

            var firstTitle = Object.keys(DATA.characters)[0];
            if (firstTitle) renderCharacterView(firstTitle);
        });
    </script>
</body>
</html>"""


def export_html(
    agents: AgentList,
    actions: list[AgentAction],
    states: list[GameState],
    output_path: str | Path = "hampton_results.html",
    title: str = "Hampton Simulation Results",
) -> Path:
    """
    Export simulation results to a self-contained HTML file.

    Args:
        agents: The list of Agent objects (used to build title -> name mapping).
        actions: Ordered list of AgentActions with speaker field populated.
        states: Ordered list of GameState snapshots (index 0 = start, 1 = after scene 1, etc.).
        output_path: Where to write the HTML file.
        title: Page title shown in the browser tab and header.

    Returns:
        The Path to the written file.
    """
    characters = {
        agent.character.title: agent.character.name
        for agent in agents
    }

    action_data = [
        {
            "index": i,
            "speaker": a.speaker,
            "speakerName": characters.get(a.speaker, a.speaker),
            "targets": a.targets,
            "targetNames": [characters.get(t, t) for t in a.targets],
            "message": a.message,
            "reasoning": a.reasoning,
        }
        for i, a in enumerate(actions)
    ]

    states_data = [asdict(s) for s in states]

    data_json = json.dumps({
        "title": title,
        "characters": characters,
        "actions": action_data,
        "states": states_data,
    })

    # Escape </ sequences to prevent breaking out of the script tag
    data_json = data_json.replace("</", "<\\/")

    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)

    out = Path(output_path)
    out.write_text(html, encoding="utf-8")
    return out.resolve()
