# ⚔️ Chronicles of the Forgotten Realm

> *A fully-featured solo fantasy tabletop RPG rules text RPG powered by Google Gemini AI, built entirelybusing Termux and Streamlit.*

---

## 🎮 What this is:

Chronicles of the Forgotten Realm is a solo tabletop RPG experience that runs entirely in your browser. An AI Dungeon Master powered by Google Gemini narrates a fully procedurally generated fantasy world, enforces modern tabletop RPG rulese, manages combat, tracks your character, and responds dynamically to every action you take.

No app store. No subscription. Just you, your phone, and an adventure.

---

## ✨ Features

- 🐉 **AI Dungeon Master** — Full narrative DM powered by Gemini, enforcing modern tabletop ruleset
- 🧝 **Character Creation** — Choose species, class, subclass, background, skills and proficiencies
- ⚔️ **Loadout System** — Class-specific starting gear, weapons, armor, spells and cantrips
- 🎲 **Animated Dice Roller** — d4 through d20 with roll animations sent directly to the DM
- ❤️ **HP & Combat Tracking** — Live Combat HUD with enemy HP bars, attacks and conditions
- 👤 **Companion System** — Up to 2 traveling companions with their own HP and relationships
- 📔 **Hero's Journal** — Write your own notes and lore throughout the campaign
- 🔮 **Oracle Engine** — Yes/No fate dice for creative storytelling decisions
- 🌙 **Short & Long Rest** — Full resource recovery mechanics
- ⭐ **Level Up System** — AI-guided level up cards with class features and spell slots
- 💾 **Autosave & Restore** — Campaign automatically saved and restored on server restart
- 📤 **Export System** — Download your save as JSON or your adventure log as Markdown
- 💀 **Death Screen** — Choose to restart, introduce a successor, or play as your companion
- 🖼️ **AI Scene Images** — Auto-generated scene illustrations via Pollinations AI
- 📱 **Mobile First** — Designed and built entirely on Android via Termux

---

## 📋 Requirements

- Python 3.13+
- A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com)
- Internet connection

---

## 🚀 Setup & Installation

**1. Clone the repository**

git clone https://github.com/ParamGGX/solo-dnd-multi.git
cd solo-dnd-multi

**2. Install dependencies**

pip install -r requirements.txt

**3. Add your API key**

Create a file called api_key.txt in the project folder and paste your Gemini API key inside it:

echo "your_api_key_here" > api_key.txt

**4. Run the app**

streamlit run app.py

**5. Open in browser**

Navigate to http://localhost:8501 in your browser.

---

## 📱 Running on Android (Termux)

pkg install python git -y
pip install streamlit requests
git clone https://github.com/ParamGGX/solo-dnd-multi.git
cd solo-dnd-multi
echo "your_api_key_here" > api_key.txt
streamlit run app.py

Then open http://localhost:8501 in your mobile browser.

---

## 📁 Project Structure

solo-dnd-multi/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── api_key.txt         # Your Gemini API key (not included)
├── saves/              # Autosave files (auto-created, not included)
└── README.md           # This file

---

## ⚠️ Important Notes

- api_key.txt is excluded from this repo — you must create your own
- Get a free API key at https://aistudio.google.com
- Save files are stored locally in the saves/ folder
- The app uses Gemini gemini-3.5-flash model
- This project uses the Google Gemini API but is not affiliated with, endorsed by, or connected to Google LLC in any way.
---

## 👤 Author

ParamGGX
Built from scratch using Termux.
GitHub: https://github.com/ParamGGX

For any problems, bugs, or errors with this project, feel free to contact the author at paramveersingh.super@gmail.com
---

## 📜 License

This project is licensed under a Creative Commons Attribution 4.0 International License.
You may use, share, or modify this project but must credit ParamGGX and link back to this repository.