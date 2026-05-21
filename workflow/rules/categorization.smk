rule categorization:
    input:
        analysis_config=ANALYSIS_CONFIG,
        event_selection=EVENT_SELECTION_SUMMARY
    output:
        summary=CATEGORIZATION_SUMMARY,
        validation=f"{WORK_DIR}/results/validation/categorization.json"
    log:
        f"{WORK_DIR}/logs/categorization.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/categorization.py"
