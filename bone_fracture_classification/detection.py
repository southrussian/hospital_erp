import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import torch
import torch.utils.data as data
import torchvision.datasets as datasets
from torchvision.transforms import v2
import torchvision.models as models
import matplotlib.pyplot as plt
import os
import torch.nn as nn
from torch.nn.modules.loss import BCEWithLogitsLoss
from torch.optim import lr_scheduler
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import Image
import torch.nn.functional as F
import math


def get_image_size(image_path):
    """Gets the size of an image in pixels.
    Args:
    image_path: The path to the image file.
    Returns:
    A tuple of (width, height) in pixels.
    """

    with open(image_path, 'rb') as f:
        image = Image.open(f)
        width, height = image.size
        return width, height


def get_image_sizes(image_folder_path):
    image_sizes = []
    for image_file in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, image_file)
        width, height = get_image_size(image_path)
        image_sizes.append((width, height))
    return image_sizes


def get_image_stats(path, categories):
    size_dict = {}
    for category in categories:
        image_sizes = get_image_sizes(os.path.join(path, category))
        for size in image_sizes:
            size_dict[size] = size_dict.get(size, 0) + 1
    sorted(size_dict.items(), key=lambda kv: -kv[1])
    return size_dict


DATA_PATH = "Bone_Fracture_Binary_Classification"
TRAIN_DATA_PATH = os.path.join(DATA_PATH, 'train')
TEST_DATA_PATH = os.path.join(DATA_PATH, 'test')
VAL_DATA_PATH = os.path.join(DATA_PATH, 'val')
MODEL_PATH = "model/model.pt"

size_dict = get_image_stats(TRAIN_DATA_PATH, ["fractured", "not fractured"])
print(size_dict)

image_height, image_width = list(size_dict.keys())[0]
print(image_height, image_width)


def get_category_distribution(path, categories):
    result = {}
    for category in categories:
        result[category] = len(os.listdir(os.path.join(path, category)))

    return result


categories = ['fractured', 'not fractured']
train_dist = get_category_distribution(TRAIN_DATA_PATH, categories)
test_dist = get_category_distribution(TEST_DATA_PATH, categories)
val_dist = get_category_distribution(VAL_DATA_PATH, categories)

print(f'Train Distribution: {train_dist}')
print(f'Test Distribution: {test_dist}')
print(f'Val Distribution: {val_dist}')

