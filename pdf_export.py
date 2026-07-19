import io
import os
import urllib.request
import textwrap
import tempfile
import pandas as pd
import matplotlib

import lang
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from lang import LANGUAGES
from classification import QuestionType
from summary import QuestionSummary

CHART_DPI = 150
BAR_WIDTH = 0.6

FONT_FILENAME = "Tinos-Regular.ttf"
FONT_PATH = os.path.join(os.getcwd(), FONT_FILENAME)
FONT_URL = "https://github.com/google/fonts/raw/main/apache/tinos/Tinos-Regular.ttf"

def ensure_font_exists():
    if not os.path.exists(FONT_PATH) or os.path.getsize(FONT_PATH) == 0:
        try:
            print(f"Loading font (Times style): {FONT_PATH}")
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
            print("Font successfully downloaded!")
        except Exception as e:
            print(f"Error downloading font: {e}")

class PDFReport(FPDF):
    def __init__(self, lang_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang_dict 

        self.add_font("ArialUni", "", "arial.ttf")         # Звичайний
        self.add_font("ArialUni", "B", "arialbd.ttf")


    def header(self):
        try:
            self.set_font("ArialUni", "B", size=12)
            self.cell(0, 10, self.lang["report_title"], ln=1, align='R')
        except Exception:
            # Fallback
            self.set_font("ArialUni", "B", 10)
            self.cell(0, 10, self.lang["report_title"], ln=1, align='R')

def create_chart_image(qs: QuestionSummary, selected_lang: str) -> io.BytesIO:
    plt.close('all')
    plt.clf()
    plt.rcParams.update({
        'font.size': 10,
        'font.family': 'serif' 
    })

    lang_dict = LANGUAGES[selected_lang]

    col_variant = qs.table.columns[0]
    col_count = qs.table.columns[1]

    labels = qs.table[col_variant].astype(str).tolist()
    values = pd.to_numeric(qs.table[col_count], errors='coerce').fillna(0).tolist()
    if sum(values) == 0:
        return None
    
    wrapped_labels = [textwrap.fill(l, 25) for l in labels]

    is_scale = (qs.question.qtype == QuestionType.SCALE)
    if not is_scale:
        try:
            vals = pd.to_numeric(qs.table[col_variant], errors='coerce')
            if vals.notna().all() and vals.min() >= 0 and vals.max() <= 10:
                is_scale = True
        except: pass

    if is_scale:
        fig = plt.figure(figsize=(6.0, 4.0))
        bars = plt.bar(wrapped_labels, values, color='#4F81BD', width=BAR_WIDTH)
        plt.ylabel(lang_dict["count"])
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    else:
        fig = plt.figure(figsize=(6.0, 4.0))
        colors = ['#4F81BD', '#C0504D', '#9BBB59', '#8064A2', '#4BACC6', '#F79646']
        c_arg = colors[:len(values)] if len(values) <= len(colors) else None
        wedges, texts, autotexts = plt.pie(
            values, labels=None, autopct='%1.1f%%', startangle=90,
            pctdistance=0.8, colors=c_arg, radius=1.0
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            import matplotlib.patheffects as path_effects
            autotext.set_path_effects([path_effects.withStroke(linewidth=2, foreground='#333333')])
        
        plt.axis('equal')
        cols = 2 if len(labels) > 3 else 1
        plt.legend(wrapped_labels, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=cols, frameon=False, fontsize=8)

    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=CHART_DPI, bbox_inches='tight')
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def build_pdf_report(original_df, sliced_df, summaries, range_info, selected_lang="UA") -> bytes:
    ensure_font_exists()

    lang = LANGUAGES[selected_lang]
    
    pdf = PDFReport(lang)
    
    font_ok = False
    if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 0:
        try:
            pdf.add_font("TimesUA", fname=FONT_PATH)
            font_ok = True
        except Exception as e:
            print(f"Font error: {e}")

    pdf.add_page()
    
    # --- ТИТУЛКА  ---
    # --- ТИТУЛКА  ---
    pdf.set_font("ArialUni", "B", 16)
    pdf.cell(0, 10, lang["report_title"], ln=1, align='C')
        
    pdf.set_font("ArialUni", "", 12)
    safe_range = range_info.replace('–', '-').replace('—', '-')
        
    pdf.cell(0, 10, f"{lang['total_surveys']}: {len(original_df)}", ln=1, align='C')
    pdf.cell(0, 10, f"{lang['processed_surveys']}: {len(sliced_df)}", ln=1, align='C')
    pdf.cell(0, 10, safe_range, ln=1, align='C')
    
    pdf.ln(5)

    for qs in summaries:
        if qs.table.empty: continue
        
        title = f"{qs.question.code}. {qs.question.text}"
        title = title.replace('–', '-').replace('—', '-').replace('’', "'")
        
        # Назва питання
        if font_ok:
            pdf.set_font("TimesUA", size=12) 
            pdf.multi_cell(0, 6, title)
        else:
            pdf.set_font("Times", "B", 12)
            pdf.multi_cell(0, 6, f"Question {qs.question.code}")

        pdf.ln(2)

        # Таблиця
        if font_ok: pdf.set_font("TimesUA", size=11)
        else: pdf.set_font("Times", size=10)

        col_w1 = 110
        col_w2 = 30

        h1 = lang["option"] if font_ok else "Option"
        h2 = lang["count"] if font_ok else "Count"
        h3 = "%"
        
        pdf.cell(col_w1, 8, h1, border=1, ln=0)
        pdf.cell(col_w2, 8, h2, border=1, ln=0)
        pdf.cell(col_w2, 8, h3, border=1, ln=1)
        
        for row in qs.table.itertuples(index=False):
            val_text = str(row[0])[:60].replace('–', '-').replace('—', '-').replace('’', "'")
            
            # Якщо шрифт не завантажився, уникаємо кирилиці
            if not font_ok and not val_text.isascii():
                val_text = "..."

            pdf.cell(col_w1, 8, val_text, border=1, ln=0)
            pdf.cell(col_w2, 8, str(row[1]), border=1, ln=0)
            pdf.cell(col_w2, 8, str(row[2]), border=1, ln=1)
            
        pdf.ln(5)

        # Графік
       # Графік
        try:
            img = create_chart_image(qs, selected_lang)
            if img is None:
                continue
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(img.getvalue())
                name = tmp.name
            
            pdf.image(name, w=140, x=35)
            os.unlink(name)
            pdf.ln(10)
        except Exception as e:
            # Отримуємо повний текст помилки
            import traceback
            error_details = traceback.format_exc()
            print(f"Помилка створення графіку:\n{error_details}")
            
            # ДРУКУЄМО ПОМИЛКУ ПРЯМО В PDF
            if font_ok: 
                pdf.set_font("TimesUA", size=10)
            else:
                pdf.set_font("Times", "B", 10)
            
            pdf.multi_cell(0, 5, f"CHART ERROR DETAILS: {str(e)}")
            pdf.ln(5)

    # Повертаємо PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        tmp_name = tmp_pdf.name
        
    with open(tmp_name, 'rb') as f:
        pdf_bytes = f.read()
    os.unlink(tmp_name)
    
    return pdf_bytes