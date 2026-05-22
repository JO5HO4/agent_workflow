rule statistics:
    input:
        analysis_config=ANALYSIS_CONFIG,
        categorization=CATEGORIZATION_SUMMARY
    output:
        summary=STATISTICS_SUMMARY,
        validation=STATISTICS_VALIDATION
    log:
        f"{WORK_DIR}/logs/statistics.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/statistics.py"
