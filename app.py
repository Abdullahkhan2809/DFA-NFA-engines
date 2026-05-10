import streamlit as st
import pandas as pd
import graphviz
import os

# --- Import Local Modules ---
# Importing local modules as per your repository structure
try:
    import dfa
    import nfa
    import presets
    import tokenizer
except ImportError as e:
    st.warning(f"Module import warning: {e}. Ensure dfa.py, nfa.py, presets.py, and tokenizer.py are in the root directory.")

# --- Page Configuration ---
st.set_page_config(page_title="Automata LAB", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Session State for Transitions ---
if 'transitions' not in st.session_state:
    st.session_state.transitions = pd.DataFrame({
        "State": ["q0", "q0", "q1", "q1", "q2", "q2"],
        "Symbol": ["0", "1", "0", "1", "0", "1"],
        "Next State": ["q1", "q0", "q2", "q0", "q2", "q3"]
    })

# --- Sidebar ---
with st.sidebar:
    # Adding the Logo
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        # Fallback if the logo isn't in the assets folder yet
        st.info("Logo placeholder. Save your logo as 'assets/logo.png'")
        st.title("L A B")
        
    st.markdown("---")
    st.subheader("Menu")
    st.radio("Navigation", ["DFA Engine", "NFA Engine", "Automata Library", "Test Runner"], label_visibility="collapsed")
    
    st.markdown("---")
    st.subheader("AUTOMATA TYPES")
    st.button("DFA", use_container_width=True)
    st.button("NFA", use_container_width=True)
    st.button("ε-NFA", use_container_width=True)
    st.button("PDA", use_container_width=True)

# --- Main Header ---
header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
with header_col1:
    st.header("DFA Engine")
with header_col2:
    st.markdown("<h4 style='color: #28a745; margin-top: 10px;'>● READY</h4>", unsafe_allow_html=True)
with header_col3:
    run_sim = st.button("▶ Run Simulation", type="primary", use_container_width=True)

st.markdown("---")

# --- Layout: Main Body Columns ---
left_col, right_col = st.columns([1, 1.2], gap="large")

# ==========================================
# LEFT COLUMN: Configuration
# ==========================================
with left_col:
    st.subheader("Configuration")
    st.markdown("### Regex to DFA")

    regex_pattern = st.text_input(
        "Enter Regular Expression",
        value="(0|1)*01",
        help="Example: (0|1)*01"
    )

    generate_dfa = st.button("Generate DFA", use_container_width=True)
    states = st.text_input("States (comma-separated)", "q0, q1, q2, q3")
    alphabet = st.text_input("Alphabet (comma-separated)", "0, 1")
    
    col_start, col_accept = st.columns(2)
    with col_start:
        start_state = st.text_input("Start State", "q0")
    with col_accept:
        accept_states = st.text_input("Accept States", "q2, q3")
        
    st.markdown("**Transition Function**")
    
    # Editable Dataframe for Transitions
    edited_df = st.data_editor(st.session_state.transitions, num_rows="dynamic", use_container_width=True)
    st.session_state.transitions = edited_df

# ==========================================
# RIGHT COLUMN: Simulation & Testing
# ==========================================
with right_col:
    st.subheader("Simulation")
    input_string = st.text_input("Input String", "10110")
    
    # Simulation Results Layout
    sim_col1, sim_col2 = st.columns([1, 1])
    
    with sim_col1:
        st.markdown("**DFA State Diagram**")
        # Placeholder for actual graphviz generation based on 'dfa' module logic
       # ==========================================
# DYNAMIC DFA GENERATION
# ==========================================

graph = graphviz.Digraph()
graph.attr(rankdir='LR')

if generate_dfa:

    try:
        # Example flow:
        # regex -> tokenizer -> nfa -> dfa
        
        tokens = tokenizer.tokenize(regex_pattern)

        # Build NFA
        nfa_machine = nfa.regex_to_nfa(tokens)

        # Convert NFA -> DFA
        dfa_machine = dfa.nfa_to_dfa(nfa_machine)

        # Initial node
        graph.node("start", shape="point")
        graph.edge("start", dfa_machine.start_state)

        # Add DFA states
        for state in dfa_machine.states:

            if state in dfa_machine.accept_states:
                graph.node(state, shape="doublecircle")
            else:
                graph.node(state, shape="circle")

        # Add transitions
        for (current_state, symbol), next_state in dfa_machine.transitions.items():

            graph.edge(
                current_state,
                next_state,
                label=str(symbol)
            )

        st.success("DFA Generated Successfully")

    except Exception as e:
        st.error(f"Regex parsing failed: {e}")

    st.graphviz_chart(graph)

    with sim_col2:
        st.markdown("**Execution Trace**")
        trace_data = {
            "Step": [0, 1, 2, 3, 4, 5],
            "State": ["q0", "q0", "q0", "q1", "q0", "q0"],
            "Symbol": ["—", "1", "0", "1", "1", "0"],
            "→ Next": ["q0", "q0", "q1", "q0", "q0", "q1"]
        }
        st.dataframe(pd.DataFrame(trace_data), use_container_width=True, hide_index=True)
    
    # Result Box
    st.success("**ACCEPTED** \n\n Input: 10110 | Final state: q1")

st.markdown("---")

# ==========================================
# BOTTOM SECTION: Test Suite
# ==========================================
st.subheader("Test Suite")

# Metrics
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("All", "12")
metric_col2.metric("Passing", "9")
metric_col3.metric("Failing", "3")
metric_col4.empty() # Placeholder for spacing

# Test Suite Table
test_data = {
    "Input": ['""', "0", "01", "001", "10110", "1111", "0101", "@#$"],
    "Expected": ["REJECT", "REJECT", "ACCEPT", "ACCEPT", "ACCEPT", "REJECT", "ACCEPT", "ERROR"],
    "Result": ["REJECT", "REJECT", "ACCEPT", "ACCEPT", "ACCEPT", "REJECT", "REJECT", "ERROR"]
}

df_tests = pd.DataFrame(test_data)

# Apply rudimentary color styling for pass/fail visualization
def color_results(row):
    if row['Expected'] == row['Result']:
        return ['background-color: #d4edda; color: #155724'] * len(row)
    else:
        return ['background-color: #f8d7da; color: #721c24'] * len(row)

st.dataframe(df_tests.style.apply(color_results, axis=1), use_container_width=True, hide_index=True)