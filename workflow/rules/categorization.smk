rule categorization:
    input:
        analysis_config=ANALYSIS_CONFIG,
        event_selection=EVENT_SELECTION_FILE_SUMMARY
    output:
        summary=CATEGORIZATION_FILE_SUMMARY,
        validation=CATEGORIZATION_FILE_VALIDATION
    log:
        f"{WORK_DIR}/logs/categorization/{{file_id}}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/categorization.py"


rule merge_categorization:
    input:
        analysis_config=ANALYSIS_CONFIG,
        summaries=expand(CATEGORIZATION_FILE_SUMMARY, file_id=DATA_FILE_IDS),
        validations=expand(CATEGORIZATION_FILE_VALIDATION, file_id=DATA_FILE_IDS)
    output:
        summary=CATEGORIZATION_SUMMARY,
        validation=CATEGORIZATION_VALIDATION
    log:
        f"{WORK_DIR}/logs/merge_categorization.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/merge_categorization.py"
