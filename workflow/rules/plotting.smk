rule plotting:
    input:
        event_selection=EVENT_SELECTION_SUMMARY,
        categorization=CATEGORIZATION_SUMMARY,
        statistics=STATISTICS_SUMMARY
    output:
        summary=PLOT_SUMMARY,
        workflow_summary=WORKFLOW_SUMMARY,
        validation=WORKFLOW_VALIDATION,
        region_table=REGION_TABLE,
        region_plot_pdf=REGION_PLOT_PDF,
        region_plot_png=REGION_PLOT_PNG
    log:
        f"{WORK_DIR}/logs/plotting.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/plotting.py"
