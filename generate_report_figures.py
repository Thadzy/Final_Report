import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os

matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'lines.linewidth': 1.5,
})

COLOR_ENCODER  = '#2196F3'
COLOR_TARGET   = '#9E9E9E'
COLOR_KALMAN   = '#4CAF50'
COLOR_ERROR    = '#F44336'
COLOR_PASS     = '#4CAF50'
COLOR_FAIL     = '#F44336'
COLOR_BAND     = '#E8F5E9'
CRITERION_COLOR = '#FF5722'

DATA_DIR = Path("/Users/thadzy/Downloads/run5/")
OUTPUT_DIR = Path("/Users/thadzy/Documents/01_Projects/Final_Report/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_read_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

# FIGURE 1: Encoder Noise
def gen_fig_encoder_noise():
    print("Generating fig_encoder_noise...")
    files = list(DATA_DIR.glob("S1-ENC-NOISE*.csv"))
    if not files:
        raise FileNotFoundError("S1-ENC-NOISE*.csv not found")
    df = safe_read_csv(files[0])
    
    pos = df['pos'].values[:500] if len(df) > 500 else df['pos'].values
    t_ms = df['t_ms'].values[:500] if len(df) > 500 else df['t_ms'].values
    
    mean_pos = np.mean(pos)
    dev = pos - mean_pos
    p_p = np.max(pos) - np.min(pos)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [7, 3]})
    ax1.plot(t_ms, pos, color=COLOR_ENCODER, label='Encoder position')
    ax1.axhline(mean_pos, color=COLOR_TARGET, linestyle='--', label='Mean')
    
    # Annotate p-p
    ax1.annotate('', xy=(t_ms[np.argmax(pos)], np.max(pos)), xytext=(t_ms[np.argmax(pos)], np.min(pos)),
                 arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(t_ms[np.argmax(pos)] + 10, mean_pos, f'p-p = {p_p:.2f} counts' if p_p > 0.1 else f'p-p < 1 count', va='center')
    
    ax1.set_xlabel('Sample (1 kHz)')
    ax1.set_ylabel('Position (deg)')
    ax1.set_title('Encoder Noise Floor — Standstill (500 samples)')
    ax1.legend()
    
    ax2.hist(dev, bins=20, color=COLOR_ENCODER, edgecolor='white')
    ax2.set_xlabel('Deviation from mean (deg)')
    ax2.set_ylabel('Count')
    ax2.set_title('Deviation Histogram')
    
    plt.tight_layout()
    out = OUTPUT_DIR / "fig_encoder_noise.png"
    plt.savefig(out)
    plt.close()
    return out

# FIGURE 2: Homing Repeatability
def gen_fig_homing_repeat():
    print("Generating fig_homing_repeat...")
    files = sorted(list(DATA_DIR.glob("S1-HOMING_*.csv")))
    if not files:
        raise FileNotFoundError("S1-HOMING_*.csv not found")
    
    finals = []
    for f in files:
        df = safe_read_csv(f)
        stable = df[df['vel'].abs() < 0.1]
        if len(stable) >= 20:
            finals.append(stable['pos'].values[-20:].mean())
        else:
            finals.append(df['pos'].values[-1])
            
    finals = np.array(finals[:10])
    trials = np.arange(1, len(finals) + 1)
    mean_val = np.mean(finals)
    std_val = np.std(finals, ddof=1) if len(finals) > 1 else 0
    max_dev = np.max(np.abs(finals - mean_val))
    status = "PASS" if max_dev <= 0.1 else "FAIL"
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(trials, finals, s=80, color=COLOR_ENCODER, zorder=3)
    ax.axhline(mean_val, color=COLOR_TARGET, linestyle='--', label=f'Mean = {mean_val:.4f}°')
    ax.axhspan(mean_val - 0.1, mean_val + 0.1, color=COLOR_BAND, alpha=0.5, label='±0.1° criterion (A2)')
    ax.axhline(mean_val - 0.1, color=COLOR_FAIL, linewidth=1, linestyle='--')
    ax.axhline(mean_val + 0.1, color=COLOR_FAIL, linewidth=1, linestyle='--')
    
    ax.set_xlabel('Homing Trial')
    ax.set_ylabel('Final Position (deg)')
    ax.set_title('Homing Repeatability — 10 Trials')
    ax.set_xticks(trials)
    ax.legend(loc='lower left' if mean_val > 0 else 'upper left')
    
    textstr = f'σ = {std_val:.4f}°\nMax dev = {max_dev:.4f}°\nStatus: {status}'
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)
            
    out = OUTPUT_DIR / "fig_homing_repeat.png"
    plt.savefig(out)
    plt.close()
    return out

