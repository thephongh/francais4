import streamlit as st
import streamlit.components.v1 as components
import random
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO
import os

# Add custom JavaScript for animations
def load_custom_js():
    return """
    <script>
    // Function to add bounce animation to correct answers
    function addBounceAnimation(element) {
        element.style.animation = 'bounce 0.5s';
    }

    // Function to add shake animation to incorrect answers
    function addShakeAnimation(element) {
        element.style.animation = 'shake 0.5s';
    }

    // CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-30px);}
            60% {transform: translateY(-15px);}
        }
        @keyframes shake {
            0%, 100% {transform: translateX(0);}
            10%, 30%, 50%, 70%, 90% {transform: translateX(-5px);}
            20%, 40%, 60%, 80% {transform: translateX(5px);}
        }
        .correct {
            color: #4CAF50;
            font-weight: bold;
        }
        .incorrect {
            color: #f44336;
            font-weight: bold;
        }
        .card {
            transition: transform 0.3s;
            cursor: pointer;
        }
        .card:hover {
            transform: scale(1.05);
        }
    `;
    document.head.appendChild(style);
    </script>
    """

# Add card component for clothing items
def create_clothing_card(image_path, name):
    return f"""
    <div class="card" onclick="this.style.transform = 'scale(1.1)'; setTimeout(() => this.style.transform = 'scale(1)', 200)">
        <img src="{image_path}" style="width: 100%; border-radius: 10px;">
        <div style="text-align: center; padding: 10px; font-size: 1.2em;">{name}</div>
    </div>
    """

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'welcome'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'player_name' not in st.session_state:
    st.session_state.player_name = ''
if 'category' not in st.session_state:
    st.session_state.category = None
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = pd.DataFrame(columns=['Player', 'Score', 'Category', 'Date'])

# Create a directory for storing images if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Load custom JavaScript
st.markdown(load_custom_js(), unsafe_allow_html=True)

# French questions database organized by categories
questions = {
    'lexique': [
        {
            'type': 'listening',
            'question': 'Écoute et coche (✓) la bonne réponse.',
            'options': ['Le corps', 'Les cheveux', "L'apparence", 'Le caractère'],
            'correct': 'Le caractère',
            'points': 10,
            'grid': True,
            'grid_options': ['Le corps', 'Les cheveux', "L'apparence", 'Le caractère'],
            'audio': 'path_to_audio.mp3'  # You'll need to add audio files
        },
        {
            'type': 'image_match',
            'question': 'Observe les photos et complète.',
            'images': {
                '1': 'chemise_blanche.jpg',
                '2': 'pantalon_noir.jpg',
                '3': 'sac_rouge.jpg',
                '4': 'veste_grise.jpg',
                '5': 'tshirt_rouge.jpg',
                '6': 'chapeau_jaune.jpg',
                '7': 'robe_violette.jpg',
                '8': 'lunettes.jpg'
            },
            'crossword': {
                'word': 'CHEMISE',
                'hint': 'Horizontal: Un vêtement porté sur le haut du corps'
            },
            'points': 15
        }
    ],
    'word_formation': [
        {
            'question': 'Associe pour former des mots.',
            'word_parts': [
                {'start': 'fé', 'end': 'te', 'word': 'fête'},
                {'start': 'karao', 'end': 'ké', 'word': 'karaoké'},
                {'start': 'gar', 'end': 'çon', 'word': 'garçon'},
                {'start': 'chan', 'end': 'son', 'word': 'chanson'},
                {'start': 'co', 'end': 'pain', 'word': 'copain'},
                {'start': 'invita', 'end': 'tion', 'word': 'invitation'}
            ],
            'points': 10
        },
        {
            'question': "Ajoute l'article indéfini un ou une.",
            'items': [
                {'word': 'invi', 'end': 'té', 'article': 'un'},
                {'word': 'fê', 'end': 'te', 'article': 'une'},
                {'word': 'karao', 'end': 'ké', 'article': 'un'},
                {'word': 'chan', 'end': 'son', 'article': 'une'},
                {'word': 'co', 'end': 'pain', 'article': 'un'},
                {'word': 'invita', 'end': 'tion', 'article': 'une'}
            ],
            'points': 10
        }
    ],
    'grammaire': [
        {
            'question': "Souligne l'adjectif qui convient.",
            'sentences': [
                {
                    'text': 'Ton fils est très',
                    'options': ['beau', 'beaux', 'belle', 'belles'],
                    'correct': 'beau'
                },
                {
                    'text': 'Elle a les cheveux',
                    'options': ['court', 'courts', 'courte', 'courtes'],
                    'correct': 'courts'
                },
                {
                    'text': 'André Hossein porte une chemise',
                    'options': ['élégant', 'élégants', 'élégante', 'élégantes'],
                    'correct': 'élégante'
                },
                {
                    'text': 'Mes filles sont',
                    'options': ['sportif', 'sportifs', 'sportive', 'sportives'],
                    'correct': 'sportives'
                },
                {
                    'text': 'Kenza est une femme',
                    'options': ['sérieux', 'sérieuse', 'sérieuses'],
                    'correct': 'sérieuse'
                },
                {
                    'text': 'Vos lunettes sont',
                    'options': ['joli', 'jolis', 'jolie', 'jolies'],
                    'correct': 'jolies'
                }
            ],
            'points': 10
        },
        {
            'question': "Entoure l'article correct.",
            'items': [
                {'text': 'lunettes', 'options': ['un', 'une', 'des'], 'correct': 'des'},
                {'text': 'sacs', 'options': ['un', 'une', 'des'], 'correct': 'des'},
                {'text': 'veste', 'options': ['un', 'une', 'des'], 'correct': 'une'},
                {'text': 'tee-shirts', 'options': ['un', 'une', 'des'], 'correct': 'des'},
                {'text': 'amie', 'options': ['un', 'une', 'des'], 'correct': 'une'},
                {'text': 'chapeau', 'options': ['un', 'une', 'des'], 'correct': 'un'},
                {'text': 'chanson', 'options': ['un', 'une', 'des'], 'correct': 'une'},
                {'text': 'invités', 'options': ['un', 'une', 'des'], 'correct': 'des'},
                {'text': 'copain', 'options': ['un', 'une', 'des'], 'correct': 'un'},
                {'text': 'chemise', 'options': ['un', 'une', 'des'], 'correct': 'une'}
            ],
            'points': 10
        }
    ]
}

