from sentence_transformers import SentenceTransformer
import numpy as np

class RelevancyScorer:
    def __init__(self):
        # lightweight model for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def calculate_relevance_score(self, skill, module_description):
        """Calculate semantic similarity between skill and module description"""
        if not skill or not module_description:
            return 0.0
        
        try:
            # Get embeddings
            skill_embedding = self.model.encode(skill)
            desc_embedding = self.model.encode(module_description)
            
            # Calculate cosine similarity
            similarity = np.dot(skill_embedding, desc_embedding) / (
                np.linalg.norm(skill_embedding) * np.linalg.norm(desc_embedding)
            )
            
            # Normalize to [0,1] range
            normalized_score = round(float((similarity + 1) / 2), 3)
            return normalized_score
            
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 0.0