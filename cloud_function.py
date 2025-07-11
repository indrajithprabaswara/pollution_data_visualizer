from pollution_data_visualizer.app import collect_all_data, TASKS_COLLECT_CALLED

def run(event, context):
    """Entry point for Pub/Sub triggered Cloud Function."""
    TASKS_COLLECT_CALLED.inc()
    collect_all_data(force=True)
    return 'ok'