# FIGURE 3: Step Response
def gen_fig_step_response_hw():
    print("Generating fig_step_response_hw...")
    files = list(DATA_DIR.glob("step180_1_trial001_20260612_202955.csv"))
    if not files:
        files = list(DATA_DIR.glob("S1-STEP*.csv"))
    if not files:
        raise FileNotFoundError("step response CSV not found")
        
    df = safe_read_csv(files[0])
    
    # Find t0
    idx_t0 = df.index[df['pos'] > 1.0].tolist()
    if not idx_t0:
        idx_t0 = [0]
    t0 = df.loc[idx_t0[0], 't_ms']
    
    df['time_s'] = (df['t_ms'] - t0) / 1000.0
    df = df[df['time_s'] >= -0.2].copy()
    
    target_pos = 40.0
    y_ss = df['pos'].values[-int(0.1 * len(df)):].mean()
    band = 0.02 * target_pos
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [3, 2, 2]}, sharex=True)
    
    ax1.plot(df['time_s'], df['pos'], color=COLOR_ENCODER, label='Actual (Encoder)')
    ax1.axhline(target_pos, color=COLOR_TARGET, linestyle='--', label=f'Setpoint {int(target_pos)}°')
    ax1.axhspan(target_pos - band, target_pos + band, color=COLOR_BAND, alpha=0.4, label='±2% settling band')
    ax1.axvline(2.11, color=COLOR_FAIL, linestyle='--', label='t_s = 2.11 s')
    ax1.set_ylabel('Position (deg)')
    ax1.set_title(f'Step Response — Hardware (With Load, {int(target_pos)}° Step)')
    ax1.legend(loc='upper left')
    
    textstr = '%OS = 0.00%  → PASS\nt_s = 2.11 s  → FAIL (>0.5 s)\nSSE = 0.000°'
    props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.9)
    ax1.text(0.95, 0.05, textstr, transform=ax1.transAxes, fontsize=10,
             verticalalignment='bottom', horizontalalignment='right', bbox=props)
             
    err = target_pos - df['pos']
    ax2.plot(df['time_s'], err, color=COLOR_ERROR)
    ax2.axhline(0, color=COLOR_TARGET, linestyle='--')
    ax2.axhline(band, color=COLOR_FAIL, linestyle=':', label='±2% band')
    ax2.axhline(-band, color=COLOR_FAIL, linestyle=':')
    ax2.set_ylabel('Error (deg)')
    
    vel_rad = df['vel'] * np.pi / 180.0
    ax3.plot(df['time_s'], vel_rad, color=COLOR_KALMAN)
    ax3.set_ylabel('Velocity (rad/s)')
    ax3.set_xlabel('Time (s)')
    
    plt.tight_layout()
    out = OUTPUT_DIR / "fig_step_response_hw.png"
    plt.savefig(out)
    plt.close()
    return out

# FIGURE 4: Accuracy Errorbar
def gen_fig_accuracy_errorbar():
    print("Generating fig_accuracy_errorbar...")
    targets = np.array([0, 40, 80, 120])
    means = np.array([-0.026, 39.944, 79.971, 120.086])
    errors = np.array([-0.026, -0.056, -0.029, 0.086])
    stds = np.array([0.050, 0.053, 0.049, 0.038])
    
    colors = [COLOR_PASS if abs(e) <= 0.5 else COLOR_FAIL for e in errors]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(targets, errors, width=15, color=colors, alpha=0.8, yerr=stds, capsize=5, ecolor='black')
    ax.axhline(0.5, color=CRITERION_COLOR, linewidth=1.5, linestyle='--', label='±0.5° criterion (A1)')
    ax.axhline(-0.5, color=CRITERION_COLOR, linewidth=1.5, linestyle='--')
    ax.axhline(0, color='black', linewidth=0.8)
    
    ax.set_xticks(targets)
    ax.set_xlabel('Target Position (deg)')
    ax.set_ylabel('Position Error (deg)')
    ax.set_title('Position Accuracy (A1) — 10 Trials per Position')
    ax.set_ylim([-0.6, 0.6])
    
    for i, bar in enumerate(bars):
        status = 'PASS' if abs(errors[i]) <= 0.5 else 'FAIL'
        y_text = errors[i] + stds[i] + 0.05 if errors[i] >= 0 else errors[i] - stds[i] - 0.1
        ax.text(bar.get_x() + bar.get_width()/2, y_text, status, ha='center', va='center', fontsize=9)
        
    ax.legend(loc='upper left')
    
    textstr = 'Max Error = 0.100°\nCriterion: ≤ ±0.5°\nStatus: PASS'
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)
            
    out = OUTPUT_DIR / "fig_accuracy_errorbar.png"
    plt.savefig(out)
    plt.close()
    return out

