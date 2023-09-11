Por supuesto, aquí está tu README actualizado:

---

# 🐉 python-dbuniverse-downloader

## 🌟 Overview

A versatile PDF downloader for the beloved Dragon Ball comic hosted on [Dragon Ball Multiverse](http://dragonball-multiverse.com). A huge shoutout and gratitude to the creators and maintainers of the Dragon Ball Multiverse website for their exceptional work and content! 💖

With the magic of GitHub Actions, every time this repo springs into action, the latest PDFs of all collections are magically conjured for your convenience! 🪄✨

## 🌈 Features:

- 📸 Download individual pages from various collections of the Dragon Ball Multiverse Universe.
- 🎨 Convert images to PDFs, supporting both jpg and png formats!
- 📘 Merge individual PDFs into one epic document for uninterrupted reading.
- ⚡ Harnesses the power of multithreading to make downloads and conversions at lightning speed!

## 🚀 Installation

### 1. Get the codebase

Clone the project repository:

```bash
$ git clone https://github.com/0x10-z/python-dbuniverse-downloader
$ cd python-dbuniverse-downloader
```

### 2. Install dependencies

```bash
$ pip install -r requirements.txt
```

⚠️ **For Linux users**:

You might need to install some extra dependencies. Here's how:

```bash
$ sudo apt-get install zlib1g-dev libxml2 libxml2-dev libxslt-dev build-essential python-dev
```

## 📘 How to use it?

To download chapters from the [Dragon Ball Multiverse comic](http://www.dragonball-multiverse.com/es/chapters.html):

```bash
$ python dbmultiverse.py <collection_name>
```

```bash
$ python dbmultiverse.py dbmultiverse
```

**Available Collections**:

- `dbmultiverse`: Main DB Multiverse series.
- `namekseijin`: Namekseijin Densetsu series.
- `dbm-colors`: DBMultiverse Colors series.
- `strip`: Minicomic series.
- `chibi-son-bra`: Chibi Son Bra did her best series.

Sit back and relax ☕️. Once the program finishes, dive right into the comic! 📖

## 🤓 How it works:

1. **Fetching the Latest Chapter:** It first identifies the latest chapter to ensure all available ones are downloaded.
2. **Image Download:** Each page is downloaded and stashed into a treasure chest named 'images'.
3. **Image Processing:** Images that exceed a certain width are resized with magic.
4. **Conversion to PDF:** All images are transformed into glorious PDFs.
5. **Merging PDFs:** All the PDFs are combined to form a single epic document.

## 📜 Changelog

### 0.3

📅 **11th Sept 2023**

- 🌪️ Uses ThreadPoolExecutor for parallel processing, so it's faster than Frieza!
- 🌟 Latest version of PDF and libraries updated.
- 🎨 More comprehensive collection support added.
- 📌 Use of `xpath`

### 0.2

📅 **26th Oct 2014**

- 🎉 First release.

📅 **15th Oct 2017**

- 🐍 Added Python3 support.

**Future improvements**

- 📌 Transition from `cssselect` to `xpath` for more flexibility.

---

Happy reading, fellow Saiyans! 🚀🌌

---