def display_welcome():
    st.title("🎮 Le Jeu de Français")
    st.markdown("""
    ### Bienvenue dans le Jeu de Français! 🇫🇷
    
    Testez vos connaissances en français avec différentes catégories d'exercices:
    - 📚 Lexique (vocabulaire, vêtements, apparence)
    - ✍️ Grammaire (adjectifs, articles)
    - 🔤 Formation des mots
    """)
    
    player_name = st.text_input("Entrez votre nom pour commencer:")
    
    if player_name:
        st.session_state.player_name = player_name
        st.subheader("Choisissez une catégorie:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📚 Lexique"):
                st.session_state.category = 'lexique'
                st.session_state.game_state = 'playing'
                st.rerun()
        with col2:
            if st.button("✍️ Grammaire"):
                st.session_state.category = 'grammaire'
                st.session_state.game_state = 'playing'
                st.rerun()
        with col3:
            if st.button("🔤 Formation des mots"):
                st.session_state.category = 'word_formation'
                st.session_state.game_state = 'playing'
                st.rerun()
    else:
        st.error("Veuillez entrer votre nom!")

def display_image_question(question):
    st.write(f"### {question['question']}")
    
    # Display images in a grid with interactive cards
    cols = st.columns(4)
    for idx, (img_num, img_path) in enumerate(question['images'].items()):
        with cols[idx % 4]:
            components.html(
                create_clothing_card(f"images/{img_path}", f"Image {img_num}"),
                height=350
            )
    
    # Display crossword hint
    st.write(f"**{question['crossword']['hint']}**")
    answer = st.text_input("Votre réponse:", key="crossword_answer")
    
    if st.button("Vérifier"):
        if answer.upper() == question['crossword']['word']:
            components.html(
                f'<div class="correct" id="result">Correct! +{question["points"]} points 🎉</div>',
                height=50
            )
            st.session_state.score += question['points']
        else:
            components.html(
                f'<div class="incorrect" id="result">Incorrect! La réponse correcte était: {question["crossword"]["word"]}</div>',
                height=50
            )
        
        time.sleep(1)
        st.session_state.current_question += 1
        st.rerun()

def display_word_formation(question):
    st.write(f"### {question['question']}")
    
    if 'word_parts' in question:
        for idx, part in enumerate(question['word_parts']):
            col1, col2, col3 = st.columns([2,1,2])
            with col1:
                st.write(part['start'])
            with col2:
                st.write("+")
            with col3:
                answer = st.selectbox(f"Choisissez la fin du mot {idx+1}", 
                                    ['', 'te', 'ké', 'çon', 'son', 'pain', 'tion'],
                                    key=f"word_part_{idx}")
    else:
        for idx, item in enumerate(question['items']):
            col1, col2 = st.columns(2)
            with col1:
                article = st.selectbox(f"Choisissez l'article pour '{item['word']}{item['end']}'",
                                     ['', 'un', 'une'],
                                     key=f"article_{idx}")
            with col2:
                st.write(f"{item['word']}{item['end']}")

