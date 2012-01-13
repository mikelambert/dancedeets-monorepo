from logic import gprediction
from servlets import tasks

class GenerateTrainingDataHandler(tasks.BaseTaskFacebookRequestHandler):
    def get(self):
        gprediction.mr_generate_training_data(self.batch_lookup)
