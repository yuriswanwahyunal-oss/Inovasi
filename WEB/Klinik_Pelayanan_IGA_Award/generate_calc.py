import os, re, json

md_path = r"d:\Brida\IGA\2026\ANTI\SATUAN INOVASI DAERAH.md"
base_dir = r"d:\Brida\IGA\2026\ANTI\WEB\Klinik_Pelayanan_IGA_Award"

def generate():
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    indicators = []
    parsed_ids = set()
    for line in md_text.split('\n'):
        if not line.startswith('|'): continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) >= 8:
            num_raw = cells[0].replace('*','').replace('\\','').strip()
            if not num_raw.isdigit(): continue
            num = int(num_raw)
            if num < 16 or num > 35: continue
            if num in parsed_ids: continue
            parsed_ids.add(num)
            name = cells[2].replace('**','').strip()
            bobot_str = cells[4].replace('**','').replace(',','.').strip()
            try: bobot = float(bobot_str)
            except: continue
            variabel = cells[1].replace('**','').strip()
            def clean(t):
                t = re.sub(r'<br>.*', '', t).replace('**','').strip()
                return t[:90]+"..." if len(t)>90 else t
            indicators.append({
                "id": num, "name": name, "bobot": bobot, "variabel": variabel,
                "p1": clean(cells[5]), "p2": clean(cells[6]), "p3": clean(cells[7])
            })

    total_bobot = sum(i["bobot"] for i in indicators)
    max_score = int(total_bobot * 3)
    js_data = json.dumps(indicators, indent=2, ensure_ascii=False)
    print(f"Parsed {len(indicators)} indikator, Max: {max_score}")

    html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kalkulator Skor IGA Award</title>
<link rel="stylesheet" href="style.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
<style>
body { background: linear-gradient(160deg, #E0F2FE 0%, #F0F9FF 30%, #F8FAFC 60%, #ECFDF5 100%); min-height: 100vh; }

.calc-page {
    padding: calc(60px + 1.5rem) 1rem 3rem;
    max-width: 580px; margin: 0 auto;
}

/* ===== SCORE HERO ===== */
.score-hero {
    text-align: center; padding: 1.5rem 0 1.25rem;
}
.score-hero-label {
    font-size: 0.7rem; font-weight: 700; color: var(--text-light);
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.25rem;
}

.big-ring {
    position: relative; width: 150px; height: 150px; margin: 0 auto 1.25rem;
}
.big-ring svg { transform: rotate(-90deg); width: 150px; height: 150px; }
.big-ring .track { fill: none; stroke: #E2E8F0; stroke-width: 8; }
.big-ring .progress {
    fill: none; stroke: var(--accent-1); stroke-width: 8; stroke-linecap: round;
    transition: stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1), stroke 0.5s ease;
}
.big-ring .center-text {
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.big-ring .score-num {
    font-size: 2.5rem; font-weight: 800; color: var(--text-dark);
    line-height: 1; letter-spacing: -0.03em;
}
.big-ring .score-max {
    font-size: 0.75rem; color: var(--text-light); margin-top: 0.2rem; font-weight: 500;
}

.score-stats {
    display: flex; justify-content: center; gap: 1.75rem;
}
.stat-item { text-align: center; }
.stat-item .stat-val { font-size: 1.25rem; font-weight: 700; color: var(--text-dark); }
.stat-item .stat-label {
    font-size: 0.6rem; color: var(--text-light);
    text-transform: uppercase; letter-spacing: 0.06em;
}

/* ===== CALCULATOR BOX ===== */
.calc-box {
    background: var(--bg-white);
    border-radius: 20px;
    box-shadow: 0 4px 30px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.04);
    padding: 0;
    margin-top: 1.5rem;
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.04);
}

/* Navigation Header */
.calc-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(180deg, #FAFCFF 0%, var(--bg-white) 100%);
}

.nav-arrow {
    width: 38px; height: 38px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: var(--bg-section-alt);
    border: 1px solid var(--border-light);
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text-body);
    font-size: 0.85rem;
}
.nav-arrow:hover {
    background: var(--accent-1); color: #fff;
    border-color: var(--accent-1);
    transform: scale(1.08);
    box-shadow: 0 3px 12px rgba(14,165,233,0.25);
}
.nav-arrow:active { transform: scale(0.96); }

.nav-center {
    flex: 1; text-align: center; min-width: 0;
}

