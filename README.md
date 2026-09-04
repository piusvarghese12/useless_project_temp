<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />



# Object Idenifier 🎯


## Basic Details
link : https://uselessprojecttemp-mwhredrbifpvkdnbnekkul.streamlit.app/
### Team Name: Done


### Team Members
- Solo Lead: Pius Varghese - Model Engineering College, Thrikkakara, Ernakulam

### Project Description
An over-engineered PyTorch Multimodal AI System utilizing ResNet-50 and DistilBERT Two-Tower Contrastive Neural Networks that asks you to upload an image and type what it is, only to process it through complex 256-dimensional vector embeddings and tell you the exact same thing back. Mind = Blown

### The Problem (that doesn't exist)
Humans constantly look at everyday objects (like a cat, a coffee mug, or running shoes) and suffer from the overwhelming existential dread of not having a deep learning neural network confirm what they literally just typed into an input box 2 seconds ago.

### The Solution (that nobody asked for)
We built a full Two-Tower Contrastive Neural Network architecture (ResNet-50 visual backbone + DistilBERT text transformer projected to a 256-dim L2-normalized embedding space with temperature-scaled cosine softmax math) that takes your image, reads your input label, computes dot-product matrix similarity, and displays what you typed with cool pixel sunglasses.


## Technical Details
### Technologies/Components Used
For Software:
- Languages used: Python 3.11 / 3.12
- Frameworks used: PyTorch, Streamlit
- Libraries used: torchvision, Pillow (PIL), open_clip_torch, NumPy, Pandas
- Tools used: uv package manager, Git


For Hardware:
- None (Software-only project)

### Implementation
For Software:
# Installation
```bash

# Run
# Clone the repository
git clone https://github.com/your-username/multimodal-product-verifier.git
cd multimodal-product-verifier

# Create virtual environment and install dependencies
uv venv .venv
.venv\Scripts\activate
uv pip install -r requirements.txt

### Project Documentation
For Software:

# Screenshots (Add at least 3)
![Screenshot1] Screenshot1.png
Uploading an image file or selecting a sample product with instant preview
![Screenshot2] Screenshot2.png
Typing what the object is (Human Input & Two-Tower contrastive evaluation
![Screenshot3] Screenshot3.png
The Shocker Result showing the object name with cool pixel sunglasses and model confidence

# Diagrams
+-------------------+        +----------------------+
|  Uploaded Image   |        | User Input Object    |
+---------+---------+        +----------+-----------+
          |                             |
          v                             v
+---------+---------+        +----------+-----------+
|  ResNet-50 Backbone|       | DistilBERT Backbone  |
+---------+---------+        +----------+-----------+
          |                             |
          v                             v
+---------+---------+        +----------+-----------+
| Linear FC (2048->256)|     | Linear FC (768->256)|
+---------+---------+        +----------+-----------+
          |                             |
          v                             v
+---------+---------+        +----------+-----------+
| L2 Normalization  |        | L2 Normalization     |
+---------+---------+        +----------+-----------+
          |                             |
          +--------------+--------------+
                         |
                         v
            +------------+------------+
            | Dot-Product Similarity  |
            +------------+------------+
                         |
                         v
            +------------+------------+
            | Temperature Softmax (10x)|
            +-------------------------+

---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)



