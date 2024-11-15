import auth
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import choices

# Define labeling interface
label_config = LabelInterface.create({
    'text': 'Text',
    'label': choices(['Positive', 'Negative'])
})
# Create a project with the specified title and labeling configuration
project = ls.projects.create(
    title='Text Classification',
    label_config=label_config
)