# FIGURE 5: Repeatability Run Chart
def gen_fig_repeatability_runchart():
    print("Generating fig_repeatability_runchart...")
    files = sorted(list(DATA_DIR.glob("S4-REPEAT*.csv")))
    if not files:
        raise FileNotFoundError("S4-REPEAT*.csv not found")
        
    pos0 = []
    pos120 = []
    
    for f in files:
        df = safe_read_csv(f)
        if df is None: continue
        df['stable'] = df['vel'].abs() < 0.05
        df['block'] = (df['stable'] != df['stable'].shift()).cumsum()
        stable_blocks = df[df['stable']].groupby('block')
        
        for _, block in stable_blocks:
            last_pos = block['pos'].iloc[-1]
            if abs(last_pos) < 20:
                pos0.append(last_pos)
            elif abs(last_pos - 120) < 20:
                pos120.append(last_pos)
                
    pos0 = np.array(pos0)
    pos120 = np.array(pos120)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
    
    if len(pos0) > 0:
        cycles = np.arange(1, len(pos0)+1)
        mean0 = np.mean(pos0)
        ax1.scatter(cycles, pos0, s=20, color=COLOR_ENCODER, alpha=0.7)
        ax1.axhline(mean0, color=COLOR_TARGET, linestyle='--', label=f'Mean = {mean0:.3f}°')
        ax1.axhspan(mean0 - 0.1, mean0 + 0.1, color=COLOR_BAND, alpha=0.5, label='±0.1° criterion (A2)')
        ax1.axhline(mean0 - 0.1, color=CRITERION_COLOR, linewidth=1, linestyle='--')
        ax1.axhline(mean0 + 0.1, color=CRITERION_COLOR, linewidth=1, linestyle='--')
        ax1.set_ylabel('Position (deg)')
        ax1.set_title('Repeatability at ~0°')
        ax1.legend(loc='lower left')
        
        std0 = np.std(pos0, ddof=1) if len(pos0)>1 else 0
        maxdev0 = np.max(np.abs(pos0 - mean0))
        status0 = 'PASS' if maxdev0 <= 0.1 else 'FAIL'
        props0 = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=COLOR_PASS if status0=='PASS' else COLOR_FAIL)
        ax1.text(0.95, 0.95, f'σ = {std0:.3f}°\nMax dev = {maxdev0:.3f}°\nStatus: {status0}', transform=ax1.transAxes, 
                 fontsize=10, va='top', ha='right', bbox=props0)
                 
    if len(pos120) > 0:
        cycles = np.arange(1, len(pos120)+1)
        mean120 = np.mean(pos120)
        ax2.scatter(cycles, pos120, s=20, color=COLOR_ENCODER, alpha=0.7)
        ax2.axhline(mean120, color=COLOR_TARGET, linestyle='--', label=f'Mean = {mean120:.3f}°')
        ax2.axhspan(mean120 - 0.1, mean120 + 0.1, color=COLOR_BAND, alpha=0.5, label='±0.1° criterion (A2)')
        ax2.axhline(mean120 - 0.1, color=CRITERION_COLOR, linewidth=1, linestyle='--')
        ax2.axhline(mean120 + 0.1, color=CRITERION_COLOR, linewidth=1, linestyle='--')
        ax2.set_ylabel('Position (deg)')
        ax2.set_title('Repeatability at ~120°')
        ax2.set_xlabel('Cycle Number')
        
        std120 = np.std(pos120, ddof=1) if len(pos120)>1 else 0
        maxdev120 = np.max(np.abs(pos120 - mean120))
        status120 = 'PASS' if maxdev120 <= 0.1 else 'FAIL'
        props120 = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=COLOR_PASS if status120=='PASS' else COLOR_FAIL)
        ax2.text(0.95, 0.95, f'σ = {std120:.3f}°\nMax dev = {maxdev120:.3f}°\nStatus: {status120}', transform=ax2.transAxes, 
                 fontsize=10, va='top', ha='right', bbox=props120)
                 
    fig.suptitle('Repeatability Test (A2) — 65 Cycles', y=0.98)
    plt.tight_layout()
    out = OUTPUT_DIR / "fig_repeatability_runchart.png"
    plt.savefig(out)
    plt.close()
    return out

