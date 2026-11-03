# Machine learning

## Preparing the dataset

Place images of products class in its corresponding directory:

`machine_learning/dataset/raw/{class_name}`

```powershell
python -m machine_learning.prepare_dataset
```

## training

```powershell
python -m machine_learning.train_model
```

## Datasets

| Category   | Datasets                                                        | Sources                                                                                                                                                                                                                                                          | Additional information                                      |
| ---------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Apple      | `apples-fvpl5`                                                  | [apples-fvpl5](https://huggingface.co/datasets/Francesco/apples-fvpl5), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360)                                                                                                                    | Used data from the linked datasets and a set of own photos. |
| Red grapes | `Fruits-30`, `fruits-360`, `red_grapes_and_leaves_segmentation` | [Fruits-30](https://huggingface.co/datasets/VinayHajare/Fruits-30), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360), [red_grapes_and_leaves_segmentation](https://huggingface.co/datasets/Project-AgML/red_grapes_and_leaves_segmentation) | Used data from the linked datasets.                         |
| Lemon      | `Fruits-30`, `fruits-360`                                       | [Fruits-30](https://huggingface.co/datasets/VinayHajare/Fruits-30), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360)                                                                                                                        | Used data from the linked datasets.                         |
| Pear       | `Fruits-30`, `fruits-360`                                       | [Fruits-30](https://huggingface.co/datasets/VinayHajare/Fruits-30), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360)                                                                                                                        | Used data from the linked datasets.                         |
| Plum       | `Fruits-30`, `fruits-360`                                       | [Fruits-30](https://huggingface.co/datasets/VinayHajare/Fruits-30), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360)                                                                                                                        | Used data from the linked datasets.                         |
| Tomato     | `Fruits-30`, `fruits-360`                                       | [Fruits-30](https://huggingface.co/datasets/VinayHajare/Fruits-30), [fruits-360](https://huggingface.co/datasets/PedroSampaio/fruits-360)                                                                                                                        | Used data from the linked datasets.                         |

## Installing dependencies

```powershell
python -m pip install datasets pillow pyarrow
```
