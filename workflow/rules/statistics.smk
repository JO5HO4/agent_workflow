rule statistics:
    input:
        analysis_config=ANALYSIS_CONFIG,
        categorization=CATEGORIZATION_SUMMARY
    output:
        summary=STATISTICS_SUMMARY,
        validation=f"{WORK_DIR}/results/validation/statistics.json"
    log:
        f"{WORK_DIR}/logs/statistics.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/statistics.py"
