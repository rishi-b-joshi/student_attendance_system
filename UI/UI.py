import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import datetime, timedelta
import base64
from typing import Any, Dict, Optional, Tuple

# =========================
# App Config
# =========================
st.set_page_config(page_title="QR Attendance", page_icon="✅", layout="wide")
DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# =========================
# Session State
# =========================
def init_state():
    if "base_url" not in st.session_state:
        st.session_state.base_url = DEFAULT_BASE_URL

    if "students" not in st.session_state:
        st.session_state.students = {}  # {student_id: {...}}
    if "lectures" not in st.session_state:
        st.session_state.lectures = {}  # {lecture_id: {...}}
    if "attendance" not in st.session_state:
        st.session_state.attendance = []  # verify log
    if "last_created_lecture_id" not in st.session_state:
        st.session_state.last_created_lecture_id = None

init_state()

# =========================
# Helpers
# =========================
def toast(msg, icon="✅"):
    st.toast(msg, icon=icon)

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_strip(x: Any) -> str:
    return (x or "").strip() if isinstance(x, str) else str(x).strip()

def seconds_left(token_generated_at: Optional[str], expires_in_seconds: Optional[int]) -> int:
    if not token_generated_at or not expires_in_seconds:
        return 0
    try:
        gen = datetime.strptime(token_generated_at, "%Y-%m-%d %H:%M:%S")
        end = gen + timedelta(seconds=int(expires_in_seconds))
        return max(0, int((end - datetime.now()).total_seconds()))
    except Exception:
        return 0

# =========================
# SVG Render Fix
# =========================
def normalize_svg(svg_text: str) -> str:
    svg_text = (svg_text or "").strip()
    svg_text = (
        svg_text.replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&amp;", "&")
    )
    return svg_text

def render_svg(svg_text: str, height: int = 420):
    svg_text = normalize_svg(svg_text)
    if not svg_text:
        st.info("No SVG received.")
        return

    b64 = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    html = f"""
    <div style="display:flex; justify-content:center; align-items:center;">
      <img src="data:image/svg+xml;base64,{b64}" style="max-width:100%; height:auto;" />
    </div>
    """
    components.html(html, height=height)

# =========================
# API Helpers
# =========================
def api_post_json(path: str, payload: Dict[str, Any], timeout: int = 20) -> Tuple[bool, Any, str]:
    base_url = st.session_state.base_url.rstrip("/")
    url = f"{base_url}{path}"
    try:
        r = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as e:
        return False, None, f"API connection error: {e}"

    try:
        data = r.json()
    except Exception:
        return False, None, f"Expected JSON response, got: {r.text}"

    if not r.ok:
        return False, data, f"HTTP {r.status_code}: {r.text}"

    return True, data, ""

def api_get_json(path: str, params: Dict[str, Any], timeout: int = 20) -> Tuple[bool, Any, str]:
    base_url = st.session_state.base_url.rstrip("/")
    url = f"{base_url}{path}"
    try:
        r = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        return False, None, f"API connection error: {e}"

    try:
        data = r.json()
    except Exception:
        return False, None, f"Expected JSON response, got: {r.text}"

    if not r.ok:
        return False, data, f"HTTP {r.status_code}: {r.text}"

    return True, data, ""

def api_get_text(path: str, params: Dict[str, Any], timeout: int = 20) -> Tuple[bool, str, str]:
    base_url = st.session_state.base_url.rstrip("/")
    url = f"{base_url}{path}"
    try:
        r = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        return False, "", f"API connection error: {e}"

    if not r.ok:
        return False, "", f"HTTP {r.status_code}: {r.text}"

    return True, r.text, ""

# =========================
# API Wrappers (Your Contract)
# =========================
def api_create_student(student_id: str, name: str, class_name: str):
    return api_post_json("/attendance/students/create/", {"id": student_id, "name": name, "class_name": class_name})

