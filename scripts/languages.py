"""Genera tarjetas SVG (clara y oscura) con los lenguajes más usados en los repos públicos."""
import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "ARL150")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else "dist"
IGNORAR = {"HTML", "CSS", "SCSS", "Shell", "Dockerfile", "Jupyter Notebook", "Batchfile", "PowerShell"}
COLORES = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Python": "#14B8A6", "C++": "#F34B7D",
    "Astro": "#FF5A03", "Java": "#B07219", "C": "#555555", "C#": "#178600", "Liquid": "#67B8DE",
    "Vue": "#41B883", "PHP": "#4F5D95", "Go": "#00ADD8", "Kotlin": "#A97BFF", "Dart": "#00B4AB",
}
PALETA = ["#6366F1", "#8B5CF6", "#0EA5E9", "#10B981", "#F59E0B", "#EC4899"]


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-languages"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
total = {}
for repo in repos:
    if repo["fork"] or repo["name"] == USER:
        continue
    for lang, n in get(repo["languages_url"]).items():
        if lang not in IGNORAR:
            total[lang] = total.get(lang, 0) + n

top = sorted(total.items(), key=lambda x: -x[1])[:6]
suma = sum(n for _, n in top) or 1
datos = [(l, n / suma * 100, COLORES.get(l, PALETA[i % len(PALETA)])) for i, (l, n) in enumerate(top)]

W, PAD = 480, 24
filas = (len(datos) + 1) // 2
H = 92 + filas * 28


def tarjeta(bg, borde, texto, sub):
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
              f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{bg}" stroke="{borde}"/>',
              f'<text x="{PAD}" y="38" font-size="17" font-weight="600" fill="{texto}">Lenguajes más usados</text>',
              f'<clipPath id="c"><rect x="{PAD}" y="54" width="{W-2*PAD}" height="10" rx="5"/></clipPath><g clip-path="url(#c)">']
    x = PAD
    for _, pct, color in datos:
        w = (W - 2 * PAD) * pct / 100
        partes.append(f'<rect x="{x:.2f}" y="54" width="{w + 0.5:.2f}" height="10" fill="{color}"/>')
        x += w
    partes.append("</g>")
    for i, (lang, pct, color) in enumerate(datos):
        cx = PAD + (i % 2) * (W - 2 * PAD) / 2
        cy = 94 + (i // 2) * 28
        partes.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}"/>')
        partes.append(f'<text x="{cx + 18}" y="{cy}" font-size="13" fill="{texto}">{lang} <tspan fill="{sub}">{pct:.1f}%</tspan></text>')
    partes.append("</svg>")
    return "\n".join(partes)


os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/languages.svg", "w").write(tarjeta("#FFFFFF", "#E5E7EB", "#1F2937", "#6B7280"))
open(f"{OUT}/languages-dark.svg", "w").write(tarjeta("#0D1117", "#30363D", "#E6EDF3", "#8B949E"))
print(datos)