BATCH_SIZE = 64
TRANSFORM_IMG = v2.Compose([
    v2.ToImage(),
    v2.ToDtype(torch.uint8, scale=True),
    v2.Resize((128, 128)),
    v2.ToDtype(torch.float32, scale=True),  # Normalize expects float input
    v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

TRAIN_TRANSFORM_IMG = v2.Compose([
    v2.ToImage(),
    v2.ToDtype(torch.uint8, scale=True),
    v2.RandomResizedCrop(size=(128, 128), antialias=True),
    v2.RandomRotation(90),
    v2.RandomHorizontalFlip(0.5),
    v2.ToDtype(torch.float32, scale=True),  # Normalize expects float input
    v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

train_data = datasets.ImageFolder(root=TRAIN_DATA_PATH, transform=TRAIN_TRANSFORM_IMG)
train_data_loader = data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
test_data = datasets.ImageFolder(root=TEST_DATA_PATH, transform=TRANSFORM_IMG)
test_data_loader = data.DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=True)
val_data = datasets.ImageFolder(root=VAL_DATA_PATH, transform=TRANSFORM_IMG)
val_data_loader = data.DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=True)

print(train_data.class_to_idx)
print(test_data.class_to_idx)
print(val_data.class_to_idx)


def matplotlib_imshow(img, one_channel=False):
    plt.autoscale()
    if one_channel:
        img = img.mean(dim=0)
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    if one_channel:
        plt.imshow(npimg, cmap="Greys")
    else:
        plt.imshow(np.transpose(npimg, (1, 2, 0)))


def plot_data(features, labels):
    if len(labels) > 16:
        plot_data(features[:16], labels[:16])
        return

    n = len(labels)
    cols = 4
    rows = n // cols

    if n != rows * cols:
        rows = rows + 1

    fig = plt.figure(figsize=(rows, cols))
    fig.set_tight_layout(True)
    for idx in np.arange(n):
        img = features[idx].squeeze()
        label = "Fractured" if labels[idx] == 0 else "Not Fractured"
        row = idx // 4
        col = idx % 4
        ax = fig.add_subplot(rows, cols, idx + 1, xticks=[], yticks=[])
        matplotlib_imshow(img)
        ax.set_title(label,
                     color=("green" if labels[idx] == 0 else "red"), fontsize=8)
    return fig


train_features, train_labels = next(iter(train_data_loader))
print(f"Feature batch shape: {train_features.size()}")
print(f"Labels batch shape: {train_labels.size()}")
plot_data(train_features, train_labels)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.resnet50(pretrained=True)

#   freeze all params
for name, params in model.named_parameters():
    if 'bn' not in name:
        params.requires_grad_ = False

nr_filters = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(nr_filters, 512),
    nn.ReLU(),
    nn.Linear(512, 2))
model.to(device)

print(model)


def get_next(iterator, data_loader):
    try:
        x, y = next(iterator)
    except StopIteration:
        iterator = iter(data_loader)
        x, y = next(iterator)
    return x, y, iterator


@torch.no_grad()
def estimate_loss(model, eval_iters, loss_fn, data_loaders={}):
    out = {}
    model.eval()  # set the mode to evaluation

    for label, data_loader in data_loaders.items():
        losses = torch.zeros(eval_iters)
        iterator = iter(data_loader)
        for k in range(eval_iters):
            x, y, iterator = get_next(iterator, data_loader)
            x = x.to(device)
            y = y.unsqueeze(1).float()
            y = y.to(device)
            pred = model(x)
            loss = loss_fn(pred, y)
            losses[k] = loss.item()
        out[label] = losses.mean()
    model.train()
    return out


def find_lr(model, optimizer, loss_fn, train_dl, init_lr=1e-8, final_lr=10.0, device='cpu'):
    step = (final_lr / init_lr) ** (1 / (len(train_dl) - 1))
    best_loss = 0.0
    losses = []
    log_lr = []

    batch_num = 0
    model.train()
    for batch in train_dl:
        current_lr = init_lr * ((step) ** batch_num)
        optimizer.param_groups[0]["lr"] = current_lr
        optimizer.zero_grad()
        inputs, targets = batch
        inputs = inputs.to(device)
        targets = targets.to(device)
        predictions = model(inputs)
        loss = loss_fn(predictions, targets)
        loss.backward()
        optimizer.step()
        curr_loss = loss.data.item()
        if batch_num != 0 and curr_loss > 4 * best_loss:
            return log_lr[10:-5], losses[10:-5]

        if batch_num == 0 or loss < best_loss:
            best_loss = loss

        losses.append(curr_loss)
        log_lr.append(math.log10(current_lr))
        batch_num = batch_num + 1

    return log_lr[10:-5], losses[10:-5]


def train(model, optimizer, loss_fn, train_dl, val_dl, epochs=10, device="cpu"):
    train_losses = []
    val_losses = []
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch in train_dl:
            optimizer.zero_grad()
            inputs, targets = batch
            inputs = inputs.to(device)
            targets = targets.to(device)
            predictions = model(inputs)
            loss = loss_fn(predictions, targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.data.item()
        train_loss = train_loss / len(train_dl)
        train_losses.append(train_loss)

        model.eval()
        val_loss = 0.0
        num_correct = 0
        num_examples = 0
        for batch in val_dl:
            inputs, targets = batch
            inputs = inputs.to(device)
            targets = targets.to(device)
            predictions = model(inputs)
            loss = loss_fn(predictions, targets)
            val_loss += loss.data.item()
            correct = torch.eq(torch.max(F.softmax(predictions), dim=1)[1], targets)
            num_correct += torch.sum(correct).item()
            num_examples += correct.shape[0]
        val_loss = val_loss / len(val_dl)
        val_losses.append(val_loss)

        print(
            f'Epoch: {epoch}, train_loss: {train_loss:.2f}, val_loss: {val_loss:.2f}, accuracy: {num_correct / num_examples:.4f}')
    return train_losses, val_losses


print(len(train_data_loader))

learning_rate = 0.001
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=learning_rate)

log_lr, losses = find_lr(model, optimizer, loss_fn, train_data_loader, init_lr=1e-8, final_lr=1e-1, device=device)
plt.plot(log_lr, losses)

print(log_lr)

epochs = 15
lr = 1e-2
optimizer = torch.optim.Adam(model.fc.parameters(), lr=learning_rate)
train_losses, val_losses = train(model, optimizer, loss_fn, train_data_loader, val_data_loader, epochs, device)

x = range(1, len(train_losses) + 1)
plt.plot(x, train_losses, label='train_loss')
plt.plot(x, val_losses, label='val_loss')
plt.legend()
plt.show()

model.eval()
val_loss = 0.0
num_correct = 0
num_examples = 0
for batch in test_data_loader:
    inputs, targets = batch
    inputs = inputs.to(device)
    targets = targets.to(device)
    predictions = model(inputs)
    loss = loss_fn(predictions, targets)
    val_loss += loss.data.item()
    correct = torch.eq(torch.max(F.softmax(predictions, dim=1), dim=1)[1], targets)
    num_correct += torch.sum(correct).item()
    num_examples += correct.shape[0]
val_loss = val_loss / len(test_data_loader)
val_losses.append(val_loss)

print(val_loss)
print(num_correct/num_examples)
