import auth
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import choices

# Define labeling interface
label_config = LabelInterface.create({
    'text': 'Text',
    'label': choices(['Positive', 'Negative'])
})
# Create a project with the specified title and labeling configuration
project = auth.ls.projects.create(
    title='Text Classification',
    label_config=label_config
)

from label_studio_sdk.label_interface.objects import PredictionValue

# this returns the same `LabelInterface` object as above
li = ls.projects.get(id=project.id).get_label_interface()

# by specifying what fields to `include` we can speed up task loading
for task in ls.tasks.list(project=project.id, include=["id"]):
    task_id = task.id
    prediction = PredictionValue(
        # tag predictions with specific model version string
        # it can help managing multiple models in Label Studio UI
        model_version='my_model_v1',
        # define your labels here
        result=[
            li.get_control('label').label(['Positive']),
            # ... add more labels if needed
        ]
    )
    ls.predictions.create(task=task_id, **prediction.model_dump())