def api_create_lecture(subject: str, section: str, date_str: str):
    return api_post_json("/attendance/lectures/create/", {"subject": subject, "section": section, "date": date_str})

def api_get_lecture_token(lecture_id: int, subject: str, section: str, date_str: str):
    return api_get_json(f"/attendance/lectures/{lecture_id}/token/", {"subject": subject, "section": section, "date": date_str})

def api_get_qr_svg(lecture_id: int, subject: str, section: str, date_str: str):
    return api_get_text(f"/attendance/lectures/{lecture_id}/qr-svg/", {"subject": subject, "section": section, "date": date_str})

def api_verify_attendance(student_id: str, qr_token: str):
    return api_post_json("/attendance/verify/", {"student_id": student_id, "qr_token": qr_token})

# =========================
# Header + Config (Sidebar only for settings)
# =========================
st.title("✅ QR Attendance System")
# st.caption("POST: create student/lecture/verify • GET: token + qr-svg (raw SVG) • Top menu navigation")
st.caption("Student Creation, Lecture Creation, Token Generation, Attendance Verification, and QR SVG fetching.")
with st.sidebar:
    st.subheader("⚙️ Settings")
    st.session_state.base_url = st.text_input("Base URL", value=st.session_state.base_url)

    st.divider()
    if st.button("🧹 Reset UI State"):
        st.session_state.students = {}
        st.session_state.lectures = {}
        st.session_state.attendance = []
        st.session_state.last_created_lecture_id = None
        toast("UI state cleared (server data unchanged).", "🧹")

# =========================
# ✅ Top Menu Bar (Tabs)
# =========================
tab_dashboard, tab_students, tab_lectures, tab_qr, tab_attendance = st.tabs(
    ["📊 Dashboard", "👩‍🎓 Students", "📚 Lectures", "🧾 QR & Check-in", "✅ Attendance"]
)

# =========================
# Dashboard
# =========================
with tab_dashboard:
    st.subheader("📊 Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Students (UI cache)", len(st.session_state.students))
    c2.metric("Lectures (UI cache)", len(st.session_state.lectures))
    c3.metric("Attendance logs (UI)", len(st.session_state.attendance))

    st.divider()
    st.subheader("Recent Attendance")
    if st.session_state.attendance:
        st.dataframe(pd.DataFrame(st.session_state.attendance).tail(10), use_container_width=True, hide_index=True)
    else:
        st.info("No attendance recorded in UI yet.")

# =========================
# Students
# =========================
with tab_students:
    st.subheader("👩‍🎓 Students")

    left, right = st.columns([1.1, 1.4], vertical_alignment="top")

    with left:
        st.markdown("### ➕ Create Student")
        with st.form("create_student_form", clear_on_submit=False):
            sid = st.text_input("Student ID", placeholder="e.g. S001")
            name = st.text_input("Name", placeholder="e.g. Alice Johnson")
            class_name = st.text_input("Class Name", placeholder="e.g. FY-CS")
            submit = st.form_submit_button("Create Student", type="primary")

        if submit:
            sid, name, class_name = safe_strip(sid), safe_strip(name), safe_strip(class_name)
            if not sid or not name or not class_name:
                toast("Student ID, Name, Class Name are required.", "❌")
            else:
                ok, data, err = api_create_student(sid, name, class_name)
                if not ok:
                    toast(err or "Create student failed.", "❌")
                else:
                    student_id = data.get("student_id", sid)
                    st.session_state.students[student_id] = {
                        "id": student_id,
                        "name": name,
                        "class_name": class_name,
                        "created_at": now_iso(),
                        "status": data.get("status", "success"),
                        "message": data.get("message", "")
                    }
                    toast(data.get("message", "Student created"), "✅")

        st.divider()
        query = st.text_input("Search (UI cache)", placeholder="Search by id/name/class...")

    with right:
        st.markdown("### 📄 Student List")
        rows = list(st.session_state.students.values())
        if query.strip():
            q = query.lower()
            rows = [s for s in rows if q in s["id"].lower() or q in s["name"].lower() or q in s["class_name"].lower()]

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No students in UI cache yet.")

