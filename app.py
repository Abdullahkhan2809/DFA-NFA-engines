"""
Automata Lab — Streamlit UI
Regex → NFA → DFA simulator with visualization, execution trace, and test suite.
"""

import os
import streamlit as st
import pandas as pd
import graphviz

# ---------- Local modules ----------
try:
    from core.automata import nfa as nfa_mod
    from core.automata import dfa as dfa_mod
    from core.automata import tokenizer as tokenizer_mod
except ImportError:
    import nfa as nfa_mod
    import dfa as dfa_mod
    import tokenizer as tokenizer_mod

try:
    import presets
except ImportError:
    presets = None


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Automata Lab",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# THEME / CSS — dark mode matching the mockup
# ==========================================================
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #e6e6e6; }

    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 0.4rem 0;
    }

    h1, h2, h3, h4 { color: #f0f6fc; }

    .status-ready {
        color: #28a745; font-weight: 600; font-size: 0.9rem;
        display: inline-block; margin-left: 8px;
    }

    .panel {
        background-color: #161b22; border: 1px solid #21262d;
        border-radius: 10px; padding: 18px; margin-bottom: 12px;
    }

    .result-accept {
        background-color: rgba(40, 167, 69, 0.12);
        border: 1.5px solid #28a745;
        border-radius: 10px; padding: 18px; text-align: center;
    }
    .result-accept h3 { color: #3fb950; margin: 0; letter-spacing: 2px; }
    .result-accept p  { color: #8b949e; font-family: monospace; margin: 6px 0 0; }

    .result-reject {
        background-color: rgba(220, 53, 69, 0.12);
        border: 1.5px solid #dc3545;
        border-radius: 10px; padding: 18px; text-align: center;
    }
    .result-reject h3 { color: #f85149; margin: 0; letter-spacing: 2px; }
    .result-reject p  { color: #8b949e; font-family: monospace; margin: 6px 0 0; }

    .stButton > button {
        border-radius: 8px; font-weight: 600;
        border: 1px solid #30363d;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        border: none;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #e6e6e6 !important;
        border: 1px solid #30363d !important;
    }

    .section-label {
        color: #8b949e; font-size: 0.85rem;
        text-transform: uppercase; letter-spacing: 1.2px;
        margin: 8px 0 6px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 6px 6px 0 0;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #3fb950 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SESSION STATE
# ==========================================================
if "transitions" not in st.session_state:
    st.session_state.transitions = pd.DataFrame({
        "State":      ["q0", "q0", "q1", "q1", "q2", "q2"],
        "Symbol":     ["0",  "1",  "0",  "1",  "0",  "1"],
        "Next State": ["q1", "q0", "q2", "q0", "q2", "q3"],
    })

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "dfa_machine" not in st.session_state:
    st.session_state.dfa_machine = None

if "nfa_machine" not in st.session_state:
    st.session_state.nfa_machine = None

if "trace" not in st.session_state:
    st.session_state.trace = pd.DataFrame(columns=["Step", "State", "Symbol", "→ Next"])


# ==========================================================
# BACKEND HELPERS
# ==========================================================
def build_from_regex(regex: str):
    """Run the full pipeline: regex → tokens → postfix → NFA → DFA.

    Returns (nfa_obj, dfa_obj, alphabet).
    """
    tokens = tokenizer_mod.tokenize(regex)
    clean_regex = tokenizer_mod.tokens_to_string(tokens)
    alphabet = tokenizer_mod.get_alphabet(tokens)

    with_concat = nfa_mod.add_concat(clean_regex)
    postfix = nfa_mod.infix_to_postfix(with_concat)
    nfa_obj = nfa_mod.regex_to_nfa(postfix)

    dfa_obj = dfa_mod.nfa_to_dfa(nfa_obj, alphabet)
    return nfa_obj, dfa_obj, alphabet


def build_dfa_from_table(states_str, alphabet_str, start_state, accept_states_str, transitions_df):
    """Build a DFA directly from the manual configuration table."""
    states = [s.strip() for s in states_str.split(",") if s.strip()]
    alphabet = [a.strip() for a in alphabet_str.split(",") if a.strip()]
    accept_states = [s.strip() for s in accept_states_str.split(",") if s.strip()]

    state_objs = {name: dfa_mod.DFAState(name) for name in states}

    for _, row in transitions_df.iterrows():
        src = str(row["State"]).strip()
        sym = str(row["Symbol"]).strip()
        dst = str(row["Next State"]).strip()
        if src in state_objs and dst in state_objs and sym in alphabet:
            state_objs[src].transitions[sym] = state_objs[dst]

    start = state_objs.get(start_state.strip())
    accepts = {state_objs[a] for a in accept_states if a in state_objs}
    return dfa_mod.DFA(start, accepts, list(state_objs.values()), alphabet)


def render_dfa_graph(dfa_obj) -> graphviz.Digraph:
    """Render DFA as a horizontal graphviz diagram."""
    g = graphviz.Digraph()
    g.attr(rankdir="LR", bgcolor="transparent")
    g.attr("node",
           fontname="Helvetica", fontcolor="#e6e6e6",
           color="#3fb950", style="filled", fillcolor="#161b22",
           penwidth="2")
    g.attr("edge", color="#8b949e", fontcolor="#f0f6fc", fontname="Helvetica")

    g.node("__start__", shape="point", width="0.15", color="#3fb950")

    for state in dfa_obj.states:
        if state in dfa_obj.accept_states:
            g.node(state.name, shape="doublecircle")
        else:
            g.node(state.name, shape="circle")

    g.edge("__start__", dfa_obj.start.name, color="#3fb950")

    for state in dfa_obj.states:
        for sym, target in state.transitions.items():
            g.edge(state.name, target.name, label=f" {sym} ")

    return g


def render_nfa_graph(nfa_obj) -> graphviz.Digraph:
    """Render NFA (with ε-transitions) as a graphviz diagram.

    NFA states are anonymous Python objects, so we walk the graph from
    the start state, assign each unique state an id like n0, n1, n2..., and
    draw every edge (symbol edges + epsilon edges).
    """
    g = graphviz.Digraph()
    g.attr(rankdir="LR", bgcolor="transparent")
    g.attr("node",
           fontname="Helvetica", fontcolor="#e6e6e6",
           color="#58a6ff", style="filled", fillcolor="#161b22",
           penwidth="2")
    g.attr("edge", color="#8b949e", fontcolor="#f0f6fc", fontname="Helvetica")

    state_ids = {}
    counter = [0]

    def get_id(state):
        key = id(state)
        if key not in state_ids:
            state_ids[key] = (state, f"n{counter[0]}")
            counter[0] += 1
        return state_ids[key][1]

    # BFS from start state to discover every reachable NFA state
    visited = set()
    stack = [nfa_obj.start]
    while stack:
        s = stack.pop()
        if id(s) in visited:
            continue
        visited.add(id(s))
        get_id(s)
        for nxt in s.epsilon:
            if id(nxt) not in visited:
                stack.append(nxt)
        for sym, targets in s.edges.items():
            for nxt in targets:
                if id(nxt) not in visited:
                    stack.append(nxt)

    # Draw nodes
    g.node("__nfa_start__", shape="point", width="0.15", color="#58a6ff")
    for _, (state, sid) in state_ids.items():
        if state is nfa_obj.accept:
            g.node(sid, shape="doublecircle", color="#3fb950")
        elif state is nfa_obj.start:
            g.node(sid, shape="circle", color="#58a6ff")
        else:
            g.node(sid, shape="circle")

    g.edge("__nfa_start__", get_id(nfa_obj.start), color="#58a6ff")

    # Draw edges
    for _, (state, sid) in state_ids.items():
        for sym, targets in state.edges.items():
            for nxt in targets:
                g.edge(sid, get_id(nxt), label=f" {sym} ")
        for nxt in state.epsilon:
            g.edge(sid, get_id(nxt), label=" ε ",
                   style="dashed", color="#d29922", fontcolor="#d29922")

    return g


def simulate_with_trace(dfa_obj, input_string: str):
    """Run the DFA step-by-step. Returns (verdict, trace_df, final_state_name)."""
    if dfa_obj is None or dfa_obj.start is None:
        return "ERROR", pd.DataFrame(), None

    rows = [{"Step": 0, "State": dfa_obj.start.name, "Symbol": "—",
             "→ Next": dfa_obj.start.name}]
    current = dfa_obj.start

    for i, ch in enumerate(input_string, start=1):
        if ch not in current.transitions:
            rows.append({"Step": i, "State": current.name, "Symbol": ch, "→ Next": "∅"})
            return "REJECT", pd.DataFrame(rows), current.name
        nxt = current.transitions[ch]
        rows.append({"Step": i, "State": current.name, "Symbol": ch, "→ Next": nxt.name})
        current = nxt

    verdict = "ACCEPT" if current in dfa_obj.accept_states else "REJECT"
    return verdict, pd.DataFrame(rows), current.name


# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    logo_path = os.path.join("assets", "logo.png")
    logo_col, title_col = st.columns([1, 3])
    with logo_col:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
    with title_col:
        st.markdown(
            "<h1 style='color:#ffffff; letter-spacing:5px; margin-top:-20px; font-family:monospace;'>"
            "AUTOMATA LAB</h1>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    nav = st.radio(
        "Navigation",
        ["Automata Engine"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("<div class='section-label'>Contributors</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:monospace; font-size:0.85rem; color:#8b949e;'>"
        "• Abdullah Khan<br>"
        "• Muhammad Zain Khan<br>"
        "• Rumman ul Haq<br>"
        "• Ayoush Kishor"
        "</div>",
        unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
h1, _, h3 = st.columns([5, 1, 2])
with h1:
    st.markdown(
        f"<h2 style='display:inline'>{nav}</h2>"
        "<span class='status-ready'>● READY</span>",
        unsafe_allow_html=True,
    )
with h3:
    run_clicked = st.button("▶  Run Simulation", type="primary", use_container_width=True)

st.markdown("---")


# ==========================================================
# 4-COLUMN MAIN LAYOUT
# ==========================================================
col_cfg, col_sim, col_result = st.columns([1.1, 1.4, 1], gap="medium")

# ---------- CONFIGURATION ----------
with col_cfg:
    st.markdown("### Configuration")

    with st.expander("⚡ Generate from Regex", expanded=True):
        regex_pattern = st.text_input("Regular Expression", value="(0|1)*01")
        if st.button("Generate NFA & DFA", use_container_width=True):
            try:
                nfa_obj, dfa_obj, alpha = build_from_regex(regex_pattern)
                st.session_state.nfa_machine = nfa_obj
                st.session_state.dfa_machine = dfa_obj
                st.session_state.transitions = pd.DataFrame([
                    {"State": s.name, "Symbol": sym, "Next State": t.name}
                    for s in dfa_obj.states
                    for sym, t in s.transitions.items()
                ])
                st.success(
                    f"Built · {len(dfa_obj.states)} DFA states · alphabet {alpha}"
                )
            except Exception as e:
                st.error(f"Regex error: {e}")

        if st.button("Clear Generated Machines", use_container_width=True):
            st.session_state.nfa_machine = None
            st.session_state.dfa_machine = None
            st.info("Cleared. The table below now drives the diagram.")

    states        = st.text_input("States (comma-separated)", "q0, q1, q2, q3")
    alphabet      = st.text_input("Alphabet (comma-separated)", "0, 1")
    start_state   = st.text_input("Start State", "q0")
    accept_states = st.text_input("Accept States", "q2, q3")

    st.markdown("<div class='section-label'>Transition Function</div>", unsafe_allow_html=True)
    edited_df = st.data_editor(
        st.session_state.transitions,
        num_rows="dynamic",
        use_container_width=True,
        key="transitions_editor",
    )
    st.session_state.transitions = edited_df


# ---------- SIMULATION ----------
with col_sim:
    st.markdown("### ▷ Simulation")

    input_string = st.text_input("Input String", value="10110", key="input_string")

    # Decide which DFA drives simulation
    try:
        manual_dfa = build_dfa_from_table(
            states, alphabet, start_state, accept_states, st.session_state.transitions
        )
        active_dfa = st.session_state.dfa_machine or manual_dfa
    except Exception as e:
        st.error(f"DFA build error: {e}")
        active_dfa = None

    tab_dfa, tab_nfa = st.tabs(["DFA Diagram", "NFA Diagram"])

    with tab_dfa:
        if active_dfa is not None:
            try:
                st.graphviz_chart(render_dfa_graph(active_dfa), use_container_width=True)
            except Exception as e:
                st.error(f"Could not render DFA: {e}")
        else:
            st.info("No DFA available.")

    with tab_nfa:
        if st.session_state.nfa_machine is not None:
            try:
                st.graphviz_chart(
                    render_nfa_graph(st.session_state.nfa_machine),
                    use_container_width=True,
                )
                st.caption("Dashed orange edges = ε (epsilon) transitions.")
            except Exception as e:
                st.error(f"Could not render NFA: {e}")
        else:
            st.info(
                "NFA is only available when built from a regex.\n\n"
                "Use **⚡ Generate from Regex** in the Configuration panel."
            )

    st.markdown("<div class='section-label'>Execution Trace</div>", unsafe_allow_html=True)

    if run_clicked and active_dfa is not None:
        verdict, trace_df, final_state = simulate_with_trace(active_dfa, input_string)
        st.session_state.trace = trace_df
        st.session_state.last_result = (verdict, input_string, final_state)

    if not st.session_state.trace.empty:
        st.dataframe(st.session_state.trace, use_container_width=True,
                     hide_index=True, height=240)
    else:
        st.info("Click ▶ Run Simulation to see the execution trace.")


# ---------- RESULT + TEST SUITE ----------
with col_result:
    st.markdown("### Result")

    if st.session_state.last_result is None:
        st.markdown(
            "<div class='panel' style='text-align:center; color:#8b949e;'>"
            "No simulation run yet.<br>"
            "<span style='font-size:0.85rem;'>Press ▶ Run Simulation</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        verdict, inp, final = st.session_state.last_result
        if verdict == "ACCEPT":
            st.markdown(
                f"<div class='result-accept'><h2>ACCEPTED</h2>"
                f"<p>Input: {inp or 'ε'}  |  Final state: {final}</p></div>",
                unsafe_allow_html=True,
            )
        elif verdict == "REJECT":
            st.markdown(
                f"<div class='result-reject'><h2>REJECTED</h2>"
                f"<p>Input: {inp or 'ε'}  |  Final state: {final}</p></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='result-reject'><h2>ERROR</h2>"
                "<p>Could not process input</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown("### Test Suite")

    # Default seed test cases — users can edit, add rows, or delete rows below
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = pd.DataFrame({
            "Input":    ['""', "0", "01", "001", "10110", "1111", "0101", "@#$"],
            "Expected": ["REJECT", "REJECT", "ACCEPT", "ACCEPT", "ACCEPT",
                         "REJECT", "ACCEPT", "ERROR"],
            "Result":   ["—"] * 8,
        })

    # --- Editable test case table ---
    st.markdown(
        "<div class='section-label'>Edit Test Cases "
        "<span style='text-transform:none; color:#6e7681;'>"
        "(use \"\" for empty string)"
        "</span></div>",
        unsafe_allow_html=True,
    )

    edited_tests = st.data_editor(
        st.session_state.test_cases,
        num_rows="dynamic",   # ← lets the user add/delete rows
        use_container_width=True,
        hide_index=True,
        height=280,
        column_config={
            "Input": st.column_config.TextColumn(
                "Input",
                help='Input string to test. Use "" (two double quotes) for the empty string.',
                required=True,
            ),
            "Expected": st.column_config.SelectboxColumn(
                "Expected",
                help="What you expect the DFA to do with this input.",
                options=["ACCEPT", "REJECT", "ERROR"],
                required=True,
            ),
            "Result": st.column_config.TextColumn(
                "Result",
                help="Filled in after running tests.",
                disabled=True,   # users can't manually type results
            ),
        },
        key="test_editor",
    )

    # Persist edits — but wipe stale Results when Input/Expected change
    if not edited_tests.equals(st.session_state.test_cases):
        edited_tests = edited_tests.copy()
        # Fresh rows / edited rows get reset to "—"
        for i, row in edited_tests.iterrows():
            old = st.session_state.test_cases
            if i >= len(old) or old.iloc[i]["Input"] != row["Input"] \
                    or old.iloc[i]["Expected"] != row["Expected"]:
                edited_tests.at[i, "Result"] = "—"
        st.session_state.test_cases = edited_tests

    # --- Action buttons ---
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        run_all = st.button("▶ Run All Tests", use_container_width=True, type="primary")
    with btn_col2:
        reset = st.button("↺ Reset to Defaults", use_container_width=True)

    if reset:
        st.session_state.test_cases = pd.DataFrame({
            "Input":    ['""', "0", "01", "001", "10110", "1111", "0101", "@#$"],
            "Expected": ["REJECT", "REJECT", "ACCEPT", "ACCEPT", "ACCEPT",
                         "REJECT", "ACCEPT", "ERROR"],
            "Result":   ["—"] * 8,
        })
        st.rerun()

    if run_all and active_dfa is not None:
        results = []
        for inp in st.session_state.test_cases["Input"]:
            # Treat the literal "" or empty cell as the empty string
            inp_str = str(inp) if inp is not None else ""
            test_str = "" if inp_str.strip() == '""' or inp_str.strip() == "" else inp_str
            if any(c not in active_dfa.alphabet for c in test_str):
                results.append("ERROR")
                continue
            v, _, _ = simulate_with_trace(active_dfa, test_str)
            results.append(v)
        st.session_state.test_cases["Result"] = results
        st.rerun()   # refresh the table to show new results + colored rows

    # --- Summary metrics ---
    passing = (st.session_state.test_cases["Expected"] ==
               st.session_state.test_cases["Result"]).sum()
    failing = ((st.session_state.test_cases["Expected"] !=
                st.session_state.test_cases["Result"]) &
               (st.session_state.test_cases["Result"] != "—")).sum()
    total = len(st.session_state.test_cases)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total", total)
    m2.metric("Passing", int(passing))
    m3.metric("Failing", int(failing))

    # --- Color-coded read-only view (under the editor) ---
    has_results = (st.session_state.test_cases["Result"] != "—").any()
    if has_results:
        st.markdown(
            "<div class='section-label'>Results Summary</div>",
            unsafe_allow_html=True,
        )

        def color_rows(row):
            if row["Result"] == "—":
                return [""] * len(row)
            if row["Expected"] == row["Result"]:
                return ["background-color: rgba(40,167,69,0.15); color:#3fb950"] * len(row)
            return ["background-color: rgba(220,53,69,0.15); color:#f85149"] * len(row)

        st.dataframe(
            st.session_state.test_cases.style.apply(color_rows, axis=1),
            use_container_width=True,
            hide_index=True,
            height=240,
        )