/* Pagination Dots */
.page-dots {
    display: flex; justify-content: center; gap: 5px;
    margin-bottom: 0.4rem;
}
.page-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #E2E8F0; transition: all 0.3s ease;
    cursor: pointer;
}
.page-dot.active { background: var(--accent-1); transform: scale(1.3); }
.page-dot.filled { background: var(--accent-3); }
.page-dot.filled.active { background: var(--accent-1); }

.nav-counter {
    font-size: 0.7rem; font-weight: 600; color: var(--text-light);
    letter-spacing: 0.03em;
}

/* Indicator Content */
.ind-content {
    padding: 1.5rem 1.5rem 0.5rem;
    text-align: center;
    transition: opacity 0.25s ease;
}

.ind-bubble {
    width: 72px; height: 72px; border-radius: 50%;
    margin: 0 auto 1rem;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: linear-gradient(135deg, #F0F9FF, #E0F2FE);
    border: 2px solid #BAE6FD;
    transition: all 0.4s ease;
}
.ind-bubble.filled {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border-color: #6EE7B7;
}
.ind-bubble .ib-num {
    font-size: 1.1rem; font-weight: 800; color: var(--accent-2); line-height: 1;
}
.ind-bubble.filled .ib-num { color: var(--accent-3); }
.ind-bubble .ib-pts {
    font-size: 0.55rem; font-weight: 600; color: var(--text-light); margin-top: 2px;
}

.ind-name {
    font-size: 1.05rem; font-weight: 700; color: var(--text-dark);
    margin-bottom: 0.25rem;
}
.ind-var {
    font-size: 0.75rem; color: var(--text-light); margin-bottom: 0.15rem;
}
.ind-bobot {
    font-size: 0.7rem; font-weight: 600; color: var(--accent-2);
    margin-bottom: 0.25rem;
}

/* Bar Chart */
.bars-area {
    padding: 1rem 1.5rem 1.5rem;
}
.bars-title {
    font-size: 0.6rem; font-weight: 700; color: var(--text-light);
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.75rem; text-align: left;
}

.bar-item {
    cursor: pointer; transition: all 0.25s ease;
    border-radius: 10px; padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border: 1.5px solid transparent;
    background: var(--bg-section-alt);
}
.bar-item:hover { background: #E8F4FD; border-color: #BAE6FD; }
.bar-item.selected {
    border-color: var(--accent-1); background: rgba(14,165,233,0.06);
    box-shadow: 0 2px 10px rgba(14,165,233,0.1);
}

.bar-top {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.4rem;
}
.bar-tag {
    font-size: 0.62rem; font-weight: 700; color: var(--accent-2);
    text-transform: uppercase; letter-spacing: 0.04em;
}
.bar-pts {
    font-size: 0.78rem; font-weight: 700; color: #CBD5E1;
    transition: color 0.3s ease;
}
.bar-item.selected .bar-pts { color: var(--accent-1); }

.bar-track {
    width: 100%; height: 8px; background: #E2E8F0;
    border-radius: 4px; overflow: hidden; margin-bottom: 0.4rem;
}
.bar-fill {
    height: 100%; border-radius: 4px; background: #CBD5E1;
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1), background 0.3s ease;
}
.bar-item.selected .bar-fill { background: var(--accent-1); }

.bar-desc {
    font-size: 0.78rem; color: var(--text-body); line-height: 1.45; text-align: left;
}
.bar-item.selected .bar-desc { color: var(--text-dark); font-weight: 500; }

.bar-reset {
    text-align: center; padding: 0.5rem;
    font-size: 0.72rem; color: var(--text-light);
    cursor: pointer; border-radius: 8px;
    transition: all 0.2s ease;
    border: 1px dashed #E2E8F0;
}
.bar-reset:hover { color: #EF4444; border-color: #FECACA; background: #FEF2F2; }

/* Keyboard hint */
.key-hint {
    text-align: center; padding: 0.75rem;
    font-size: 0.65rem; color: var(--text-light);
}
.key-hint kbd {
    display: inline-block; padding: 0.15rem 0.4rem;
    background: #F1F5F9; border: 1px solid #E2E8F0;
    border-radius: 4px; font-size: 0.6rem; font-family: inherit; font-weight: 600;
}

/* Responsive */
@media (max-width: 480px) {
    .calc-page { padding-left: 0.5rem; padding-right: 0.5rem; }
    .big-ring { width: 120px; height: 120px; }
    .big-ring svg { width: 120px; height: 120px; }
    .big-ring .score-num { font-size: 2rem; }
    .ind-content { padding: 1rem 1rem 0.5rem; }
    .bars-area { padding: 0.75rem 1rem 1.25rem; }
    .page-dots { gap: 4px; }
    .page-dot { width: 6px; height: 6px; }
}
</style>
</head>
<body>
<nav class="navbar">
    <div class="logo">
        <img src="Media/logo-medan.gif" alt="Logo Pemko" class="logo-img">
        <img src="Media/Brida logo.png" alt="Logo BRIDA" class="logo-img">
        <span>IGA<strong>Clinic</strong></span>
    </div>
    <ul class="nav-links" id="navLinks">
        <li><a href="index.html">Beranda</a></li>
        <li><a href="index.html#layanan">Layanan</a></li>
        <li><a href="index.html#galeri">Galeri</a></li>
        <li><a href="index.html#indikator">Indikator</a></li>
        <li><a href="index.html#faq">FAQ</a></li>
        <li><a href="feedback.html">Feedback</a></li>
        <li class="dropdown">
            <a href="#" class="dropdown-toggle" onclick="event.preventDefault(); this.parentElement.classList.toggle('open')">Download <i class="fas fa-chevron-down" style="font-size:0.6rem;margin-left:0.2rem"></i></a>
            <ul class="dropdown-menu">
                <li><a href="downloads/SOP_IGA.pdf" target="_blank">SOP</a></li>
                <li><a href="downloads/Modul_IGA.pdf" target="_blank">Modul</a></li>
                <li><a href="downloads/Pengumuman_IGA.pdf" target="_blank">Pengumuman</a></li>
                <li><a href="downloads/Template_Bukti_Dukung.xlsx" target="_blank">Template Bukti Dukung</a></li>
            </ul>
        </li>
    </ul>
    <div class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('active')">
        <span></span><span></span><span></span>
    </div>
    <a href="kalkulator.html" class="btn" style="background:var(--accent-3);color:#fff;"><i class="fas fa-calculator"></i> Kalkulator</a>
</nav>

<div class="calc-page">
    <div class="score-hero">
        <div class="score-hero-label">Kalkulator Skor Satuan Inovasi Daerah</div>
        <div class="big-ring">
            <svg viewBox="0 0 150 150">
                <circle class="track" cx="75" cy="75" r="65"></circle>
                <circle class="progress" id="ringProg" cx="75" cy="75" r="65"
                        stroke-dasharray="408.41" stroke-dashoffset="408.41"></circle>
            </svg>
            <div class="center-text">
                <div class="score-num" id="scoreNum">0</div>
                <div class="score-max">dari """ + str(max_score) + """</div>
            </div>
        </div>
        <div class="score-stats">
            <div class="stat-item"><div class="stat-val" id="filledCount">0</div><div class="stat-label">Terisi</div></div>
            <div class="stat-item"><div class="stat-val">20</div><div class="stat-label">Indikator</div></div>
            <div class="stat-item"><div class="stat-val" id="pctVal">0%</div><div class="stat-label">Pencapaian</div></div>
        </div>
    </div>

    <!-- Calculator Box -->
    <div class="calc-box">
        <div class="calc-nav">
            <div class="nav-arrow" id="prevBtn" onclick="nav(-1)"><i class="fas fa-chevron-left"></i></div>
            <div class="nav-center">
                <div class="page-dots" id="pageDots"></div>
                <div class="nav-counter" id="navCounter">1 / 20</div>
            </div>
            <div class="nav-arrow" id="nextBtn" onclick="nav(1)"><i class="fas fa-chevron-right"></i></div>
        </div>
        <div id="indContent" class="ind-content"></div>
        <div id="barsArea" class="bars-area"></div>
        <div class="key-hint"><kbd>&larr;</kbd> <kbd>&rarr;</kbd> untuk navigasi &middot; <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> untuk pilih parameter</div>
    </div>
</div>

<footer>
    <div class="footer-content">
        <div class="footer-logo">
            <img src="Media/logo-medan.gif" alt="Logo" class="footer-logo-img">
            <img src="Media/Brida logo.png" alt="Logo" class="footer-logo-img">
            <span>IGA<strong>Clinic</strong></span>
        </div>
        <p>&copy; 2026 BRIDA Kota Medan - Klinik Pelayanan IGA Award.</p>
    </div>
</footer>

<script>
const MAX = """ + str(max_score) + """;
const data = """ + js_data + """;
const sel = {};
let idx = 0;

data.forEach(d => sel[d.id] = 0);

function color(pct) {
    if (pct >= 80) return '#10B981';
    if (pct >= 50) return '#F59E0B';
    if (pct > 0) return '#0EA5E9';
    return '#CBD5E1';
}

function animNum(el, from, to, ms) {
    const t0 = performance.now();
    (function tick(now) {
        const p = Math.min((now-t0)/ms, 1);
        el.textContent = Math.round(from + (to-from)*(1-Math.pow(1-p,3)));
        if (p < 1) requestAnimationFrame(tick);
    })(t0);
}

function refreshScore() {
    let total = 0, filled = 0;
    data.forEach(d => { const v=sel[d.id]||0; total+=v*d.bobot; if(v>0)filled++; });
    const pct = (total/MAX)*100;
    const c = color(pct);
    const circ = 2*Math.PI*65;
    document.getElementById('ringProg').style.strokeDashoffset = circ-(pct/100)*circ;
    document.getElementById('ringProg').style.stroke = c;
    const el = document.getElementById('scoreNum');
    animNum(el, parseFloat(el.textContent)||0, total, 500);
    document.getElementById('filledCount').textContent = filled;
    document.getElementById('pctVal').textContent = Math.round(pct)+'%';
}

function buildDots() {
    const dotsEl = document.getElementById('pageDots');
    dotsEl.innerHTML = '';
    data.forEach((d,i) => {
        const dot = document.createElement('div');
        dot.className = 'page-dot';
        if (i === idx) dot.classList.add('active');
        if (sel[d.id] > 0) dot.classList.add('filled');
        dot.onclick = () => { idx = i; render(); };
        dotsEl.appendChild(dot);
    });
}

function render() {
    const d = data[idx];
    const v = sel[d.id] || 0;
    const maxBar = 3 * d.bobot;

    // Counter
    document.getElementById('navCounter').textContent = (idx+1) + ' / ' + data.length;

    // Dots
    buildDots();

    // Content
    const content = document.getElementById('indContent');
    content.style.opacity = '0';
    setTimeout(() => {
        content.innerHTML = `
            <div class="ind-bubble ${v>0?'filled':''}">
                <div class="ib-num">${d.id}</div>
                <div class="ib-pts">${v>0?(v*d.bobot).toFixed(0)+' pts':'—'}</div>
            </div>
            <div class="ind-name">${d.name}</div>
            <div class="ind-var">${d.variabel}</div>
            <div class="ind-bobot">Bobot Pengali: ${d.bobot}</div>
        `;
        content.style.opacity = '1';
    }, 80);

    // Bars
    const bars = document.getElementById('barsArea');
    bars.innerHTML = `
        <div class="bars-title">Pilih Parameter</div>
        <div class="bar-item ${v===1?'selected':''}" onclick="pick(1)">
            <div class="bar-top"><span class="bar-tag">Parameter 1</span><span class="bar-pts">${Math.round(1*d.bobot)} poin</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:${(1*d.bobot/maxBar)*100}%"></div></div>
            <div class="bar-desc">${d.p1}</div>
        </div>
        <div class="bar-item ${v===2?'selected':''}" onclick="pick(2)">
            <div class="bar-top"><span class="bar-tag">Parameter 2</span><span class="bar-pts">${Math.round(2*d.bobot)} poin</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:${(2*d.bobot/maxBar)*100}%"></div></div>
            <div class="bar-desc">${d.p2}</div>
        </div>
        <div class="bar-item ${v===3?'selected':''}" onclick="pick(3)">
            <div class="bar-top"><span class="bar-tag">Parameter 3</span><span class="bar-pts">${Math.round(3*d.bobot)} poin</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:100%"></div></div>
            <div class="bar-desc">${d.p3}</div>
        </div>
        <div class="bar-reset" onclick="pick(0)"><i class="fas fa-undo"></i> Reset</div>
    `;

    refreshScore();
}

function pick(val) {
    sel[data[idx].id] = val;
    render();
}

function nav(dir) {
    idx = (idx + dir + data.length) % data.length;
    render();
}

// Keyboard support
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') nav(-1);
    else if (e.key === 'ArrowRight') nav(1);
    else if (e.key === '1') pick(1);
    else if (e.key === '2') pick(2);
    else if (e.key === '3') pick(3);
    else if (e.key === '0') pick(0);
});

render();
</script>
</body>
</html>
"""

    with open(os.path.join(base_dir, "kalkulator.html"), "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate()
    print("kalkulator.html updated.")