# =========================
# Lectures
# =========================
with tab_lectures:
    st.subheader("📚 Lectures")

    left, right = st.columns([1.1, 1.4], vertical_alignment="top")

    with left:
        st.markdown("### ➕ Create Lecture")
        with st.form("create_lecture_form", clear_on_submit=False):
            subject = st.text_input("Subject", placeholder="e.g. Maths")
            section = st.text_input("Section", placeholder="e.g. A")
            date_val = st.date_input("Date")
            submit = st.form_submit_button("Create Lecture", type="primary")

        if submit:
            subject, section, date_str = safe_strip(subject), safe_strip(section), str(date_val)
            if not subject or not section or not date_str:
                toast("Subject, Section, Date are required.", "❌")
            else:
                ok, data, err = api_create_lecture(subject, section, date_str)
                if not ok:
                    toast(err or "Create lecture failed.", "❌")
                else:
                    lecture_id = data.get("lecture_id")
                    if lecture_id is None:
                        toast("lecture_id missing in response.", "❌")
                    else:
                        lecture_id = int(lecture_id)
                        st.session_state.lectures[lecture_id] = {
                            "id": lecture_id,
                            "subject": subject,
                            "section": section,
                            "date": date_str,
                            "created_at": now_iso(),
                            "status": data.get("status", "success"),
                            "message": data.get("message", ""),
                            "qr_token": None,
                            "expires_in_seconds": None,
                            "token_generated_at": None,
                            "qr_svg": None
                        }
                        st.session_state.last_created_lecture_id = lecture_id
                        toast(data.get("message", "Lecture created"), "✅")

    with right:
        st.markdown("### 📄 Lecture List")
        if st.session_state.lectures:
            st.dataframe(pd.DataFrame(list(st.session_state.lectures.values())), use_container_width=True, hide_index=True)
        else:
            st.info("No lectures in UI cache yet.")