# FIGURE 6: Cycle Time
def gen_fig_cycle_timeline():
    print("Generating fig_cycle_timeline...")
    files = sorted(list(DATA_DIR.glob("cycle*.csv")))
    if not files:
        raise FileNotFoundError("cycle CSV not found")
        
    fig, axes = plt.subplots(len(files), 1, figsize=(10, 3.5*len(files)), sharex=True)
    if len(files) == 1:
        axes = [axes]
        
    for i, f in enumerate(files):
        df = safe_read_csv(f)
        ax = axes[i]
        
        df['is_moving'] = df['vel'].abs() > 0.2
        df['block'] = (df['is_moving'] != df['is_moving'].shift()).cumsum()
        
        moves = []
        stops = []
        for is_moving, block in df.groupby(['is_moving', 'block']):
            start_time = block['t_ms'].iloc[0] / 1000.0
            end_time = block['t_ms'].iloc[-1] / 1000.0
            duration = end_time - start_time
            if duration > 0.1:
                if is_moving:
                    moves.append((start_time, duration))
                else:
                    stops.append((start_time, duration))
                    
        if moves or stops:
            t0 = min([m[0] for m in moves] + [s[0] for s in stops])
            moves = [(m[0]-t0, m[1]) for m in moves]
            stops = [(s[0]-t0, s[1]) for s in stops]
            
        y_ticks = []
        y_labels = []
        y_pos = len(moves) + len(stops)
        
        all_blocks = sorted([('Move', m[0], m[1]) for m in moves] + [('Stop', s[0], s[1]) for s in stops], key=lambda x: x[1])
        
        move_count = 1
        stop_count = 1
        
        for btype, start, dur in all_blocks:
            if btype == 'Move':
                ax.barh(y_pos, width=dur, left=start, height=0.4, color=COLOR_ENCODER, align='center', label='Move' if move_count==1 else "")
                y_labels.append(f'Move {move_count}')
                move_count += 1
            else:
                ax.barh(y_pos, width=dur, left=start, height=0.4, color='#FF9800', align='center', label='Stop' if stop_count==1 else "")
                y_labels.append(f'Stop {stop_count}')
                stop_count += 1
            y_ticks.append(y_pos)
            y_pos -= 1
            
        total_time = max([m[0]+m[1] for m in moves] + [s[0]+s[1] for s in stops]) if (moves or stops) else 0
        
        ax.axvline(total_time, color=CRITERION_COLOR, linestyle='--', label=f'Run {i+1}: {total_time:.1f} s')
        ax.axvline(35.0, color='black', linestyle=':', label='Criterion: 35 s')
        
        ax.set_yticks(y_ticks)
        # only show label for some to avoid crowding if there are too many
        ax.set_yticklabels(y_labels, fontsize=8) 
        ax.set_title(f'Cycle Time Timeline — Run {i+1}')
        
        # Avoid legend warning if no lines
        if ax.get_legend_handles_labels()[1]:
            ax.legend(loc='lower right')
            
    axes[-1].set_xlabel('Time (s)')
    
    plt.tight_layout()
    out = OUTPUT_DIR / "fig_cycle_timeline.png"
    plt.savefig(out)
    plt.close()
    return out

if __name__ == "__main__":
    funcs = [
        gen_fig_step_response_hw,
        gen_fig_cycle_timeline
    ]
    
    for f in funcs:
        try:
            outpath = f()
            print(f"Saved: {outpath.name}")
        except Exception as e:
            print(f"WARNING: Failed to generate figure in {f.__name__}: {e}")
