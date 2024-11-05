from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np

class RelevancyScorer:
    def __init__(self):
        # Lightweight model for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    @lru_cache(maxsize=1000)  
    def get_embedding(self, text):
        """Cache embeddings for texts"""
        return tuple(self.model.encode(text))  
    
    def calculate_batch_relevance_scores(self, skills_and_descriptions):
        """
        Calculate relevancy scores for multiple skill-description pairs at once
        with cached embeddings
        """
        if not skills_and_descriptions:
            return []

        skills, descriptions = zip(*skills_and_descriptions)
        
        try:
            skill_embeddings = [np.array(self.get_embedding(skill)) for skill in skills]
            desc_embeddings = [np.array(self.get_embedding(desc)) for desc in descriptions]
            
            scores = []
            for i in range(len(skills)):
                similarity = np.dot(skill_embeddings[i], desc_embeddings[i]) / (
                    np.linalg.norm(skill_embeddings[i]) * np.linalg.norm(desc_embeddings[i])
                )
                # Normalize to [0,1] range
                normalized_score = round(float((similarity + 1) / 2), 3)
                scores.append(normalized_score)
            
            return scores
            
        except Exception as e:
            print(f"Error calculating batch scores: {e}")
            return [0.0] * len(skills_and_descriptions)