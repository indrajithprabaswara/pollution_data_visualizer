from pollution_data_visualizer.app import collect_all_data

def pubsub_collect(event, context):
    collect_all_data(force=True)
    return 'ok'
