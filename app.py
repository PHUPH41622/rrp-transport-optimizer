import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="RRP TSP Optimizer",
    page_icon="🚛",
    layout="wide"
)

# --- 1. Data Loading ---
@st.cache_data
def load_data():
    """Loads the RRP.csv file and returns a DataFrame."""
    try:
        # Load CSV using the first column as the index (row labels)
        df = pd.read_csv('RRP.csv', index_col=0)
        return df
    except FileNotFoundError:
        st.error("Error: 'RRP.csv' not found. Please make sure the file is in the same directory.")
        return pd.DataFrame()

df = load_data()

# --- 2. TSP Logic (Nearest Neighbor) ---
def calculate_path_distance(path, df):
    """Calculates the total distance of a given ordered path."""
    total_distance = 0
    # Loop through the path: distance from current node to next node
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i+1]
        total_distance += df.loc[from_node, to_node]
    
    # Add distance from last node back to start (cycle)
    total_distance += df.loc[path[-1], path[0]]
    return total_distance

def solve_tsp_nearest_neighbor(nodes, df, start_node=None):
    """
    Solves TSP using the Nearest Neighbor heuristic.
    Algorithm:
    1. Start at a random node (or user-defined).
    2. Find the nearest unvisited node.
    3. Move to that node and mark it as visited.
    4. Repeat until all nodes are visited.
    5. Return to the start node.
    """
    if not nodes:
        return [], 0
    
    # Determine start node
    current_node = start_node if start_node in nodes else nodes[0]
    
    path = [current_node]
    unvisited = set(nodes)
    unvisited.remove(current_node)
    
    while unvisited:
        nearest_neighbor = None
        min_dist = float('inf')
        
        # Find the nearest unvisited neighbor
        for neighbor in unvisited:
            dist = df.loc[current_node, neighbor]
            if dist < min_dist:
                min_dist = dist
                nearest_neighbor = neighbor
        
        # Move to the nearest neighbor
        if nearest_neighbor:
            path.append(nearest_neighbor)
            unvisited.remove(nearest_neighbor)
            current_node = nearest_neighbor
        else:
            break # Should not happen if graph is connected (here it's fully connected)

    # Calculate total distance including return to start
    total_dist = calculate_path_distance(path, df)
    
    return path, total_dist

# --- 3. UI Layout ---
st.title("🚛 RRP Routing")
st.markdown("Select locations to visit. The route will optimized by **Nearest Neighbor algorithm**.")

if not df.empty:
    st.header("📍 Configuration")
    
    available_nodes = df.index.tolist()
    
    # Multiselect for choosing locations (exclude C00 from selection as it's mandatory)
    selectable_nodes = [n for n in available_nodes if n != 'C00']
    
    selected_nodes_user = st.multiselect(
        "Select Locations to Visit (C00 is included by default):",
        options=selectable_nodes,
        default=selectable_nodes[:5] if len(selectable_nodes) >= 5 else [],
        help="Choose the nodes you want to include in the route."
    )
    
    # Combine C00 with user selection
    selected_nodes = ['C00'] + selected_nodes_user
    
    st.info("ℹ️ Route always starts and ends at **C00**.")

    calculate_btn = st.button("🚀 Calculate Best Route", type="primary")

    # Main Area
    if calculate_btn:
        if len(selected_nodes) < 2:
            st.warning("⚠️ Please select at least 1 locations (besides C00) to calculate a route.")
        else:
            with st.spinner("Calculating optimal route..."):
                # Run Algorithm with fixed start node C00
                optimal_path, total_distance = solve_tsp_nearest_neighbor(
                    selected_nodes, 
                    df, 
                    start_node='C00'
                )
                
                # Display Results
                st.success("✅ Optimization Complete!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(label="🛣️ Total Distance", value=f"{total_distance:.2f}")
                    st.metric(label="📍 Stops", value=len(optimal_path))

                with col2:
                     st.write("### 🗺️ Optimized Route Order")
                     # Prepare a nice arrow formatted string
                     path_str = " ➡️ ".join(optimal_path) + f" ➡️ {optimal_path[0]} (Back to Depot)"
                     st.info(path_str)

                # Detailed Step-by-Step Table
                st.subheader("📋 Step-by-Step Details")
                
                step_data = []
                cumulative_dist = 0
                
                # Path steps
                for i in range(len(optimal_path)):
                    from_node = optimal_path[i]
                    # Next node logic (handles wrapping back to start)
                    if i < len(optimal_path) - 1:
                        to_node = optimal_path[i+1]
                    else:
                        to_node = optimal_path[0] # Return to start
                    
                    dist = df.loc[from_node, to_node]
                    cumulative_dist += dist
                    
                    step_data.append({
                        "Step": i + 1,
                        "From": from_node,
                        "To": to_node,
                        "Distance": dist,
                        "Cumulative Distance": cumulative_dist
                    })
                
                step_df = pd.DataFrame(step_data)
                st.dataframe(step_df, width='stretch')

else:
    st.info("Awaiting data load...")
