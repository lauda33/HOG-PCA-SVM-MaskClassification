from google.colab import drive
drive.mount("/content/drive")

# I've downloaded the dataset from Kaggle, here is the link of the dataset: https://www.kaggle.com/niharika41298/withwithout-mask
import numpy as np
import PIL
from skimage.feature import hog
import cv2
import time
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
import warnings as wrn
wrn.filterwarnings('ignore')

# First, we should determine paths of images
test_mask = glob("/content/drive/MyDrive/archive/maskdata/maskdata/test/with_mask"+"/*")
test_without = glob("/content/drive/MyDrive/archive/maskdata/maskdata/test/without_mask"+"/*")

train_mask = glob("/content/drive/MyDrive/archive/maskdata/maskdata/train/with_mask"+"/*")
train_without = glob("/content/drive/MyDrive/archive/maskdata/maskdata/train/without_mask"+"/*")

# I'll concatenate all images to work with them easily, after preprocessing I'll split them
mask = train_mask + test_mask
without = train_without + test_without

print(len(mask))
print(len(without))

"""
Histogram of Gradients is a traditional feature description method.
It is a complex approach so you should learn it, I can't explain it in here.
"""


# We'll store labels and hog features in those lists
image_features = []
labels = []

start_time = time.time()

# Each iteration will be a class
for label,path in zip([0,1],[without,mask]):

  # And each iteration will be an another image path
  for image_path in path:

    img = np.asarray(PIL.Image.open(image_path))
    img = cv2.resize(img,(64,128))
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    # Histogram of Oriented Gradients, returns feature vectors
    img = hog(img,cells_per_block=(2,2))
    image_features.append(img)
    labels.append(label)

image_features = np.asarray(image_features)
labels = np.asarray(labels)

end_time = time.time()

print("This process took {} seconds".format(round(end_time-start_time,2)))

print("Shape of images",image_features.shape)
print("Shape of labels",labels.shape)

# Now we'll fit a PCA (Principal Component Analysis) model to make dimensionality reduction
"""
PCA is a statistical method that generally used in dimensionality reduction, it reducts dimensions of the data by keeping variance.
In our mission, we'll convert 3780d dataset to 100d dataset
"""
start_time = time.time()

pca = PCA(n_components=600)
pca_features = pca.fit_transform(image_features)

end_time = time.time()

print("This process just took {} seconds".format(round(end_time-start_time,2)))

sum(pca.explained_variance_ratio_)

# Now we have 600 features and we saved %94 of our data

x_train,x_test,y_train,y_test = train_test_split(pca_features,labels,random_state=42)

"""
SVM Support Vector Machines
Support Vector Machines is a machine learning approach that has a regressor and a classifier
In Linear Support Vector Machine Classifier, model fits n-lines to split classes to each other.
"""

start_time = time.time()

classifier = SVC()
classifier.fit(x_train,y_train)

print("Score of SVM classifier:",classifier.score(x_test,y_test))

y_pred = classifier.predict(x_test)

end_time = time.time()
print("This process took {} seconds".format(round(end_time-start_time,2)))

conf_matrix = confusion_matrix(y_pred=y_pred,y_true=y_test)

plt.subplots(figsize=(4,4))
plt.title("Confusion Matrix of Test Set")
sns.heatmap(conf_matrix,annot=True,linewidths=1.5,fmt=".1f")
plt.xlabel("Predicted Labels")
plt.ylabel("Actual Labels")
plt.show()

# Our model's accuracy is %83, not bad but good for starting

# Saving model
import pickle
with open("classifier.pickle",mode="wb") as F:
  pickle.dump(classifier,F)

# Saving Principal Component Analysis model 
with open("pca.pickle",mode="wb") as F:
  pickle.dump(pca,F)


# Now we need a function to predict an image

def predictImage(image_path):

  classifier = pickle.load(open("classifier.pickle",mode="rb"))
  pca = pickle.load(open("pca.pickle",mode="rb"))

  # Now let's process the image
  image = np.asarray(PIL.Image.open(image_path))
  image = cv2.resize(image,(64,128))
  image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
  hog_features = hog(image,cells_per_block=(2,2))

  pca_features = pca.transform(np.asarray([hog_features]))

  return classifier.predict(pca_features)[0]

# Now let's train this function

mask_path = "/content/drive/MyDrive/archive/maskdata/maskdata/train/with_mask/101-with-mask.jpg"
without_path = "/content/drive/MyDrive/archive/maskdata/maskdata/train/without_mask/0.jpg"

plt.imshow(PIL.Image.open(mask_path))
plt.title("Real Label {} | Predicted Label {}".format(1,predictImage(mask_path)))
plt.axis("off")
plt.show()

plt.imshow(PIL.Image.open(without_path))
plt.title("Real Label {} | Predicted Label {}".format(0,predictImage(without_path)))
plt.axis("off")
plt.show()

# Thanks for your attention
