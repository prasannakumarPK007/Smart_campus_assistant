# frontend/summarizer.py
import streamlit as st
import requests
from io import BytesIO
from typing import Optional, Dict, Any


def render_upload_and_summary(api_base: str) -> Optional[Dict[str, Any]]:
    """
    Renders the upload widget and summary view.
    Returns the backend response meta dict if upload succeeded, otherwise None.
    """
    st.write("Upload a single file (PDF / DOCX / TXT). Uploading a new file clears the previous one on the backend.")
    uploaded_file = st.file_uploader("Choose a file to upload", type=["pdf", "docx", "txt"], key="file_uploader")
    meta = None

    if uploaded_file is not None:
        # show filename and size
        st.write(f"Selected file: **{uploaded_file.name}** — {uploaded_file.size} bytes")
        if st.button("Upload & Process"):
            with st.spinner("Uploading and processing (this may take a few seconds)..."):
                try:
                    # prepare files for requests
                    file_bytes = uploaded_file.getvalue()
                    files = {"file": (uploaded_file.name, BytesIO(file_bytes), "application/octet-stream")}

                    resp = requests.post(f"{api_base}/upload", files=files, timeout=120)

                    # 🔴 INSTEAD OF resp.raise_for_status(), handle errors manually
                    if not resp.ok:
                        st.error(f"Backend error {resp.status_code}")
                        # show backend response (often includes traceback / detail)
                        st.code(resp.text)
                        return meta  # stop here

                    # try to parse JSON safely
                    try:
                        rj = resp.json()
                    except Exception as e:
                        st.error(f"Could not parse JSON from backend: {e}")
                        st.code(resp.text)
                        return meta

                    st.success("Upload complete and processed.")

                    # show a compact summary
                    summary_points = rj.get("summary_points") or rj.get("summary") or []
                    if summary_points:
                        st.markdown("#### Summary (point form)")
                        for i, s in enumerate(summary_points, start=1):
                            st.write(f"{i}. {s}")
                    else:
                        st.info("No summary returned from backend.")

                    meta = {"file_id": rj.get("file_id"), "filename": rj.get("filename")}

                except requests.exceptions.RequestException as e:
                    st.error("Upload failed due to network / backend error.")
                    st.exception(e)
                except Exception as e:
                    st.error("Upload failed.")
                    st.exception(e)

    # Also provide a button to fetch existing summary if a file was previously uploaded
    if st.button("Fetch current summary from backend"):
        try:
            resp = requests.get(f"{api_base}/summary", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                summary = data.get("summary", [])
                if summary:
                    st.markdown("#### Current Summary (from backend)")
                    for i, s in enumerate(summary, start=1):
                        st.write(f"{i}. {s}")
                    meta = {"file_id": data.get("file_id"), "filename": data.get("filename")}
                else:
                    st.info("No summary available.")
            else:
                st.warning(f"Backend returned {resp.status_code}")
                st.code(resp.text)
        except Exception as e:
            st.error("Could not fetch summary.")
            st.exception(e)

    return meta
