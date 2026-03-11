# ⚡ NeuralChat — Local AI Interface for Ollama

> A sleek, feature-rich Streamlit chat interface for locally running LLMs via Ollama. No cloud. No API keys. Just your machine.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?style=flat-square&logo=streamlit)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🖼️ Preview

| Dark Mode | Light Mode |
|-----------|------------|
| Deep navy UI with glowing accents | Clean indigo-white with soft shadows |

---

## ✨ Features

- 🌙☀️ **Dark / Light theme** — toggle instantly from the sidebar
- 💬 **Multi-session chat history** — create, switch, rename, and delete conversations
- ⚡ **Real-time streaming** — token-by-token response with live typing cursor
- 🤖 **Auto model detection** — dropdown auto-populates with all locally installed Ollama models
- 🛠️ **Configurable settings** — temperature, max tokens, and custom system prompt per session
- 📝 **Smart auto-titles** — sessions title themselves from your first message
- 📊 **Session stats** — turn count, average response time, total word count
- 💾 **Export chat** — download any conversation as a `.txt` file
- 🟢 **Live connection status** — animated pulse indicator shows Ollama availability
- 🔢 **Character counter** — real-time count in the input box

---

## 🚀 Quick Start

### 1. Install Ollama
Download from [ollama.com](https://ollama.com) and pull a model:
```bash
ollama pull llama3.2       # recommended
# or: mistral, phi3, gemma3, codellama, etc.
```

### 2. Start Ollama
```bash
ollama serve
```

### 3. Clone & Set Up
```bash
git clone https://github.com/YOUR_USERNAME/neuralchat.git
cd neuralchat

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Run the App
```bash
streamlit run app.py
```
Open your browser at **http://localhost:8501**

---

## 📦 Requirements

```
streamlit>=1.32.0
requests>=2.31.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🗂️ Project Structure

```
neuralchat/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # You're here
```

---

## ⚙️ Configuration

All settings are accessible from the sidebar at runtime — no config files needed.

| Setting | Default | Description |
|---|---|---|
| Model | Auto-detected | Any model installed via Ollama |
| Temperature | 0.72 | Creativity vs. focus (0 = precise, 2 = wild) |
| Max Tokens | 1024 | Maximum length of each response |
| System Prompt | Helpful assistant | Shapes the AI's personality and behavior |

---

## 🧠 Supported Models

Any model available through Ollama works out of the box. Popular picks:

| Model | Size | Best For |
|---|---|---|
| `llama3.2` | ~2GB | General purpose |
| `mistral` | ~4GB | Reasoning & analysis |
| `phi3` | ~2.3GB | Fast, lightweight tasks |
| `codellama` | ~4GB | Code generation |
| `gemma3` | ~3GB | Multimodal tasks |

---

## 🛠️ Troubleshooting

**Ollama shows "Offline" in the UI**
```bash
ollama serve   # run this in a separate terminal
```

**No models in the dropdown**
```bash
ollama pull llama3.2
```

**Port conflict**
```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
# Then update OLLAMA_BASE in app.py to match
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push and open a PR

---

## 📄 License

MIT © [Hamama Komal](https://github.com/Hamama-Komal/)

---

<div align="center">
  Built with ❤️ using <a href="https://streamlit.io">Streamlit</a> + <a href="https://ollama.com">Ollama</a> · Runs 100% on your machine
</div>