# =========================
# QR & Check-in
# =========================
with tab_qr:
    st.subheader("🧾 QR & Check-in")

    if not st.session_state.lectures:
        st.info("Create a lecture first.")
    else:
        lecture_ids = sorted(st.session_state.lectures.keys())
        default_idx = lecture_ids.index(st.session_state.last_created_lecture_id) if st.session_state.last_created_lecture_id in lecture_ids else 0
        selected_lecture_id = st.selectbox("Select Lecture ID", lecture_ids, index=default_idx)
        lecture = st.session_state.lectures[selected_lecture_id]

        c1, c2 = st.columns([1.2, 1.0], vertical_alignment="top")

        with c1:
            st.markdown("### 🎟️ Lecture Details")
            st.write(f"**Subject:** {lecture['subject']}")
            st.write(f"**Section:** {lecture['section']}")
            st.write(f"**Date:** {lecture['date']}")

            st.divider()
            st.markdown("### 🔐 Get Token")
            if st.button("Generate Token", type="primary"):
                ok, data, err = api_get_lecture_token(lecture["id"], lecture["subject"], lecture["section"], lecture["date"])
                if not ok:
                    toast(err or "Token generation failed.", "❌")
                else:
                    lecture["qr_token"] = data.get("qr_token")
                    lecture["expires_in_seconds"] = data.get("expires_in_seconds", 300)
                    lecture["token_generated_at"] = now_iso()
                    lecture["qr_svg"] = None
                    st.session_state.lectures[selected_lecture_id] = lecture
                    toast("Token generated.", "✅")

            if lecture.get("qr_token"):
                remaining = seconds_left(lecture.get("token_generated_at"), lecture.get("expires_in_seconds"))
                st.info(f"Token valid for ~{remaining} seconds" if remaining else "Token expired. Generate again.")
                st.code(lecture["qr_token"], language="text")
            else:
                st.caption("No token yet.")

            st.divider()
            st.markdown("### ✅ Verify Attendance")
            student_ids = sorted(st.session_state.students.keys())
            mode = st.radio("Student Input", ["Pick from UI Students", "Enter Student ID"], horizontal=True)

            if mode == "Pick from UI Students":
                if not student_ids:
                    st.warning("No students in UI cache. Create student first.")
                    student_id = ""
                else:
                    student_id = st.selectbox("Select Student", student_ids)
                    st.caption(f"Name: {st.session_state.students[student_id]['name']} • Class: {st.session_state.students[student_id]['class_name']}")
            else:
                student_id = st.text_input("Student ID", placeholder="e.g. S001")

            with st.form("verify_form"):
                token_input = st.text_input("QR Token", value=lecture.get("qr_token") or "")
                submit = st.form_submit_button("Verify & Mark Attendance", type="primary")

            if submit:
                sid = safe_strip(student_id)
                token = safe_strip(token_input)

                if not sid:
                    toast("Student ID required.", "❌")
                elif not token:
                    toast("QR token required.", "❌")
                else:
                    ok, data, err = api_verify_attendance(sid, token)
                    if not ok:
                        toast(err or "Verify failed.", "❌")
                    else:
                        msg = data.get("message", "Attendance marked")
                        toast(msg, "✅")
                        st.session_state.attendance.append({
                            "marked_at_ui": now_iso(),
                            "status": data.get("status", "success"),
                            "message": msg,
                            "student_id": data.get("student", {}).get("id", sid),
                            "student_name": data.get("student", {}).get("name", ""),
                            "lecture_id": data.get("lecture", {}).get("id", lecture["id"]),
                            "subject": data.get("lecture", {}).get("subject", lecture["subject"]),
                            "section": data.get("lecture", {}).get("section", lecture["section"]),
                            "date": data.get("lecture", {}).get("date", lecture["date"]),
                        })

        with c2:
            st.markdown("### 📷 QR Code")
            if not lecture.get("qr_token"):
                st.info("Generate token first.")
            else:
                if st.button("Fetch QR SVG", type="secondary"):
                    ok, svg, err = api_get_qr_svg(lecture["id"], lecture["subject"], lecture["section"], lecture["date"])
                    if not ok:
                        toast(err or "QR fetch failed.", "❌")
                    else:
                        svg = normalize_svg(svg)
                        if "<svg" not in svg[:200].lower():
                            toast("QR API did not return SVG.", "❌")
                            st.code(svg[:800])
                        else:
                            lecture["qr_svg"] = svg
                            st.session_state.lectures[selected_lecture_id] = lecture
                            toast("QR loaded.", "✅")

                if lecture.get("qr_svg"):
                    render_svg(lecture["qr_svg"], height=420)

                    st.download_button(
                        "⬇ Download QR (SVG)",
                        data=lecture["qr_svg"].encode("utf-8"),
                        file_name=f"lecture_{lecture['id']}_qr.svg",
                        mime="image/svg+xml"
                    )
                else:
                    st.caption("Click **Fetch QR SVG** to display the QR code.")

# =========================
# Attendance
# =========================
with tab_attendance:
    st.subheader("✅ Attendance Log")

    if not st.session_state.attendance:
        st.info("No attendance in UI yet. Verify attendance from 'QR & Check-in'.")
    else:
        df = pd.DataFrame(st.session_state.attendance)

        lecture_ids = sorted(df["lecture_id"].dropna().unique().tolist()) if "lecture_id" in df.columns else []
        if lecture_ids:
            sel = st.selectbox("Filter by Lecture ID", ["All"] + [str(x) for x in lecture_ids])
            if sel != "All":
                df = df[df["lecture_id"] == int(sel)]

        st.dataframe(df.sort_values("marked_at_ui", ascending=False), use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export CSV", data=csv, file_name="attendance_ui_log.csv", mime="text/csv")