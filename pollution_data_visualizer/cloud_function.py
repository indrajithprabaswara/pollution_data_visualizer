from pollution_data_visualizer.app import collect_all_data, TASKS_COLLECT_CALLED

def pubsub_collect(event, context):
    TASKS_COLLECT_CALLED.inc()
    collect_all_data(force=True)
    return 'ok'
