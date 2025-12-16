# backend/utils/quiz_maker.py
import random
import re
from typing import List
import nltk

# Ensure required NLTK data is available; try to download if missing:
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except:
    nltk.download("averaged_perceptron_tagger")
from nltk import sent_tokenize, word_tokenize, pos_tag

def _extract_candidate(sent):
    toks = word_tokenize(sent)
    tags = pos_tag(toks)
    # pick first proper noun (NNP) or numeric (CD) or noun (NN)
    for w, t in tags:
        if t in ("NNP", "NNPS", "CD", "NN"):
            # avoid very short tokens or punctuation
            if re.match(r"^[A-Za-z0-9\-\']+$", w) and len(w) > 2:
                return w
    return None

def generate_quiz_from_text(text: str, num_questions: int = 5):
    sents = sent_tokenize(text)
    candidates = []
    for s in sents:
        c = _extract_candidate(s)
        if c:
            candidates.append((s, c))
    random.shuffle(candidates)
    quiz = []
    used_answers = set()
    i = 0
    for sent, answer in candidates:
        if len(quiz) >= num_questions:
            break
        if answer.lower() in used_answers:
            continue
        # build options: correct + 3 distractors
        distractors = []
        # gather noun pool
        pool = set()
        for s2 in sents:
            toks2 = word_tokenize(s2)
            for w, t in pos_tag(toks2):
                if t.startswith("NN") or t == "CD":
                    if re.match(r"^[A-Za-z0-9\-\']+$", w) and len(w) > 2:
                        pool.add(w)
        pool.discard(answer)
        pool = list(pool)
        random.shuffle(pool)
        for p in pool:
            if len(distractors) >= 3:
                break
            if p.lower() != answer.lower():
                distractors.append(p)
        if len(distractors) < 3:
            # fallback: generate simple numeric distractors if answer numeric
            while len(distractors) < 3:
                distractors.append(answer + str(random.randint(1,9)))
        options = [answer] + distractors[:3]
        random.shuffle(options)
        ans_index = options.index(answer)
        # question: replace answer in sentence with blank
        q_text = re.sub(re.escape(answer), "_____", sent, flags=re.IGNORECASE)
        quiz.append({"question": q_text, "options": options, "answer_index": ans_index})
        used_answers.add(answer.lower())
    # If insufficient items, fall back to simple sentence truncation questions
    if len(quiz) < num_questions:
        for s in sents:
            if len(quiz) >= num_questions:
                break
            words = s.split()
            if len(words) > 8:
                answer = words[min(2, len(words)-1)]
                options = [answer, answer + "X", answer + "Y", answer + "Z"]
                random.shuffle(options)
                quiz.append({"question": "Complete: " + " ".join(words[:6]) + " ...", "options": options, "answer_index": options.index(answer)})
    return quiz[:num_questions]
