rule event_selection:
    input:
        analysis_config=ANALYSIS_CONFIG
    output:
        summary=EVENT_SELECTION_SUMMARY,
        validation=EVENT_SELECTION_VALIDATION
    params:
        input_dir=INPUT_DIR
    log:
        f"{WORK_DIR}/logs/event_selection.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/event_selection.py"
