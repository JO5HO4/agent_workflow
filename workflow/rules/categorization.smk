rule categorization:
    input:
        analysis_config=ANALYSIS_CONFIG,
        event_selection=EVENT_SELECTION_SUMMARY
    output:
        summary=CATEGORIZATION_SUMMARY,
        validation=CATEGORIZATION_VALIDATION
    log:
        f"{WORK_DIR}/logs/categorization.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/categorization.py"
