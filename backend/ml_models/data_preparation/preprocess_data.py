import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------- CONFIG ----------
DATA_DIR = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\raw\Maize_Plantain"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
# ----------------------------

datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    validation_split=0.2,
    rotation_range=25,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True
)

train_ds = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset='training',
    class_mode='categorical'
)

val_ds = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset='validation',
    class_mode='categorical'
)

print(f"✅ Loaded {train_ds.samples} training images and {val_ds.samples} validation images.")
print("📚 Classes:", train_ds.class_indices)
