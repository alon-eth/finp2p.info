# Render src/og/privacy.png with the same template as tools/make-og.py
import re, subprocess, tempfile, html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
src=(ROOT/'tools'/'make-og.py').read_text()
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TPL=eval(re.search(r'TPL=(""".*?""")',src,flags=re.S).group(1))
for slug,eye,h1,sub in [('privacy','Need-to-know privacy','Only the parties to a trade should see the trade.','Who sees what, privacy by chain, and what a transaction costs. Every claim sourced.'),
    ('privacy-why','Need-to-know privacy · Explainer','Why public blockchains are a problem for institutions.','Front-running data from ESMA, and what the SEC, the BIS and J.P. Morgan say institutions need instead.')]:
    f=Path(tempfile.mkdtemp())/'p.html'; f.write_text(TPL.format(size=62 if len(h1)<62 else 54,eye=html.escape(eye),h1=html.escape(h1),sub=html.escape(sub)))
    out=ROOT/'src'/'og'/f'{slug}.png'
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--window-size=1200,630',f'--screenshot={out}','--virtual-time-budget=6000',f.as_uri()],check=True,capture_output=True)
    print('wrote',out)
