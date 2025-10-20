"""
train_cnn_model.py
Train a CNN (MobileNetV2) for Maize & Plantain Leaf Disease Classification
"""

import os
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import joblib

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\raw\Maize_Plantain"
MODEL_PATH = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\models\disease_model.h5"
ENCODER_PATH = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\models\label_encoder.pkl"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20  # you can increase later once verified
# -----------------------------

# Data generators (with augmentation)
datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
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

# Save label encoder mapping
label_map = train_ds.class_indices
joblib.dump(label_map, ENCODER_PATH)
print(f"✅ Label encoder saved at {ENCODER_PATH}")
print("📚 Classes:", label_map)

# -----------------------------
# BUILD MODEL
# -----------------------------
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze base layers (transfer learning)
for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.4)(x)
predictions = Dense(train_ds.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Compile
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# -----------------------------
# TRAINING
# -----------------------------
checkpoint = ModelCheckpoint(MODEL_PATH, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[checkpoint, early_stop]
)

# -----------------------------
# SAVE MODEL
# -----------------------------
model.save(MODEL_PATH)
print(f"✅ Model saved at {MODEL_PATH}")

# Evaluate
loss, acc = model.evaluate(val_ds)
print(f"📊 Final Validation Accuracy: {acc*100:.2f}%")
