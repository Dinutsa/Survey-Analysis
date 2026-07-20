import io
import os
import zipfile
import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

import streamlit.components.v1 as components

st.write(f'<script>console.log("GTM TEST");</script>', unsafe_allow_html=True)
# Імпорти
from data_loader import load_excels, get_row_bounds, slice_range
from classification import classify_questions, QuestionType
from summary import build_all_summaries

from excel_export import build_excel_report
from pdf_export import build_pdf_report
from docx_export import build_docx_report
from pptx_export import build_pptx_report
from lang import LANGUAGES

# Initialize session state variables
if 'processed' not in st.session_state: st.session_state.processed = False
if 'ld' not in st.session_state: st.session_state.ld = None
if 'uploaded_files_store' not in st.session_state: st.session_state.uploaded_files_store = None


# --- SIDEBAR ---
with st.sidebar:
    selected_lang = st.sidebar.selectbox("🌐 Language / Мова / Limba / Język", ["UA", "EN", "RO", "PL"])
    lang = LANGUAGES[selected_lang]
    st.set_page_config(page_title=LANGUAGES[selected_lang]["page_title"], layout="wide")


    st.title(lang["app_title"])
    st.header(lang["upload_label"])

    demo_file_path = "demo_en_surveys.xlsx"
    if os.path.exists(demo_file_path):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            with open(demo_file_path, "rb") as f:
             st.download_button(
                label=lang["download_demo_btn"] + " 📄",
                data=f,
                file_name="survey_analytics_demo_en.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_d2:
            if st.button("⚡ Quick Demo", type="primary", use_container_width=True):
                try:
                    ld = load_excels([demo_file_path])
                    st.session_state.ld = ld

                    min_r, max_r = get_row_bounds(ld)
                    st.session_state.from_row = min_r
                    st.session_state.to_row = max_r
                    
                    sliced = slice_range(ld, min_r, max_r)
                    st.session_state.sliced = sliced
                    st.session_state.qinfo = classify_questions(sliced)
                    st.session_state.summaries = build_all_summaries(sliced, st.session_state.qinfo)
                    st.session_state.processed = True
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"{lang['error']}: {e}")


    uploaded_files = st.file_uploader("Excel-files (.xlsx)", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        if st.session_state.ld is None or uploaded_files != st.session_state.uploaded_files_store:
            try:
                ld = load_excels(uploaded_files)
                st.session_state.ld = ld
                st.session_state.uploaded_files_store = uploaded_files
                min_r, max_r = get_row_bounds(ld)
                st.session_state.from_row = min_r
                st.session_state.to_row = max_r
                st.session_state.processed = False
            except Exception as e: st.error(f"{lang['error']}: {e}")

    if st.session_state.ld:
        st.success(f"{lang['loaded']}: {st.session_state.ld.n_rows} {lang['surveys']}.")
        st.divider()
        st.header(lang["filter_section"])
        min_r, max_r = get_row_bounds(st.session_state.ld)
        if max_r > min_r:
            r_range = st.slider(lang["row_slider"], min_r, max_r, (st.session_state.from_row, st.session_state.to_row))
            st.session_state.from_row, st.session_state.to_row = r_range
        
        c1, c2 = st.columns(2)
        if c1.button(lang["process_btn"], type="primary", use_container_width=True):
            sliced = slice_range(st.session_state.ld, st.session_state.from_row, st.session_state.to_row)
            st.session_state.sliced = sliced
            st.session_state.qinfo = classify_questions(sliced)
            st.session_state.summaries = build_all_summaries(sliced, st.session_state.qinfo)
            st.session_state.processed = True
            
        if c2.button(lang["reset_btn"], use_container_width=True):
            st.session_state.clear()
            st.rerun()

# --- HELPER FUNCTIONS ---
def get_label(code, summary_map, selected_lang="UA"):
    lang = LANGUAGES[selected_lang]
    qs = summary_map[code]
    text = qs.question.text
    if len(text) > 90: text = text[:90] + "..."
    return f"{code}. {text}"

# def get_chart_fig(qs, df_data=None, title=None):
    data = df_data if df_data is not None else qs.table
    if data.empty: return None
    is_scale = (qs.question.qtype == QuestionType.SCALE)
    if not is_scale:
        try:
            vals = pd.to_numeric(data[""], errors='coerce')
            if vals.notna().all() and vals.min() >= 0 and vals.max() <= 10:
                is_scale = True
        except: pass

    if is_scale:
        fig = px.bar(data, x=lang["variant"], y=lang["count"], text=lang["count"], title=title)
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_type='category')
    else:
        fig = px.pie(data, names=lang["variant"], values=lang["count"], hole=0, title=title)
        fig.update_traces(textinfo='percent+label')
    return fig
