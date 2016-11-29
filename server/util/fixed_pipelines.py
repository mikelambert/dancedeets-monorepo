from pipeline import pipeline

# The default base_path doesn't work on Managed VMs, so we override it here (and app.yaml).
# See https://github.com/GoogleCloudPlatform/appengine-pipelines/issues/57
class Pipeline(pipeline.Pipeline):
    def start(self,
        idempotence_key='',
        queue_name='default',
        base_path='/_pipeline',
        return_task=False,
        countdown=None,
        eta=None):
        super(Pipeline, self).start(
            idempotence_key=idempotence_key,
            queue_name=queue_name,
            base_path=base_path,
            return_task=return_task,
            countdown=countdown,
            eta=eta)
