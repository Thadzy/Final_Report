import re
import sys

missing = [
    "fig:sys_arch", "subsec:mech_arch", "subsec:elec_arch", "subsec:sysid", "subsec:pid_design",
    "subsec:joystick_integration", "subsec:modbus_integration", "eq:armature_voltage", "subsec:kalman_filter",
    "tab:pid_gains_hw", "eq:pid_velocity", "tab:zvd_params", "eq:zvd_transfer_function", "eq:state_space_ct",
    "eq:rod_wn_num", "subsec:zv_shaping", "eq:anti_windup", "subsec:drivetrain_arch", "fig:mech_cad",
    "tab:shaft_summary", "subsec:shaft_calc", "fig:locked_rotor_setup", "subsec:matlab_sysid", "eq:kvl_locked",
    "subsec:filtfilt", "eq:butter_atten", "fig:filtfilt_concept", "fig:preprocessing_validation", "eq:ABCD_matrices",
    "tab:chirp_config", "tab:crossval_fit", "fig:crossval_results", "eq:mechanical_ode", "sec:dc_motor_model",
    "fig:cascade_pid_block_ch3", "eq:Gvel_num", "eq:electrical_ode", "eq:ia_reduced", "eq:Kpp", "eq:Kiv", "eq:Kpv",
    "subsec:cascade_pid", "eq:tustin_sub", "eq:Cv_ct", "eq:bw_sep", "subsec:rod_dynamics", "eq:rod_eom",
    "eq:rod_natural_freq", "fig:zvd_sensitivity", "eq:zv_amplitudes", "eq:rod_wn_ch3", "eq:zvd_K", "eq:zvd_A1",
    "eq:zvd_A2", "eq:zvd_A3", "eq:zvd_delays", "fig:zvd_rod_response", "subsec:scurve", "eq:scurve_tv",
    "eq:scurve_ta", "eq:scurve_tj", "fig:scurve_single_profile", "fig:scurve_scenario2", "fig:scurve_scenario1",
    "tab:base_parts", "tab:arm_parts", "tab:encoder_parts", "tab:bom", "fig:block_diagram_wiring",
    "fig:power_architecture", "tab:firmware_modules", "fig:application_fsm", "eq:zvd_impl", "tab:pid_gains",
    "fig:system_architecture", "fig:firmware_flow", "ch:design", "tab:chirp_results", "tab:zvd_sim_summary",
    "subsec:sensor_test", "sec:subsystem_test", "sec:performance", "tab:vnv_matrix"
]

with open("labels.txt", "r") as f:
    defined_labels = [re.search(r'\\label{(.*?)}', line).group(1) for line in f if re.search(r'\\label{(.*?)}', line)]

for label in missing:
    if label in defined_labels:
        print(f"DEFINED: {label} (Will resolve on rerun)")
    else:
        print(f"MISSING: {label}")
