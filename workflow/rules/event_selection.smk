rule event_selection:
    input:
        analysis_config=ANALYSIS_CONFIG,
        data=lambda wildcards: DATA_FILES[wildcards.file_id]
    output:
        summary=EVENT_SELECTION_FILE_SUMMARY,
        validation=EVENT_SELECTION_FILE_VALIDATION
    params:
        file_id=lambda wildcards: wildcards.file_id
    log:
        f"{WORK_DIR}/logs/event_selection/{{file_id}}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/event_selection.py"


rule merge_event_selection:
    input:
        summaries=expand(EVENT_SELECTION_FILE_SUMMARY, file_id=DATA_FILE_IDS),
        validations=expand(EVENT_SELECTION_FILE_VALIDATION, file_id=DATA_FILE_IDS)
    output:
        summary=EVENT_SELECTION_SUMMARY,
        validation=EVENT_SELECTION_VALIDATION
    log:
        f"{WORK_DIR}/logs/merge_event_selection.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/merge_event_selection.py"