def display_grammar_question(question):
    st.write(f"### {question['question']}")
    
    if 'sentences' in question:
        for idx, sentence in enumerate(question['sentences']):
            st.write(f"{sentence['text']}")
            answer = st.selectbox("Choisissez la forme correcte:", 
                                [''] + sentence['options'],
                                key=f"adj_{idx}")
    else:
        for idx, item in enumerate(question['items']):
            col1, col2 = st.columns(2)
            with col1:
                st.write(item['text'])
            with col2:
                answer = st.selectbox("Choisissez l'article:", 
                                    [''] + item['options'],
                                    key=f"art_{idx}")

def display_listening_question(question):
    st.write(f"### {question['question']}")
    
    # Create a grid for options
    if question.get('grid', False):
        # Create a table-like structure
        col1, col2, col3, col4 = st.columns(4)
        headers = [col1, col2, col3, col4]
        
        # Display headers
        for idx, header in enumerate(question['grid_options']):
            with headers[idx]:
                st.write(f"**{header}**")
        
        # Create checkboxes in a grid
        selected_option = None
        for idx, option in enumerate(question['options']):
            with headers[idx]:
                if st.checkbox("✓", key=f"check_{idx}"):
                    selected_option = option
        
        # Add verify button
        if st.button("Vérifier la réponse"):
            if selected_option == question['correct']:
                st.success(f"Correct! +{question['points']} points 🎉")
                st.session_state.score += question['points']
            else:
                st.error(f"Incorrect! La réponse correcte était: {question['correct']}")
            
            time.sleep(1)
            st.session_state.current_question += 1
            st.rerun()

def display_question():
    category_questions = questions[st.session_state.category]
    current_q = category_questions[st.session_state.current_question % len(category_questions)]
    
    # Display progress
    progress = (st.session_state.current_question % len(category_questions)) / len(category_questions)
    st.progress(progress)
    
    # Display category and score
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📝 {st.session_state.category.title()}")
    with col2:
        st.subheader(f"🎯 Score: {st.session_state.score}")
    
    # Display question based on type
    if st.session_state.category == 'lexique':
        if current_q['type'] == 'image_match':
            display_image_question(current_q)
        else:
            display_listening_question(current_q)
    elif st.session_state.category == 'word_formation':
        display_word_formation(current_q)
    else:
        display_grammar_question(current_q)

# Add confetti effect for high scores
def show_confetti():
    return """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.4.0/dist/confetti.browser.min.js"></script>
    <script>
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
    });
    </script>
    """

def display_game_over():
    st.title("🎮 Fin du Jeu!")
    
    # Update leaderboard
    new_score = pd.DataFrame({
        'Player': [st.session_state.player_name],
        'Score': [st.session_state.score],
        'Category': [st.session_state.category],
        'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_score], ignore_index=True)
    
    # Show confetti for high scores
    if st.session_state.score >= 50:
        components.html(show_confetti(), height=100)
    
    st.write(f"### Score final: {st.session_state.score} points")
    
    # Display category-specific leaderboard with enhanced styling
    st.subheader(f"🏆 Classement - {st.session_state.category.title()}")
    category_scores = st.session_state.leaderboard[
        st.session_state.leaderboard['Category'] == st.session_state.category
    ]
    fig = px.bar(
        category_scores.sort_values('Score', ascending=False).head(5),
        x='Player',
        y='Score',
        title=f'Top 5 - {st.session_state.category.title()}'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'size': 14}
    )
    st.plotly_chart(fig)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Rejouer même catégorie"):
            st.session_state.score = 0
            st.session_state.current_question = 0
            st.session_state.game_state = 'playing'
            st.rerun()
    with col2:
        if st.button("🏠 Retour à l'accueil"):
            st.session_state.game_state = 'welcome'
            st.session_state.score = 0
            st.session_state.current_question = 0
            st.session_state.category = None
            st.rerun()

# Main game loop
if st.session_state.game_state == 'welcome':
    display_welcome()
elif st.session_state.game_state == 'playing':
    display_question()
elif st.session_state.game_state == 'game_over':
    display_game_over()

# Add custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        margin: 5px 0;
        padding: 10px;
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .css-1d391kg {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)
