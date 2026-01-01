
import pandas as pd

def combine_multirow_header(csv_path, header_rows=2, sep='_', out_path=None):
    """
    Read a CSV with multi-row headers and collapse them into single-level
    column names, ignoring 'Unnamed' placeholders.
    """
   
    df = pd.read_csv(csv_path, header=list(range(header_rows)))
    
    new_cols = []
    for col in df.columns:
        parts = []
        for p in col:
            p_str = str(p).strip()
            if pd.notna(p) and p_str != '' and 'Unnamed' not in p_str:
                parts.append(p_str)
        
        if not parts:
            combined = ''
        else:
            combined = sep.join(parts)
            
        # 4. Normalize common characters for cleaner programming use
        combined = (combined.replace(' ', '_')
                            .replace('%', 'pct')
                            .replace('/', '_')
                            .replace('(', '')
                            .replace(')', '')
                            .lower()) # Optional: lowercase for consistency
        new_cols.append(combined)
    
    # 5. Ensure uniqueness (handles cases where different columns end up with the same name)
    counts = {}
    final_names = []
    for i, name in enumerate(new_cols):
        if name == '':
            name = f'unnamed_{i}'
        
        if name in counts:
            counts[name] += 1
            final_names.append(f"{name}_{counts[name]}")
        else:
            counts[name] = 0
            final_names.append(name)
            
    df.columns = final_names
    
    if out_path:
        df.to_csv(out_path, index=False)
        
    return df

# Usage
df_fixed = combine_multirow_header(
    "Genre_gamepass_comparison.csv", 
    header_rows=2, 
    sep='_', 
    out_path="Genre_Gamepass_fixed.csv"
)

print(df_fixed.columns.tolist())

# Example usage:


