
--------------------------------------------------------------------------------

English | [Русский](./README_ru.md) 

[![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](LICENSE)


# [WIP] Clinically validated annotated dataset of cystoscopy videos with bladder cancer

Repository of [paper](https://doi.org/10.5281/zenodo.19002839) with validated dataset of cystoscopy videos with bladder cancer

## 0. Prepare environment
Install [pypoetry](https://python-poetry.org/docs/) and install packages^
```bash
poetry install
```
Run `poetry env activate` to get script for virtual environment activation. Copy and run it in shell.

## 1. Download data
Assuming OS is linux distribution, script below will install `zenodo_get` utility and download data:
```bash
pip install zenodo_get
mkdir archive/
zenodo_get -o archive 19002839
unzip archive/videos.zip -d archive
```

## 2. Generate samples
To verify data visually, we added script for overlaying annotations on video samples. 
To generate video with bounding boxes run script:
```bash
python generate_video.py
```

## Video samples

https://github.com/user-attachments/assets/73397afb-ad84-45bd-a722-394f36c2f77a

https://github.com/user-attachments/assets/12490ebe-28f6-4e6b-8861-673fd531fed6



## Citation
```
@Article{Lekarev2026,
  title={Clinically validated annotated dataset of cystoscopy videos with bladder cancer},
  author={Lekarev, V. Yu.},
  doi={10.5281/zenodo.19002839},
  month     = Feb,
  year={2026}
}
```

## License

This code is distributed under an [APACHE-2.0 LICENSE](LICENSE).
