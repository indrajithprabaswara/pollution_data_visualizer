from pollution_data_visualizer.app import collect_all_data

def run(event, context):
    """Entry point for Pub/Sub triggered Cloud Function."""
    collect_all_data(force=True)
    return 'ok'