#

def get_chart_fig(qs, df_data=None, title=None, selected_lang="UA"):
    lang = LANGUAGES[selected_lang]
    raw_data = df_data if df_data is not None else qs.table
    if raw_data.empty: 
        return None
    
    data = raw_data.copy()
    
    current_columns = list(data.columns)
    if len(current_columns) >= 2:
        data = data.rename(columns={
            current_columns[0]: lang["variant"], 
            current_columns[1]: lang["count"]  
        })
    
    is_scale = (qs.question.qtype == QuestionType.SCALE)
    if not is_scale:
        try:
            vals = pd.to_numeric(data[lang["variant"]], errors='coerce')
            if vals.notna().all() and vals.min() >= 0 and vals.max() <= 10:
                is_scale = True
        except: 
            pass

    if is_scale:
        fig = px.bar(data, x=lang["variant"], y=lang["count"], text=lang["count"], title=title)
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_type='category')
    else:
        fig = px.pie(data, names=lang["variant"], values=lang["count"], hole=0, title=title)
        fig.update_traces(textinfo='percent+label')
        
    return fig
# --- MAIN ---
if st.session_state.processed and st.session_state.sliced is not None:
    sliced = st.session_state.sliced
    summaries = st.session_state.summaries
    
    summary_map = {qs.question.code: qs for qs in summaries}
    question_codes = list(summary_map.keys())

    t1, t2 = st.tabs([lang["analyze_tab"], lang["export_tab"]])
    
    # === Tab 1: Analysis ===
    with t1:
        st.info(f"**{lang['in_work']} {len(sliced)} {lang['surveys']}** ({lang['rows']} {st.session_state.from_row}–{st.session_state.to_row})")
        with st.expander(lang["view_data"], expanded=False): 
            st.dataframe(sliced, use_container_width=True)
        st.divider()
        
        # 1. detailed viewer
        st.subheader(lang["detailed_view"])
        # ДОДАНО: Передаємо selected_lang у get_label
        selected_code = st.selectbox(lang["select_question"], options=question_codes, format_func=lambda x: get_label(x, summary_map, selected_lang), key="sb_detail")

        if selected_code:
            selected_qs = summary_map[selected_code]
            if not selected_qs.table.empty:
                st.markdown(f"**{selected_qs.question.text}**")
                c1, c2 = st.columns([1.5, 1])
                with c1: 
                    # ДОДАНО: Передаємо selected_lang у get_chart_fig
                    st.plotly_chart(get_chart_fig(selected_qs, title=lang["chart_title"], selected_lang=selected_lang), use_container_width=True)
                with c2: 
                    # ДОДАНО: Переклад колонок таблиці на льоту
                    disp_df = selected_qs.table.copy()
                    cols = list(disp_df.columns)
                    if len(cols) >= 2:
                        disp_df = disp_df.rename(columns={cols[0]: lang["variant"], cols[1]: lang["count"]})
                    st.dataframe(disp_df, use_container_width=True)
            else: st.warning(lang["no_data"])
        st.divider()

        # 2. МУЛЬТИ-ФІЛЬТР
        st.subheader(lang["analyze_responses"])
        with st.expander(lang["setup_filters"], expanded=True):
            f1_col1, f1_col2 = st.columns(2)
            with f1_col1:
                filter1_code = st.selectbox(lang["filter1"], options=question_codes, format_func=lambda x: get_label(x, summary_map, selected_lang), key="f1_q")
                filter1_qs = summary_map[filter1_code] if filter1_code else None
            with f1_col2:
                filter1_val = None
                if filter1_qs and filter1_qs.question.text in sliced.columns:
                    vals1 = [x for x in sliced[filter1_qs.question.text].unique() if pd.notna(x)]
                    try: vals1.sort() 
                    except: pass
                    filter1_val = st.selectbox(lang["filter1_value"], vals1, key="f1_v")

            use_filter2 = st.checkbox(lang["add_filter2"], value=False, key="use_f2")
            filter2_qs = None; filter2_val = None
            if use_filter2:
                f2_col1, f2_col2 = st.columns(2)
                with f2_col1:
                    filter2_code = st.selectbox(lang["filter2"], options=question_codes, format_func=lambda x: get_label(x, summary_map, selected_lang), key="f2_q")
                    filter2_qs = summary_map[filter2_code] if filter2_code else None
                with f2_col2:
                    if filter2_qs and filter2_qs.question.text in sliced.columns:
                        vals2 = [x for x in sliced[filter2_qs.question.text].unique() if pd.notna(x)]
                        try: vals2.sort()
                        except: pass
                        filter2_val = st.selectbox(lang["filter2_value"], vals2, key="f2_v")
            st.divider()
            target_code = st.selectbox(lang["target_question"], options=question_codes, format_func=lambda x: get_label(x, summary_map, selected_lang), key="target_q")
            target_qs = summary_map[target_code] if target_code else None

            if st.button(lang["apply_filters"], type="primary", use_container_width=True):
                if filter1_qs and filter1_val and target_qs:
                    subset = sliced[sliced[filter1_qs.question.text] == filter1_val]
                    info_text = f"{filter1_code}='{filter1_val}'"
                    if use_filter2 and filter2_qs and filter2_val:
                        subset = subset[subset[filter2_qs.question.text] == filter2_val]
                        info_text += f" + {filter2_code}='{filter2_val}'"

                    if not subset.empty:
                        st.success(f"{lang['found_results']} **{len(subset)}** {lang['surveys']} ({info_text})")
                        st.markdown(f"### {lang['result']}: {target_qs.question.code}")
                        col_target = target_qs.question.text
                        counts = subset[col_target].value_counts().reset_index()
                        
                        # Можливо, у твоєму словнику тут 'option' замість 'variant', тому залишаємо як є, але впевнюємося, що беремо зі словника
                        counts.columns = [lang.get("option", lang["variant"]), lang["count"]]
                        counts["%"] = (counts[lang["count"]] / len(subset) * 100).round(1)
                        g1, g2 = st.columns([1.5, 1])
                        with g1: 
                            # ДОДАНО: Передаємо selected_lang
                            st.plotly_chart(get_chart_fig(target_qs, df_data=counts, title=lang["distribution"], selected_lang=selected_lang), use_container_width=True)
                        with g2: st.dataframe(counts, use_container_width=True)
                    else: st.error(lang["no_results"])
                else: st.warning(lang["select_parameters"])
        st.divider()
        
        st.subheader(lang["full_summary"])
        for q in summaries:
            if q.table.empty: continue
            with st.expander(f"{q.question.code}. {q.question.text}", expanded=True):
                c1, c2 = st.columns([1, 1])
                with c1: 
                    # ДОДАНО: Передаємо selected_lang
                    st.plotly_chart(get_chart_fig(q, selected_lang=selected_lang), use_container_width=True, key=f"all_{q.question.code}")
                with c2: 
                    # ДОДАНО: Переклад колонок таблиці
                    disp_df = q.table.copy()
                    cols = list(disp_df.columns)
                    if len(cols) >= 2:
                        disp_df = disp_df.rename(columns={cols[0]: lang["variant"], cols[1]: lang["count"]})
                    st.dataframe(disp_df, use_container_width=True)

    # === Tab 2: Export ===
    with t2:
        st.subheader(lang["export_reports"])
        range_info = f"{lang['rows']} {st.session_state.from_row}–{st.session_state.to_row}"

        # caching the report generation functions to avoid re-computation
        @st.cache_data(show_spinner=False)
        def get_excel(_ld, _sl, _qi, _sm, _ri, selected_lang): return build_excel_report(_ld, _sl, _qi, _sm, _ri, selected_lang)
        @st.cache_data(show_spinner=False)
        def get_pdf(_ld, _sl, _sm, _ri, selected_lang): return build_pdf_report(_ld, _sl, _sm, _ri, selected_lang)
        @st.cache_data(show_spinner=False)
        def get_docx(_ld, _sl,_sm, _ri, selected_lang): return build_docx_report(_ld, _sl, _sm, _ri, selected_lang)
        @st.cache_data(show_spinner=False)
        def get_pptx(_ld, _sl, _sm, _ri, selected_lang): return build_pptx_report(_ld, _sl, _sm, _ri, selected_lang)

        @st.cache_data(show_spinner=False)
        def get_zip_archive(_ld, _sl, _qi, _sm, _ri, selected_lang="UA"):
            lang = LANGUAGES[selected_lang]
            plt.close('all') 
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("results.xlsx", build_excel_report(_ld, _sl, _qi, _sm, _ri, selected_lang))
                plt.close('all') 
                zf.writestr("results.pdf", build_pdf_report(_ld, _sl, _sm, _ri, selected_lang))
                plt.close('all') 
                zf.writestr("results.docx", build_docx_report(_ld, _sl, _sm, _ri, selected_lang))
                plt.close('all') 
                zf.writestr("results.pptx", build_pptx_report(_ld, _sl, _sm, _ri, selected_lang)) 
            return buf.getvalue()

        st.markdown(lang['chose_format'])
        current_lang = selected_lang
    
        cols = st.columns(4)
        
        with cols[0]:
            st.download_button(
                label=lang["download_excel"],
                data=get_excel(st.session_state.ld.df, sliced, st.session_state.qinfo, summaries, range_info,current_lang),
                file_name="survey_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_excel",
            )
        
        with cols[1]:
            st.download_button(
                label=lang["download_pdf"],
                data=get_pdf(st.session_state.ld.df, sliced, summaries, range_info, current_lang),
                file_name="survey_results.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_pdf",
            )
            
        with cols[2]:
            st.download_button(
                label=lang["download_docx"],
                data=get_docx(st.session_state.ld.df, sliced, summaries, range_info, current_lang),
                file_name="survey_results.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, 
                key="btn_docx",
            )
            
        with cols[3]:
            st.download_button(
                label=lang["download_pptx"],
                data=get_pptx(st.session_state.ld.df, sliced, summaries, range_info, current_lang),
                file_name="survey_results.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                key="btn_pptx",
            )

        st.divider()
        st.download_button(
            label=lang["download_zip"] + " 🗃️",
            data=get_zip_archive(st.session_state.ld.df, sliced, st.session_state.qinfo, summaries, range_info, current_lang),
            file_name="full_report.zip", 
            mime="application/zip", 
            type="primary", 
            use_container_width=True,
            key="btn_zip"
        )

elif not st.session_state.ld:
    st.info(lang["load_file_left"])

st.markdown("<br><br>", unsafe_allow_html=True) # Відступ
st.markdown("---") # Лінія

footer_html = f"""
<div style='text-align: center; color: #6c757d; font-size: 14px;'>
    <p>
        {lang['made_by']} <br>
        <b>{lang['developer']}</b> <br>
        <b>{lang['supervisor']}</b>
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)